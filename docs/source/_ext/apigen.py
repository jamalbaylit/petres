"""Automatic API reference generator for Sphinx.

Discovers public API via __all__ recursion, detects aliases,
categorizes objects, and generates complete .rst documentation.

Canonical Selection Priority:
1) Prefer the MOST EXPLICIT (deeper) import path
   e.g., petromod.grids.Rectilinear2DGrid over petromod.Rectilinear2DGrid
2) If depth is equal, prefer the longest descriptive name
3) Final fallback: stable alphabetical order
"""

import importlib
import inspect
import pkgutil
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


class APIGenerator:
    """Generates complete API reference documentation automatically."""

    def __init__(self, app):
        self.app = app
        self.source_dir = Path(app.srcdir)
        self.api_dir = self.source_dir / "api"
        
        # Get package name from config or default to 'petromod'
        self.package_name = getattr(app.config, 'api_package_name', 'petromod')
        
        # Storage for discovered objects
        self.objects = {}  # canonical_name -> object_info
        self.aliases = defaultdict(list)  # canonical_name -> [alias_names]
        self.categories = defaultdict(list)  # category -> [canonical_names]
        
        # Track all names for each object during discovery
        self.object_names = defaultdict(list)  # obj_id -> [all_export_names]
        
    def generate(self):
        """Main generation entry point."""
        from sphinx.util import logging
        logger = logging.getLogger(__name__)
        
        logger.info("[apigen] Starting automatic API reference generation")
        
        # Clean and recreate api directory
        if self.api_dir.exists():
            shutil.rmtree(self.api_dir)
        self.api_dir.mkdir(parents=True)
        
        # Discover public API
        self._discover_api()
        
        if not self.objects:
            logger.warning("[apigen] No public objects found in __all__")
            return
        
        # Generate all .rst files
        self._generate_index()
        self._generate_category_pages()
        self._generate_object_pages()
        
        logger.info(f"[apigen] Generated docs for {len(self.objects)} objects "
                     f"in {len(self.categories)} categories")
    
    def _discover_api(self):
        """Discover all public API objects via __all__ recursion.
        
        Discovers ALL objects from ANY __init__.py's __all__, regardless of
        whether they are re-exported at the top level.
        """
        from sphinx.util import logging
        logger = logging.getLogger(__name__)
        
        try:
            package = importlib.import_module(self.package_name)
        except ImportError as e:
            logger.warning(f"[apigen] Could not import {self.package_name}: {e}")
            return
        
        # Discover from ALL subpackages and their __all__ declarations
        # This is the primary discovery mechanism - we find everything,
        # not just what's re-exported at the top level
        self._discover_all_subpackages(package, self.package_name)
        
        # Second pass: select canonical names and categorize
        self._select_canonical_names()
        
        # Sort categories and objects deterministically
        for category in self.categories:
            self.categories[category].sort()
    
    def _discover_all_subpackages(self, package, parent_path: str):
        """Recursively discover ALL subpackages and their __all__ exports.
        
        This discovers objects from every __init__.py's __all__, regardless
        of whether they're re-exported at higher levels.
        """
        from sphinx.util import logging
        logger = logging.getLogger(__name__)
        
        # First, discover from this package's __all__
        self._discover_module(package, parent_path)
        
        # Then recursively discover from all subpackages
        if not hasattr(package, '__path__'):
            return
        
        try:
            for importer, modname, ispkg in pkgutil.iter_modules(package.__path__):
                if ispkg:
                    full_name = f"{parent_path}.{modname}"
                    try:
                        subpackage = importlib.import_module(full_name)
                        # Recursively discover from this subpackage
                        self._discover_all_subpackages(subpackage, full_name)
                    except Exception as e:
                        # Log import failures for debugging
                        logger.warning(f"[apigen] Failed to import {full_name}: {e}")
        except Exception as e:
            # Log iteration failures for debugging
            logger.warning(f"[apigen] Error iterating subpackages of {parent_path}: {e}")
    
    def _select_canonical_names(self):
        """Select canonical name for each object using priority rules.
        
        Priority:
        1) Prefer deeper (more explicit) paths
        2) If equal depth, prefer longer names
        3) Final fallback: alphabetical order
        """
        for obj_id, export_names in self.object_names.items():
            if not export_names:
                continue
            
            # Sort by priority: depth (descending), length (descending), alphabetical
            def priority_key(name):
                depth = name.count('.')
                return (-depth, -len(name), name)
            
            sorted_names = sorted(export_names, key=priority_key)
            canonical_name = sorted_names[0]
            alias_names = sorted_names[1:]
            
            # Get the object info from temp storage
            if not hasattr(self, '_temp_objects') or canonical_name not in self._temp_objects:
                continue
            
            obj_info = self._temp_objects[canonical_name]
            
            # Update the name in obj_info to match canonical
            obj_info['full_name'] = canonical_name
            obj_info['name'] = canonical_name.split('.')[-1]
            
            # Store canonical object
            self.objects[canonical_name] = obj_info
            
            # Store aliases
            if alias_names:
                self.aliases[canonical_name] = alias_names
            
            # Categorize based on the CANONICAL EXPORT PATH, not where it's defined
            category = self._extract_category(canonical_name)
            self.categories[category].append(canonical_name)
    
    def _discover_module(self, module, parent_path: str):
        """Recursively discover objects from a module's __all__."""
        from sphinx.util import logging
        logger = logging.getLogger(__name__)
        
        if not hasattr(module, '__all__'):
            return
        
        # Initialize temp storage on first call
        if not hasattr(self, '_temp_objects'):
            self._temp_objects = {}
        
        for name in module.__all__:
            try:
                obj = getattr(module, name)
                full_name = f"{parent_path}.{name}"
                
                # Get object identity
                obj_id = id(obj)
                
                # Determine object type
                if inspect.isclass(obj):
                    obj_type = 'class'
                elif inspect.isfunction(obj):
                    obj_type = 'function'
                elif inspect.ismodule(obj):
                    # Recurse into submodules
                    self._discover_module(obj, full_name)
                    continue
                else:
                    # Skip other types (constants, etc.)
                    continue
                
                # Store object info temporarily
                obj_info = {
                    'name': name,
                    'full_name': full_name,
                    'type': obj_type,
                    'obj': obj,
                    'import_path': parent_path,
                    'module': obj.__module__,  # Track where object is defined
                }
                self._temp_objects[full_name] = obj_info
                
                # Track this name for this object
                self.object_names[obj_id].append(full_name)
                
            except (AttributeError, ImportError) as e:
                logger.warning(f"[apigen] Could not import {parent_path}.{name}: {e}")
    
    def _extract_category(self, import_path: str) -> str:
        """Extract category from canonical export path.
        
        Supports nested categories by preserving the namespace hierarchy
        from the canonical export path. For example:
        - petromod.grids.Rectilinear2DGrid → "Grids"
        - petromod.interpolators.spatial.InverseDistanceWeightingInterpolator → "Interpolators / Spatial"
        - petromod.interpolators.NearestNeighborInterpolator → "Interpolators"
        """
        # Remove package name prefix
        path_parts = import_path.split('.')
        if path_parts[0] == self.package_name:
            path_parts = path_parts[1:]
        
        if not path_parts:
            return "Core"
        
        # Build nested category path from the export namespace
        # Remove the final object name
        category_parts = path_parts[:-1] if len(path_parts) > 1 else []
        
        if not category_parts:
            return "Core"
        
        # Convert each part to title case and join with " / "
        category_titles = [self._make_title(part) for part in category_parts]
        return " / ".join(category_titles)
    
    def _make_title(self, text: str) -> str:
        """Convert snake_case or module name to Title Case."""
        # Replace underscores with spaces
        text = text.replace('_', ' ')
        # Title case
        return text.title()
    
    def _generate_index(self):
        """Generate main API Reference index page."""
        from sphinx.util import logging
        logger = logging.getLogger(__name__)
        
        lines = [
            "API Reference",
            "=" * 80,
            "",
            "Complete reference for all public classes and functions.",
            "",
        ]
        
        # Build hierarchical category tree
        category_tree = self._build_category_tree()
        
        # Generate toctree with hierarchy
        lines.extend(self._generate_toctree_from_tree(category_tree))
        
        lines.append("")
        
        index_file = self.api_dir / "index.rst"
        index_file.write_text("\n".join(lines), encoding='utf-8')
        logger.info(f"[apigen] Generated {index_file}")
    
    def _build_category_tree(self):
        """Build hierarchical category tree from flat category list."""
        tree = {}
        for category in sorted(self.categories.keys()):
            parts = category.split(" / ")
            current = tree
            for part in parts:
                if part not in current:
                    current[part] = {}
                current = current[part]
            # Mark leaf nodes with the full category path
            current['__category__'] = category
        return tree
    
    def _generate_toctree_from_tree(self, tree, level=0):
        """Generate toctree entries from hierarchical tree."""
        lines = []
        
        if level == 0:
            lines.append(".. toctree::")
            lines.append("   :maxdepth: 2")
            lines.append("   :caption: Categories")
            lines.append("")
        
        for key in sorted(tree.keys()):
            if key == '__category__':
                continue
            
            subtree = tree[key]
            category_slug = self._slugify(subtree.get('__category__', key))
            
            indent = "   " * (level + 1)
            lines.append(f"{indent}{category_slug}")
            
            # If this has subcategories, we don't recurse here
            # Each category page will have its own toctree
        
        return lines
    
    def _generate_category_pages(self):
        """Generate one page per category, supporting nested categories."""
        from sphinx.util import logging
        logger = logging.getLogger(__name__)
        
        # Collect all categories that need pages (including parents without objects)
        all_category_paths = set()
        for category in self.categories.keys():
            # Add this category
            all_category_paths.add(category)
            # Add all parent categories
            parts = category.split(" / ")
            for i in range(1, len(parts)):
                parent = " / ".join(parts[:i])
                all_category_paths.add(parent)
        
        # Generate pages for all categories
        for category in sorted(all_category_paths):
            category_slug = self._slugify(category)
            object_names = self.categories.get(category, [])
            
            # Determine if this is a leaf category (has objects)
            # or a parent category (has subcategories)
            parts = category.split(" / ")
            category_title = parts[-1] if parts else category
            
            lines = [
                category_title,
                "=" * 80,
                "",
            ]
            
            # Check for subcategories
            subcategories = self._get_subcategories(category)
            
            if subcategories:
                # This category has subcategories
                if object_names:
                    lines.append(f"Public API for {category_title.lower()}.")
                else:
                    lines.append(f"Subcategories of {category_title.lower()}.")
                lines.append("")
                lines.append(".. toctree::")
                lines.append("   :maxdepth: 1")
                lines.append("")
                
                for subcat in sorted(subcategories):
                    subcat_slug = self._slugify(subcat)
                    subcat_name = subcat.split(" / ")[-1]
                    lines.append(f"   {subcat_name} <{subcat_slug}>")
                
                lines.append("")
            
            if object_names:
                # This category has objects
                if subcategories:
                    lines.append("Objects")
                    lines.append("-" * 40)
                    lines.append("")
                else:
                    lines.append(f"Public API for {category_title.lower()}.")
                    lines.append("")
                
                lines.append(".. toctree::")
                lines.append("   :maxdepth: 1")
                lines.append("")
                
                # Add objects in this category
                for full_name in object_names:
                    obj_slug = self._slugify(full_name)
                    obj_info = self.objects[full_name]
                    lines.append(f"   {obj_info['name']} <{obj_slug}>")
                
                lines.append("")
            
            category_file = self.api_dir / f"{category_slug}.rst"
            category_file.write_text("\n".join(lines), encoding='utf-8')
            logger.info(f"[apigen] Generated {category_file}")
    
    def _get_subcategories(self, parent_category: str) -> list:
        """Get all subcategories of a given category."""
        subcats = []
        prefix = parent_category + " / "
        for category in self.categories.keys():
            if category.startswith(prefix):
                # Check if this is a direct child (not a grandchild)
                remaining = category[len(prefix):]
                if " / " not in remaining:
                    subcats.append(category)
        return subcats
    
    def _generate_object_pages(self):
        """Generate one page per canonical object."""
        for full_name, obj_info in self.objects.items():
            obj_slug = self._slugify(full_name)
            obj_name = obj_info['name']
            obj_type = obj_info['type']
            
            lines = [
                obj_name,
                "=" * 80,
                "",
            ]
            
            # Add aliases section if present
            if full_name in self.aliases and self.aliases[full_name]:
                alias_list = self.aliases[full_name]
                lines.append("**Aliases:**")
                lines.append("")
                for alias in alias_list:
                    # Extract just the final name component
                    alias_name = alias.split('.')[-1]
                    lines.append(f"- ``{alias}``")
                lines.append("")
                lines.append("----")
                lines.append("")
            
            # Add autodoc directive
            if obj_type == 'class':
                lines.extend([
                    f".. autoclass:: {full_name}",
                    "   :members:",
                    "   :undoc-members:",
                    "   :show-inheritance:",
                    "   :special-members: __init__",
                    "   :exclude-members: __weakref__",
                ])
            elif obj_type == 'function':
                lines.extend([
                    f".. autofunction:: {full_name}",
                ])
            
            lines.append("")
            
            obj_file = self.api_dir / f"{obj_slug}.rst"
            obj_file.write_text("\n".join(lines), encoding='utf-8')
    
    def _slugify(self, text: str) -> str:
        """Convert text to valid filename slug."""
        # Replace dots and spaces with hyphens
        slug = text.lower().replace('.', '-').replace(' ', '-')
        # Remove any other non-alphanumeric characters except hyphens
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        return slug


def generate_api_docs(app):
    """Sphinx event handler for builder-inited."""
    generator = APIGenerator(app)
    generator.generate()


def setup(app):
    """Sphinx extension setup."""
    # Add config value for package name
    app.add_config_value('api_package_name', 'petromod', 'html')
    
    # Connect to builder-inited event
    app.connect('builder-inited', generate_api_docs)
    
    return {
        'version': '1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
