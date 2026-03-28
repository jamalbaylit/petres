from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
import re
import shutil

import yaml
from sphinx.application import Sphinx
from sphinx.util import logging


logger = logging.getLogger(__name__)

ALLOWED_DIFFICULTIES = {"beginner", "intermediate", "advanced"}
ALLOWED_LOCATIONS = {"getting_started", "tutorials", "examples"}


@dataclass(frozen=True)
class ExampleBlock:
    path: str
    title: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class Section:
    title: str
    description: str | None = None
    examples: tuple[ExampleBlock, ...] = ()


@dataclass(frozen=True)
class Page:
    slug: str
    title: str
    location: str
    summary: str | None = None
    description: str | None = None
    difficulty: str | None = None
    sections: tuple[Section, ...] = ()
    tags: tuple[str, ...] = ()


@dataclass(frozen=True)
class NavLink:
    title: str
    docname: str


def _source_dir(app: Sphinx) -> Path:
    return Path(app.confdir).resolve()


def _docs_dir(app: Sphinx) -> Path:
    return _source_dir(app).parent


def _project_root(app: Sphinx) -> Path:
    return _docs_dir(app).parent


def _generated_dir(app: Sphinx) -> Path:
    return _source_dir(app) / "_generated"


def _generated_getting_started_dir(app: Sphinx) -> Path:
    return _generated_dir(app) / "getting_started"


def _generated_tutorials_dir(app: Sphinx) -> Path:
    return _generated_dir(app) / "tutorials"


def _generated_examples_dir(app: Sphinx) -> Path:
    return _generated_dir(app) / "examples"


def _config_path(app: Sphinx) -> Path:
    config_value = app.config.example_docs_config
    path = Path(config_value)
    if not path.is_absolute():
        path = _source_dir(app) / path
    return path.resolve()


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "page"


def _title_from_path(path_str: str) -> str:
    return Path(path_str).stem.replace("_", " ").strip().title()


def _landing_filename(location: str) -> str:
    if location == "getting_started":
        return "getting_started.rst"
    if location == "tutorials":
        return "tutorials.rst"
    if location == "examples":
        return "examples.rst"
    raise ValueError(f"Unsupported location: {location!r}")


def _generated_subdir_for_location(app: Sphinx, location: str) -> Path:
    if location == "getting_started":
        return _generated_getting_started_dir(app)
    if location == "tutorials":
        return _generated_tutorials_dir(app)
    if location == "examples":
        return _generated_examples_dir(app)
    raise ValueError(f"Unsupported location: {location!r}")


def _docname_for_page(location: str, slug: str) -> str:
    return f"_generated/{location}/{slug}"


