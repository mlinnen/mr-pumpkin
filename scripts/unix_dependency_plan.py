#!/usr/bin/env python3
"""Build Unix dependency install plans for release scripts."""

from __future__ import annotations

from pathlib import Path
import argparse
import shlex


RASPBERRY_PI_APT_PACKAGE_MAP = {
    "mutagen": "python3-mutagen",
    "pygame": "python3-pygame",
    "websockets": "python3-websockets",
}


class InstallPlan:
    def __init__(self, apt_packages: list[str], pip_requirements: list[str]):
        self.apt_packages = apt_packages
        self.pip_requirements = pip_requirements


def normalize_package_name(name: str) -> str:
    """Normalize requirement names for matching across packaging styles."""
    return name.lower().replace("_", "-").replace(".", "-")


def extract_requirement_name(requirement_line: str) -> str | None:
    """Extract the package name from a pip requirement line."""
    line = requirement_line.split("#", 1)[0].strip()
    if not line:
        return None

    if line.startswith(("-r ", "--requirement ")):
        return None

    if line.startswith("-"):
        return None

    marker_free = line.split(";", 1)[0].strip()
    name_chars: list[str] = []
    for char in marker_free:
        if char.isalnum() or char in "._-":
            name_chars.append(char)
            continue
        break

    if not name_chars:
        return None

    return "".join(name_chars)


def load_requirement_lines(
    requirement_file: str | Path,
    visited: set[Path] | None = None,
) -> list[str]:
    """Load requirement lines, resolving nested -r directives."""
    path = Path(requirement_file).resolve()
    visited = visited or set()
    if path in visited:
        return []

    visited.add(path)
    lines: list[str] = []

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue

        if line.startswith("-r "):
            nested_path = (path.parent / line[3:].strip()).resolve()
            lines.extend(load_requirement_lines(nested_path, visited))
            continue

        if line.startswith("--requirement "):
            nested_path = (path.parent / line[len("--requirement "):].strip()).resolve()
            lines.extend(load_requirement_lines(nested_path, visited))
            continue

        lines.append(line)

    return lines


def build_install_plan(
    requirement_files: list[str | Path],
    raspberry_pi: bool = False,
) -> InstallPlan:
    """Split requirements into apt-managed and pip-managed groups."""
    apt_packages: list[str] = []
    pip_requirements: list[str] = []
    seen_apt: set[str] = set()
    seen_pip: set[str] = set()

    for requirement_file in requirement_files:
        for requirement_line in load_requirement_lines(requirement_file):
            package_name = extract_requirement_name(requirement_line)
            normalized_name = normalize_package_name(package_name) if package_name else None
            apt_package = None

            if raspberry_pi and normalized_name:
                apt_package = RASPBERRY_PI_APT_PACKAGE_MAP.get(normalized_name)

            if apt_package:
                if apt_package not in seen_apt:
                    apt_packages.append(apt_package)
                    seen_apt.add(apt_package)
                continue

            if requirement_line not in seen_pip:
                pip_requirements.append(requirement_line)
                seen_pip.add(requirement_line)

    return InstallPlan(
        apt_packages=sorted(apt_packages),
        pip_requirements=pip_requirements,
    )


def emit_shell(plan: InstallPlan) -> str:
    """Emit bash array assignments for eval in shell scripts."""
    apt_packages = " ".join(shlex.quote(package) for package in plan.apt_packages)
    pip_requirements = " ".join(shlex.quote(requirement) for requirement in plan.pip_requirements)
    return f"APT_PACKAGES=({apt_packages})\nPIP_REQUIREMENTS=({pip_requirements})"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("requirement_files", nargs="+", help="Requirement files to analyze")
    parser.add_argument(
        "--raspberry-pi",
        action="store_true",
        help="Prefer apt packages for dependencies available on Raspberry Pi OS",
    )
    parser.add_argument(
        "--emit-shell",
        action="store_true",
        help="Emit bash array assignments for shell scripts",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    plan = build_install_plan(
        requirement_files=args.requirement_files,
        raspberry_pi=args.raspberry_pi,
    )

    if args.emit_shell:
        print(emit_shell(plan))
    else:
        print(f"apt_packages={plan.apt_packages}")
        print(f"pip_requirements={plan.pip_requirements}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
