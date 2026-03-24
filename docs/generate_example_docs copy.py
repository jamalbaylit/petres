from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import textwrap
import yaml


ROOT = Path(__file__).resolve().parent
SOURCE_DIR = ROOT / "source"
GENERATED_DIR = SOURCE_DIR / "_generated"
CONFIG_PATH = ROOT / "docs_examples.yml"


@dataclass(frozen=True)
class ExampleEntry:
    path: str
    title: str | None = None
    summary: str | None = None
    description: str | None = None
    difficulty: str | None = None


def _load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_PATH}")
    with CONFIG_PATH.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if not isinstance(data, dict):
        raise ValueError("Root of docs_examples.yml must be a mapping.")
    return data


def _clean_generated() -> None:
    shutil.rmtree(GENERATED_DIR, ignore_errors=True)
    (GENERATED_DIR / "getting_started").mkdir(parents=True, exist_ok=True)
    (GENERATED_DIR / "tutorials").mkdir(parents=True, exist_ok=True)
    (GENERATED_DIR / "examples").mkdir(parents=True, exist_ok=True)


def _validate_difficulty(value: str | None) -> None:
    if value is None:
        return
    allowed = {"beginner", "intermediate", "advanced"}
    if value not in allowed:
        raise ValueError(
            f"Invalid difficulty {value!r}. Allowed values: {sorted(allowed)}."
        )


def _slug_from_path(path_str: str) -> str:
    p = Path(path_str)
    parts = list(p.with_suffix("").parts)
    return "__".join(parts)


def _title_from_path(path_str: str) -> str:
    stem = Path(path_str).stem
    return stem.replace("_", " ").strip().title()


def _read_code(path_str: str) -> str:
    file_path = ROOT / path_str
    if not file_path.exists():
        raise FileNotFoundError(f"Configured example file does not exist: {file_path}")
    return file_path.read_text(encoding="utf-8")


def _write_rst_page(
    output_path: Path,
    *,
    title: str,
    summary: str | None,
    description: str | None,
    difficulty: str | None,
    source_path: str,
    code: str,
) -> None:
    title_underline = "=" * len(title)

    lines: list[str] = [
        title,
        title_underline,
        "",
    ]

    if summary:
        lines.extend([summary.strip(), ""])

    if difficulty:
        lines.extend(
            [
                f"**Difficulty:** {difficulty}",
                "",
            ]
        )

    lines.extend(
        [
            f"**Source:** ``{source_path}``",
            "",
        ]
    )

    if description:
        lines.extend([description.strip(), ""])

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


def _entry_from_mapping(item: dict) -> ExampleEntry:
    if "path" not in item:
        raise ValueError("Each entry must include a 'path'.")
    entry = ExampleEntry(
        path=item["path"],
        title=item.get("title"),
        summary=item.get("summary"),
        description=item.get("description"),
        difficulty=item.get("difficulty"),
    )
    _validate_difficulty(entry.difficulty)
    return entry


def _build_getting_started(config: dict) -> list[str]:
    docnames: list[str] = []

    for item in config.get("getting_started", []):
        entry = _entry_from_mapping(item)
        slug = _slug_from_path(entry.path)
        out = GENERATED_DIR / "getting_started" / f"{slug}.rst"
        code = _read_code(entry.path)

        _write_rst_page(
            out,
            title=entry.title or _title_from_path(entry.path),
            summary=entry.summary,
            description=entry.description,
            difficulty=entry.difficulty,
            source_path=entry.path,
            code=code,
        )
        docnames.append(f"_generated/getting_started/{slug}")

    return docnames


def _build_tutorials(config: dict) -> tuple[list[str], dict[str, list[str]]]:
    all_docnames: list[str] = []
    sections: dict[str, list[str]] = {}

    for section in config.get("tutorials", []):
        section_name = section.get("section")
        if not section_name:
            raise ValueError("Each tutorials section must include 'section'.")
        pages = section.get("pages", [])
        section_docnames: list[str] = []

        for item in pages:
            entry = _entry_from_mapping(item)
            slug = _slug_from_path(entry.path)
            out = GENERATED_DIR / "tutorials" / f"{slug}.rst"
            code = _read_code(entry.path)

            _write_rst_page(
                out,
                title=entry.title or _title_from_path(entry.path),
                summary=entry.summary,
                description=entry.description,
                difficulty=entry.difficulty,
                source_path=entry.path,
                code=code,
            )

            docname = f"_generated/tutorials/{slug}"
            section_docnames.append(docname)
            all_docnames.append(docname)

        sections[section_name] = section_docnames

    return all_docnames, sections


def _build_examples(config: dict) -> list[str]:
    docnames: list[str] = []

    for item in config.get("examples", []):
        if isinstance(item, str):
            entry = ExampleEntry(path=item)
        elif isinstance(item, dict):
            entry = _entry_from_mapping(item)
        else:
            raise ValueError("Each examples entry must be a string path or a mapping.")

        slug = _slug_from_path(entry.path)
        out = GENERATED_DIR / "examples" / f"{slug}.rst"
        code = _read_code(entry.path)

        _write_rst_page(
            out,
            title=entry.title or _title_from_path(entry.path),
            summary=entry.summary,
            description=entry.description,
            difficulty=entry.difficulty,
            source_path=entry.path,
            code=code,
        )
        docnames.append(f"_generated/examples/{slug}")

    return docnames


def _write_section_index(
    output_path: Path,
    *,
    title: str,
    intro: str | None,
    docnames: list[str],
    maxdepth: int = 1,
) -> None:
    title_underline = "=" * len(title)
    lines = [title, title_underline, ""]
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


def _write_tutorials_landing(sections: dict[str, list[str]]) -> None:
    output_path = SOURCE_DIR / "tutorials.rst"
    lines = [
        "Tutorials",
        "=========",
        "",
        "Task-oriented walkthroughs for common Petres workflows.",
        "",
    ]

    for section_name, docnames in sections.items():
        lines.extend(
            [
                section_name,
                "-" * len(section_name),
                "",
                ".. toctree::",
                "   :maxdepth: 1",
                "",
            ]
        )
        for docname in docnames:
            lines.append(f"   {docname}")
        lines.append("")

    output_path.write_text("\n".join(lines), encoding="utf-8")


def _write_getting_started_landing(docnames: list[str]) -> None:
    _write_section_index(
        SOURCE_DIR / "getting_started.rst",
        title="Getting Started",
        intro=(
            "Start here if you are new to Petres. These pages introduce the "
            "basic workflow and the most common first steps."
        ),
        docnames=docnames,
        maxdepth=1,
    )


def _write_examples_landing(docnames: list[str]) -> None:
    _write_section_index(
        SOURCE_DIR / "examples.rst",
        title="Examples",
        intro="Reference examples and runnable scripts.",
        docnames=docnames,
        maxdepth=1,
    )


def main() -> None:
    config = _load_config()
    _clean_generated()

    getting_started_docnames = _build_getting_started(config)
    examples_docnames = _build_examples(config)
    _, tutorial_sections = _build_tutorials(config)

    _write_getting_started_landing(getting_started_docnames)
    _write_tutorials_landing(tutorial_sections)
    _write_examples_landing(examples_docnames)

    print("Generated example documentation successfully.")


if __name__ == "__main__":
    main()