def _resolve_example_file(app: Sphinx, path_str: str) -> Path:
    """
    Resolve example file paths.

    Expected config paths are usually project-root relative, for example:
        examples/getting_started.py
        examples/property_modeling/apply.py

    As a fallback, docs-relative paths are also supported.
    """
    path = Path(path_str)

    if path.is_absolute():
        return path

    candidates = [
        _project_root(app) / path,
        _docs_dir(app) / path,
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    return candidates[0].resolve()


def _read_code(app: Sphinx, path_str: str) -> str:
    file_path = _resolve_example_file(app, path_str)
    if not file_path.exists():
        raise FileNotFoundError(f"Configured example file does not exist: {file_path}")
    return file_path.read_text(encoding="utf-8")


def _load_config(app: Sphinx) -> dict[str, Any]:
    path = _config_path(app)

    if not path.exists():
        raise FileNotFoundError(f"Example docs config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError(f"Root of example docs config must be a mapping: {path}")

    return data


def _clean_generated(app: Sphinx) -> None:
    shutil.rmtree(_generated_dir(app), ignore_errors=True)

    _generated_getting_started_dir(app).mkdir(parents=True, exist_ok=True)
    _generated_tutorials_dir(app).mkdir(parents=True, exist_ok=True)
    _generated_examples_dir(app).mkdir(parents=True, exist_ok=True)

    for filename in ("getting_started.rst", "tutorials.rst", "examples.rst"):
        (_source_dir(app) / filename).unlink(missing_ok=True)


def _validate_difficulty(value: str | None) -> None:
    if value is None:
        return
    if value not in ALLOWED_DIFFICULTIES:
        raise ValueError(
            f"Invalid difficulty {value!r}. Allowed values: "
            f"{sorted(ALLOWED_DIFFICULTIES)}."
        )


def _validate_location(value: str) -> None:
    if value not in ALLOWED_LOCATIONS:
        raise ValueError(
            f"Invalid location {value!r}. Allowed values: "
            f"{sorted(ALLOWED_LOCATIONS)}."
        )


def _parse_example_block(item: dict[str, Any]) -> ExampleBlock:
    if not isinstance(item, dict):
        raise ValueError("Each example block must be a mapping.")
    if "path" not in item:
        raise ValueError("Each example block must include a 'path' field.")

    path = item["path"]
    title = item.get("title")
    description = item.get("description")

    if not isinstance(path, str) or not path.strip():
        raise ValueError("Each example block 'path' must be a non-empty string.")
    if title is not None and not isinstance(title, str):
        raise ValueError(f"Invalid example block title for path {path!r}.")
    if description is not None and not isinstance(description, str):
        raise ValueError(f"Invalid example block description for path {path!r}.")

    return ExampleBlock(
        path=path.strip(),
        title=title.strip() if isinstance(title, str) else None,
        description=description.strip() if isinstance(description, str) else None,
    )


def _parse_section(item: dict[str, Any]) -> Section:
    if not isinstance(item, dict):
        raise ValueError("Each section must be a mapping.")
    if "title" not in item:
        raise ValueError("Each section must include a 'title' field.")

    title = item["title"]
    description = item.get("description")
    examples_raw = item.get("examples", [])

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Each section title must be a non-empty string.")
    if description is not None and not isinstance(description, str):
        raise ValueError(f"Invalid section description for section {title!r}.")
    if not isinstance(examples_raw, list):
        raise ValueError(f"'examples' must be a list in section {title!r}.")
    if not examples_raw:
        raise ValueError(f"Section {title!r} must contain at least one example block.")

    examples = tuple(_parse_example_block(example_item) for example_item in examples_raw)

    return Section(
        title=title.strip(),
        description=description.strip() if isinstance(description, str) else None,
        examples=examples,
    )


def _parse_page(item: dict[str, Any]) -> Page:
    if not isinstance(item, dict):
        raise ValueError("Each page must be a mapping.")

    required = ("slug", "title", "location", "sections")
    for field_name in required:
        if field_name not in item:
            raise ValueError(f"Each page must include a '{field_name}' field.")

    slug = item["slug"]
    title = item["title"]
    location = item["location"]
    summary = item.get("summary")
    description = item.get("description")
    difficulty = item.get("difficulty")
    tags_raw = item.get("tags", [])
    sections_raw = item["sections"]

    if not isinstance(slug, str) or not slug.strip():
        raise ValueError("Each page slug must be a non-empty string.")
    if not isinstance(title, str) or not title.strip():
        raise ValueError(f"Invalid title for page slug {slug!r}.")
    if not isinstance(location, str) or not location.strip():
        raise ValueError(f"Invalid location for page slug {slug!r}.")
    if summary is not None and not isinstance(summary, str):
        raise ValueError(f"Invalid summary for page slug {slug!r}.")
    if description is not None and not isinstance(description, str):
        raise ValueError(f"Invalid description for page slug {slug!r}.")
    if not isinstance(tags_raw, list):
        raise ValueError(f"Invalid tags for page slug {slug!r}; expected a list.")
    if not isinstance(sections_raw, list):
        raise ValueError(f"'sections' must be a list for page slug {slug!r}.")
    if not sections_raw:
        raise ValueError(f"Page {slug!r} must contain at least one section.")

    slug = _slugify(slug)
    location = location.strip()
    _validate_location(location)
    _validate_difficulty(difficulty)

    sections = tuple(_parse_section(section_item) for section_item in sections_raw)
    tags = tuple(str(tag).strip() for tag in tags_raw if str(tag).strip())

    return Page(
        slug=slug,
        title=title.strip(),
        location=location,
        summary=summary.strip() if isinstance(summary, str) else None,
        description=description.strip() if isinstance(description, str) else None,
        difficulty=difficulty,
        sections=sections,
        tags=tags,
    )


def _collect_pages(config: dict[str, Any]) -> list[Page]:
    pages_raw = config.get("pages", [])
    if not isinstance(pages_raw, list):
        raise ValueError("'pages' must be a list.")

    pages = [_parse_page(item) for item in pages_raw]

    seen_slugs: dict[str, int] = {}
    for page in pages:
        seen_slugs[page.slug] = seen_slugs.get(page.slug, 0) + 1

    duplicate_slugs = sorted(slug for slug, count in seen_slugs.items() if count > 1)
    if duplicate_slugs:
        raise ValueError(f"Duplicate page slugs found: {', '.join(duplicate_slugs)}")

    return pages


def _ensure_example_files_exist(app: Sphinx, pages: list[Page]) -> None:
    missing: list[str] = []

    for page in pages:
        for section in page.sections:
            for example in section.examples:
                file_path = _resolve_example_file(app, example.path)
                if not file_path.exists():
                    missing.append(f"{example.path} -> {file_path}")

    if missing:
        joined = "\n".join(f"  - {item}" for item in missing)
        raise FileNotFoundError(
            f"Missing example files referenced in example docs config:\n{joined}"
        )


def _assert_unique_example_paths_within_page(page: Page) -> None:
    seen: dict[str, int] = {}
    for section in page.sections:
        for example in section.examples:
            seen[example.path] = seen.get(example.path, 0) + 1

    duplicates = sorted(path for path, count in seen.items() if count > 1)
    if duplicates:
        raise ValueError(
            f"Duplicate example paths found within page {page.slug!r}: "
            f"{', '.join(duplicates)}"
        )


def _write_page(
    output_path: Path,
    *,
    page: Page,
    app: Sphinx,
    show_source: bool = False,
    previous: NavLink | None = None,
    next_: NavLink | None = None,
) -> None:
    title = page.title
    underline = "=" * len(title)

    lines: list[str] = [
        title,
        underline,
        "",
    ]

    if page.summary:
        lines.extend([page.summary, ""])

    meta_lines: list[str] = []
    if page.difficulty:
        meta_lines.append(f"**Difficulty:** {page.difficulty}")
    if page.tags:
        meta_lines.append(f"**Tags:** {', '.join(page.tags)}")

    if meta_lines:
        lines.extend(meta_lines)
        lines.append("")

    if page.description:
        lines.extend([page.description, ""])

    # if previous or next_:
    #     lines.extend(
    #         [
    #             "Navigation",
    #             "----------",
    #             "",
    #         ]
    #     )
    #     if previous:
    #         lines.append(f"**Previous:** :doc:`{previous.title} <{previous.docname}>`")
    #     if next_:
    #         lines.append(f"**Next:** :doc:`{next_.title} <{next_.docname}>`")
    #     lines.append("")

    for section in page.sections:
        section_underline = "-" * len(section.title)
        lines.extend(
            [
                section.title,
                section_underline,
                "",
            ]
        )

        if section.description:
            lines.extend([section.description, ""])

        for idx, example in enumerate(section.examples, start=1):
            example_title = example.title or _title_from_path(example.path)

            # When there are multiple example blocks in one section,
            # use a sub-sub-heading for readability.
            if len(section.examples) > 1 or example.title or example.description:
                example_underline = "^" * len(example_title)
                lines.extend(
                    [
                        example_title,
                        example_underline,
                        "",
                    ]
                )

            if show_source:
                lines.append(f"**Source:** ``{example.path}``")
                lines.append("")

            if example.description:
                lines.extend([example.description, ""])

            lines.extend(
                [
                    ".. code-block:: python",
                    "",
                ]
            )

            code = _read_code(app, example.path)
            for line in code.splitlines():
                lines.append(f"   {line}")
            lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _write_landing_page(
    output_path: Path,
    *,
    title: str,
    intro: str,
    docnames: list[str],
    maxdepth: int,
) -> None:
    underline = "=" * len(title)
    lines: list[str] = [
        title,
        underline,
        "",
        intro,
        "",
        ".. toctree::",
        f"   :maxdepth: {maxdepth}",
        "",
    ]

    for docname in docnames:
        lines.append(f"   {docname}")

    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _group_pages_by_location(pages: list[Page]) -> dict[str, list[Page]]:
    grouped = {location: [] for location in ALLOWED_LOCATIONS}
    for page in pages:
        grouped[page.location].append(page)
    return grouped


def _build_pages_for_location(
    app: Sphinx,
    pages: list[Page],
    *,
    location: str,
) -> list[str]:
    out_dir = _generated_subdir_for_location(app, location)
    docnames: list[str] = []

    for i, page in enumerate(pages):
        previous = None
        next_ = None

        if i > 0:
            prev_page = pages[i - 1]
            previous = NavLink(
                title=prev_page.title,
                docname=_docname_for_page(prev_page.location, prev_page.slug),
            )

        if i < len(pages) - 1:
            next_page = pages[i + 1]
            next_ = NavLink(
                title=next_page.title,
                docname=_docname_for_page(next_page.location, next_page.slug),
            )

        output_path = out_dir / f"{page.slug}.rst"
        _write_page(
            output_path,
            page=page,
            app=app,
            previous=previous,
            next_=next_,
        )

        docnames.append(_docname_for_page(location, page.slug))

    return docnames


def _write_location_landing_pages(app: Sphinx, grouped_pages: dict[str, list[Page]]) -> None:
    landing_specs = {
        # "getting_started": {
        #     "title": "Getting Started",
        #     "intro": (
        #         "Start here if you are new to Petres. These guides introduce the "
        #         "core workflow and the most common first steps."
        #     ),
        #     "maxdepth": 1,
        # },
        "tutorials": {
            "title": "Tutorials",
            "intro": "Task-oriented walkthroughs for common Petres workflows.",
            "maxdepth": 2,
        },
        "examples": {
            "title": "Examples",
            "intro": "Focused examples and reference-style usage patterns.",
            "maxdepth": 2,
        },
    }

    for location, spec in landing_specs.items():
        pages = grouped_pages[location]
        docnames = [_docname_for_page(location, page.slug) for page in pages]
        _write_landing_page(
            _source_dir(app) / _landing_filename(location),
            title=spec["title"],
            intro=spec["intro"],
            docnames=docnames,
            maxdepth=spec["maxdepth"],
        )


def generate_example_docs(app: Sphinx) -> None:
    logger.info("[exampledocs] Generating example documentation...")

    config = _load_config(app)
    pages = _collect_pages(config)

    for page in pages:
        _assert_unique_example_paths_within_page(page)

    _ensure_example_files_exist(app, pages)
    _clean_generated(app)

    grouped = _group_pages_by_location(pages)

    for location in ("getting_started", "tutorials", "examples"):
        _build_pages_for_location(app, grouped[location], location=location)

    _write_location_landing_pages(app, grouped)

    logger.info("[exampledocs] Example documentation generated successfully.")


def setup(app: Sphinx) -> dict[str, Any]:
    app.add_config_value(
        name="example_docs_config",
        default="_config/examples.yml",
        rebuild="env",
        types=(str,),
    )
    app.connect("builder-inited", generate_example_docs)

    return {
        "version": "3.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }