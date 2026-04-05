from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
import tempfile
import tomllib
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from packaging.version import Version


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT_PATH = PROJECT_ROOT / "pyproject.toml"


@dataclass
class DependencySpec:
    name: str
    minimum: str


def _run(command: list[str], *, cwd: Path = PROJECT_ROOT) -> tuple[int, str]:
    process = subprocess.run(
        command,
        cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        check=False,
    )
    return process.returncode, process.stdout


def _load_project_deps(pyproject_path: Path) -> list[DependencySpec]:
    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    dep_entries = data["project"]["dependencies"]
    specs: list[DependencySpec] = []

    pattern = re.compile(r"^\s*([A-Za-z0-9_.-]+)\s*>=\s*([^;\s]+)")
    for dep in dep_entries:
        match = pattern.match(dep)
        if not match:
            continue
        specs.append(DependencySpec(name=match.group(1).lower(), minimum=match.group(2)))
    return specs


def _fetch_versions(package_name: str) -> list[str]:
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Failed to fetch {package_name} metadata from PyPI: {exc}") from exc

    versions: list[Version] = []
    releases: dict[str, list[dict]] = payload.get("releases", {})
    for raw_version, files in releases.items():
        if not files:
            continue
        try:
            version = Version(raw_version)
        except Exception:
            continue
        if version.is_prerelease or version.is_devrelease:
            continue
        if all(file.get("yanked", False) for file in files):
            continue
        versions.append(version)

    versions.sort()
    return [str(v) for v in versions]


def _write_overrides_file(pins: dict[str, str]) -> Path:
    handle = tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8")
    with handle:
        for name, version in sorted(pins.items()):
            handle.write(f"{name}=={version}\n")
    return Path(handle.name)


def _validate_candidate(pins: dict[str, str], pytest_args: Iterable[str]) -> tuple[bool, str]:
    overrides_path = _write_overrides_file(pins)
    try:
        install_command = [
            "uv",
            "pip",
            "install",
            "--resolution",
            "lowest-direct",
            "--upgrade",
            ".",
            "--group",
            "test",
            "--overrides",
            str(overrides_path),
        ]
        install_rc, install_output = _run(install_command)
        if install_rc != 0:
            return False, install_output

        test_command = ["uv", "run", "--no-sync", "--group", "test", "pytest", *pytest_args]
        test_rc, test_output = _run(test_command)
        return test_rc == 0, test_output
    finally:
        overrides_path.unlink(missing_ok=True)


def _find_min_working_version(
    package_name: str,
    current_version: str,
    selected_versions: dict[str, str],
    pytest_args: Iterable[str],
) -> str:
    versions = _fetch_versions(package_name)
    current = Version(current_version)

    candidates = [v for v in versions if Version(v) <= current]
    if not candidates:
        return current_version

    low = 0
    high = len(candidates) - 1
    best: str | None = None

    while low <= high:
        middle = (low + high) // 2
        candidate = candidates[middle]
        trial_pins = dict(selected_versions)
        trial_pins[package_name] = candidate

        ok, _ = _validate_candidate(trial_pins, pytest_args)
        if ok:
            best = candidate
            high = middle - 1
        else:
            low = middle + 1

    return best or current_version


def _apply_versions_to_pyproject(pyproject_path: Path, updated: dict[str, str]) -> None:
    lines = pyproject_path.read_text(encoding="utf-8").splitlines()
    in_dependencies = False

    dep_pattern = re.compile(r'^(\s*")([A-Za-z0-9_.-]+)(>=)([^"\s]+)("\s*,?\s*)$')

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "dependencies = [":
            in_dependencies = True
            continue

        if in_dependencies and stripped == "]":
            in_dependencies = False
            continue

        if not in_dependencies:
            continue

        match = dep_pattern.match(line)
        if not match:
            continue

        name = match.group(2).lower()
        if name not in updated:
            continue

        prefix = match.group(1)
        op = match.group(3)
        suffix = match.group(5)
        lines[index] = f"{prefix}{name}{op}{updated[name]}{suffix}"

    pyproject_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Discover lower working bounds for [project].dependencies by pinning candidates, "
            "running tests, and optionally updating pyproject.toml."
        )
    )
    parser.add_argument(
        "--package",
        action="append",
        dest="packages",
        help="Restrict discovery to one or more package names (repeatable).",
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write discovered minima back to pyproject.toml.",
    )
    parser.add_argument(
        "--pytest-args",
        default="-q",
        help=(
            "Arguments forwarded to pytest as a quoted string (default: '-q'). "
            "Example: --pytest-args \"-q -m unit\"."
        ),
    )

    args = parser.parse_args()
    pytest_args = shlex.split(args.pytest_args)
    if not pytest_args:
        pytest_args = ["-q"]

    deps = _load_project_deps(PYPROJECT_PATH)
    if not deps:
        print("No >= dependencies found under [project].dependencies.")
        return 1

    selected: dict[str, str] = {dep.name: dep.minimum for dep in deps}
    target_names = {name.lower() for name in args.packages} if args.packages else set(selected)

    unknown = sorted(target_names - set(selected))
    if unknown:
        print(f"Unknown package(s): {', '.join(unknown)}")
        return 1

    print("Starting minimum bound discovery...")
    print(f"Pytest args: {' '.join(pytest_args)}")

    for dep in deps:
        if dep.name not in target_names:
            continue

        current = selected[dep.name]
        print(f"\n[{dep.name}] current minimum: {current}")

        found = _find_min_working_version(
            package_name=dep.name,
            current_version=current,
            selected_versions=selected,
            pytest_args=pytest_args,
        )

        selected[dep.name] = found
        marker = "(changed)" if found != current else "(unchanged)"
        print(f"[{dep.name}] discovered minimum: {found} {marker}")

    print("\nDiscovered minimum bounds:")
    for name in sorted(target_names):
        print(f"- {name}>={selected[name]}")

    if args.apply:
        _apply_versions_to_pyproject(PYPROJECT_PATH, selected)
        print("\nUpdated pyproject.toml with discovered minimums.")
    else:
        print("\nDry run complete. Re-run with --apply to update pyproject.toml.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
