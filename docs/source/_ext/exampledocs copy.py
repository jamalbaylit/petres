from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import re
import shutil

import yaml
from sphinx.application import Sphinx
from sphinx.util import logging


logger = logging.getLogger(__name__)

ALLOWED_DIFFICULTIES = {"beginner", "intermediate", "advanced"}


@dataclass(frozen=True)
class ExampleEntry:
    path: str
    title: str
    summary: str | None = None
    description: str | None = None
    difficulty: str | None = None
    tags: tuple[str, ...] = ()
    section: str | None = None


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


def _examples_dir(app: Sphinx) -> Path:
    return _docs_dir(app) / "examples"


def _generated_dir(app: Sphinx) -> Path:
    return _source_dir(app) / "_generated"


def _getting_started_dir(app: Sphinx) -> Path:
    return _generated_dir(app) / "getting_started"


def _tutorial_pages_dir(app: Sphinx) -> Path:
    return _generated_dir(app) / "tutorials" / "pages"


def _tutorial_sections_dir(app: Sphinx) -> Path:
    return _generated_dir(app) / "tutorials" / "sections"


def _examples_generated_dir(app: Sphinx) -> Path:
    return _generated_dir(app) / "examples"


def _config_path(app: Sphinx) -> Path:
    config_value = app.config.example_docs_config
    path = Path(config_value)
    if not path.is_absolute():
        path = _source_dir(app) / path
    return path.resolve()


def _load_config(app: Sphinx) -> dict[str, Any]:
    path = _config_path(app)

    if not path.exists():
        raise FileNotFoundError(
            f"Example docs config file not found: {path}"
        )

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    if not isinstance(data, dict):
        raise ValueError(
            f"Root of example docs config must be a mapping: {path}"
        )

    return data


def _clean_generated(app: Sphinx) -> None:
    shutil.rmtree(_generated_dir(app), ignore_errors=True)

    _getting_started_dir(app).mkdir(parents=True, exist_ok=True)
    _tutorial_pages_dir(app).mkdir(parents=True, exist_ok=True)
    _tutorial_sections_dir(app).mkdir(parents=True, exist_ok=True)
    _examples_generated_dir(app).mkdir(parents=True, exist_ok=True)

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


def _title_from_path(path_str: str) -> str:
    return Path(path_str).stem.replace("_", " ").strip().title()


def _slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return value or "page"


def _page_slug_from_path(path_str: str) -> str:
    parts = Path(path_str).with_suffix("").parts
    return _slugify("-".join(parts))


def _section_slug(section_name: str) -> str:
    return _slugify(section_name)


def _resolve_example_file(app: Sphinx, path_str: str) -> Path:
    """
    Resolve an example path from config.

    Expected config paths are relative to the project root, such as:
        examples/getting_started.py
        examples/property_modeling/apply.py
    """
    path = Path(path_str)

    if path.is_absolute():
        return path

    candidate = _project_root(app) / path
    return candidate.resolve()

def _read_code(app: Sphinx, path_str: str) -> str:
    file_path = _resolve_example_file(app, path_str)
    if not file_path.exists():
        raise FileNotFoundError(
            f"Configured example file does not exist: {file_path}"
        )
    return file_path.read_text(encoding="utf-8")


def _entry_from_mapping(
    item: dict[str, Any],
    *,
    section: str | None = None,
) -> ExampleEntry:
    if "path" not in item:
        raise ValueError("Each entry must include a 'path' field.")

    title = item.get("title") or _title_from_path(item["path"])
    summary = item.get("summary")
    description = item.get("description")
    difficulty = item.get("difficulty")
    tags_raw = item.get("tags", [])

    if not isinstance(title, str) or not title.strip():
        raise ValueError(f"Invalid title for path {item['path']!r}.")
    if summary is not None and not isinstance(summary, str):
        raise ValueError(f"Invalid summary for path {item['path']!r}.")
    if description is not None and not isinstance(description, str):
        raise ValueError(f"Invalid description for path {item['path']!r}.")
    if not isinstance(tags_raw, list):
        raise ValueError(
            f"Invalid tags for path {item['path']!r}; expected a list."
        )

    _validate_difficulty(difficulty)

    tags = tuple(str(tag).strip() for tag in tags_raw if str(tag).strip())

    return ExampleEntry(
        path=item["path"],
        title=title.strip(),
        summary=summary.strip() if isinstance(summary, str) else None,
        description=description.strip() if isinstance(description, str) else None,
        difficulty=difficulty,
        tags=tags,
        section=section,
    )


def _parse_examples_entries(items: list[Any]) -> list[ExampleEntry]:
    entries: list[ExampleEntry] = []

    for item in items:
        if isinstance(item, str):
            entries.append(
                ExampleEntry(
                    path=item,
                    title=_title_from_path(item),
                )
            )
        elif isinstance(item, dict):
            entries.append(_entry_from_mapping(item))
        else:
            raise ValueError(
                "Each examples entry must be either a string path or a mapping."
            )

    return entries


def _assert_unique_paths(entries: list[ExampleEntry], *, label: str) -> None:
    seen: dict[str, int] = {}
    duplicates: list[str] = []

    for entry in entries:
        seen[entry.path] = seen.get(entry.path, 0) + 1

    for path, count in seen.items():
        if count > 1:
            duplicates.append(path)

    if duplicates:
        dup_text = ", ".join(sorted(duplicates))
        raise ValueError(f"Duplicate paths found in {label}: {dup_text}")


def _ensure_example_files_exist(app: Sphinx, entries: list[ExampleEntry], *, label: str) -> None:
    missing: list[str] = []

    for entry in entries:
        file_path = _resolve_example_file(app, entry.path)
        if not file_path.exists():
            missing.append(f"{entry.path} -> {file_path}")

    if missing:
        joined = "\n".join(f"  - {item}" for item in missing)
        raise FileNotFoundError(
            f"Missing example files referenced in {label}:\n{joined}"
        )


def _write_page(
    output_path: Path,
    *,
    title: str,
    summary: str | None,
    description: str | None,
    difficulty: str | None,
    source_path: str,
    code: str,
    previous: NavLink | None = None,
    next_: NavLink | None = None,
    section_name: str | None = None,
    section_docname: str | None = None,
) -> None:
    underline = "=" * len(title)

    lines: list[str] = [
        title,
        underline,
        "",
    ]

    if section_name and section_docname:
        lines.extend(
            [
                f"**Tutorial Section:** :doc:`{section_name} <{section_docname}>`",
                "",
            ]
        )

    if summary:
        lines.extend([summary, ""])

    meta_lines: list[str] = []
    if difficulty:
        meta_lines.append(f"**Difficulty:** {difficulty}")
    meta_lines.append(f"**Source:** ``{source_path}``")

    lines.extend(meta_lines)
    lines.append("")

    if description:
        lines.extend([description, ""])

    if previous or next_:
        lines.extend(
            [
                "Navigation",
                "----------",
                "",
            ]
        )
        if previous:
            lines.append(f"**Previous:** :doc:`{previous.title} <{previous.docname}>`")
        if next_:
            lines.append(f"**Next:** :doc:`{next_.title} <{next_.docname}>`")
        lines.append("")

    lines.extend(
        [
            "Code",
            "----",
            "",
            ".. code-block:: python",
            "",
        ]
    )

    for line in code.splitlines():
        lines.append(f"   {line}")
    lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _write_section_landing_page(
    output_path: Path,
    *,
    section_title: str,
    intro: str | None,
    page_docnames: list[str],
) -> None:
    underline = "=" * len(section_title)

    lines: list[str] = [
        section_title,
        underline,
        "",
    ]

    if intro:
        lines.extend([intro.strip(), ""])

    lines.extend(
        [
            ".. toctree::",
            "   :maxdepth: 1",
            "",
        ]
    )

    for docname in page_docnames:
        lines.append(f"   {docname}")

    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _write_index_page(
    output_path: Path,
    *,
    title: str,
    intro: str | None,
    docnames: list[str],
    maxdepth: int = 1,
) -> None:
    underline = "=" * len(title)

    lines: list[str] = [
        title,
        underline,
        "",
    ]

    if intro:
        lines.extend([intro.strip(), ""])

    lines.extend(
        [
            ".. toctree::",
            f"   :maxdepth: {maxdepth}",
            "",
        ]
    )

    for docname in docnames:
        lines.append(f"   {docname}")

    lines.append("")
    output_path.write_text("\n".join(lines), encoding="utf-8")


def _build_getting_started(app: Sphinx, config: dict[str, Any]) -> list[str]:
    items = config.get("getting_started", [])
    if not isinstance(items, list):
        raise ValueError("'getting_started' must be a list.")

    entries = [_entry_from_mapping(item) for item in items]
    _assert_unique_paths(entries, label="getting_started")
    _ensure_example_files_exist(app, entries, label="getting_started")

    docnames: list[str] = []

    for i, entry in enumerate(entries):
        slug = _page_slug_from_path(entry.path)
        docname = f"_generated/getting_started/{slug}"
        output_path = _getting_started_dir(app) / f"{slug}.rst"

        prev_link = None
        next_link = None

        if i > 0:
            prev_entry = entries[i - 1]
            prev_link = NavLink(
                title=prev_entry.title,
                docname=f"_generated/getting_started/{_page_slug_from_path(prev_entry.path)}",
            )

        if i < len(entries) - 1:
            next_entry = entries[i + 1]
            next_link = NavLink(
                title=next_entry.title,
                docname=f"_generated/getting_started/{_page_slug_from_path(next_entry.path)}",
            )

        _write_page(
            output_path,
            title=entry.title,
            summary=entry.summary,
            description=entry.description,
            difficulty=entry.difficulty,
            source_path=entry.path,
            code=_read_code(app, entry.path),
            previous=prev_link,
            next_=next_link,
        )
        docnames.append(docname)

    return docnames


def _build_tutorials(
    app: Sphinx,
    config: dict[str, Any],
) -> tuple[list[str], dict[str, list[str]]]:
    tutorial_sections = config.get("tutorials", [])
    if not isinstance(tutorial_sections, list):
        raise ValueError("'tutorials' must be a list.")

    section_docnames: list[str] = []
    pages_by_section_docname: dict[str, list[str]] = {}

    for section_item in tutorial_sections:
        if not isinstance(section_item, dict):
            raise ValueError("Each tutorials section must be a mapping.")

        section_name = section_item.get("section")
        if not isinstance(section_name, str) or not section_name.strip():
            raise ValueError(
                "Each tutorials section must include a non-empty 'section'."
            )

        section_name = section_name.strip()
        section_intro = section_item.get("description")
        pages = section_item.get("pages", [])

        if not isinstance(pages, list):
            raise ValueError(
                f"The 'pages' field for tutorials section {section_name!r} must be a list."
            )

        entries = [
            _entry_from_mapping(page_item, section=section_name)
            for page_item in pages
        ]

        _assert_unique_paths(entries, label=f"tutorial section {section_name!r}")
        _ensure_example_files_exist(app, entries, label=f"tutorial section {section_name!r}")

        page_docnames: list[str] = []
        section_slug = _section_slug(section_name)
        section_docname = f"_generated/tutorials/sections/{section_slug}"
        section_output_path = _tutorial_sections_dir(app) / f"{section_slug}.rst"

        for i, entry in enumerate(entries):
            page_slug = _page_slug_from_path(entry.path)
            page_docname = f"_generated/tutorials/pages/{page_slug}"
            page_output_path = _tutorial_pages_dir(app) / f"{page_slug}.rst"

            prev_link = None
            next_link = None

            if i > 0:
                prev_entry = entries[i - 1]
                prev_link = NavLink(
                    title=prev_entry.title,
                    docname=f"_generated/tutorials/pages/{_page_slug_from_path(prev_entry.path)}",
                )

            if i < len(entries) - 1:
                next_entry = entries[i + 1]
                next_link = NavLink(
                    title=next_entry.title,
                    docname=f"_generated/tutorials/pages/{_page_slug_from_path(next_entry.path)}",
                )

            _write_page(
                page_output_path,
                title=entry.title,
                summary=entry.summary,
                description=entry.description,
                difficulty=entry.difficulty,
                source_path=entry.path,
                code=_read_code(app, entry.path),
                previous=prev_link,
                next_=next_link,
                section_name=section_name,
                section_docname=section_docname,
            )

            page_docnames.append(page_docname)

        _write_section_landing_page(
            section_output_path,
            section_title=section_name,
            intro=section_intro,
            page_docnames=page_docnames,
        )

        section_docnames.append(section_docname)
        pages_by_section_docname[section_docname] = page_docnames

    return section_docnames, pages_by_section_docname


def _build_examples(app: Sphinx, config: dict[str, Any]) -> list[str]:
    items = config.get("examples", [])
    if not isinstance(items, list):
        raise ValueError("'examples' must be a list.")

    entries = _parse_examples_entries(items)
    _assert_unique_paths(entries, label="examples")
    _ensure_example_files_exist(app, entries, label="examples")

    docnames: list[str] = []

    for entry in entries:
        slug = _page_slug_from_path(entry.path)
        docname = f"_generated/examples/{slug}"
        output_path = _examples_generated_dir(app) / f"{slug}.rst"

        _write_page(
            output_path,
            title=entry.title,
            summary=entry.summary,
            description=entry.description,
            difficulty=entry.difficulty,
            source_path=entry.path,
            code=_read_code(app, entry.path),
        )

        docnames.append(docname)

    return docnames


def _write_getting_started_landing(app: Sphinx, docnames: list[str]) -> None:
    _write_index_page(
        _source_dir(app) / "getting_started.rst",
        title="Getting Started",
        intro=(
            "Start here if you are new to Petres. These pages introduce the "
            "basic workflow and the most common first steps."
        ),
        docnames=docnames,
        maxdepth=1,
    )


def _write_tutorials_landing(app: Sphinx, section_docnames: list[str]) -> None:
    _write_index_page(
        _source_dir(app) / "tutorials.rst",
        title="Tutorials",
        intro="Task-oriented walkthroughs for common Petres workflows.",
        docnames=section_docnames,
        maxdepth=2,
    )


def _write_examples_landing(app: Sphinx, docnames: list[str]) -> None:
    _write_index_page(
        _source_dir(app) / "examples.rst",
        title="Examples",
        intro="Reference examples and runnable scripts.",
        docnames=docnames,
        maxdepth=2,
    )


def generate_example_docs(app: Sphinx) -> None:
    logger.info("[exampledocs] Generating example documentation...")

    config = _load_config(app)
    _clean_generated(app)

    getting_started_docnames = _build_getting_started(app, config)
    tutorial_section_docnames, _ = _build_tutorials(app, config)
    examples_docnames = _build_examples(app, config)

    _write_getting_started_landing(app, getting_started_docnames)
    _write_tutorials_landing(app, tutorial_section_docnames)
    _write_examples_landing(app, examples_docnames)

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
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }