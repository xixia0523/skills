#!/usr/bin/env python3
"""Install or replace custom-imagegen from a downloaded Skill folder."""

from __future__ import annotations

import argparse
import ast
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile


SKILL_NAME = "custom-imagegen"
PACKAGE_FILES = (
    "SKILL.md",
    "README.md",
    "agents/openai.yaml",
    "references/setup.md",
    "references/install.md",
    "scripts/image_gen.py",
    "scripts/install_skill.py",
)


class InstallError(Exception):
    pass


def default_destination() -> Path:
    codex_root = os.getenv("CODEX_HOME", "").strip()
    root = Path(codex_root).expanduser() if codex_root else Path.home() / ".codex"
    return root / "skills" / SKILL_NAME


def active_config_path() -> Path:
    override = os.getenv("CUSTOM_IMAGEGEN_CONFIG", "").strip()
    if override:
        return Path(override).expanduser()
    config_home = os.getenv("XDG_CONFIG_HOME", "").strip()
    root = Path(config_home).expanduser() if config_home else Path.home() / ".config"
    return root / SKILL_NAME / ".env"


def validate_identity(directory: Path) -> None:
    manifest = directory / "SKILL.md"
    if not manifest.is_file() or manifest.is_symlink():
        raise InstallError(f"not a {SKILL_NAME} Skill directory: {directory}")
    content = manifest.read_text(encoding="utf-8")
    sections = content.split("---", 2)
    if len(sections) != 3 or sections[0].strip():
        raise InstallError(f"invalid Skill frontmatter: {manifest}")
    fields = {}
    for line in sections[1].splitlines():
        if line and not line[0].isspace() and ":" in line:
            key, value = line.split(":", 1)
            fields[key] = value.strip().strip("\"'")
    if fields.get("name") != SKILL_NAME or not fields.get("description"):
        raise InstallError(f"expected a Skill named {SKILL_NAME}: {manifest}")


def validate_source(source: Path) -> None:
    validate_identity(source)
    for relative in PACKAGE_FILES:
        path = source / relative
        if not path.is_file() or path.is_symlink() or source not in path.resolve().parents:
            raise InstallError(f"missing or unsupported package file: {relative}")
        if path.suffix == ".py":
            try:
                ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            except (SyntaxError, UnicodeError) as exc:
                raise InstallError(f"invalid Python script: {relative}") from exc


def install_skill(source: Path, destination: Path) -> str:
    source = source.expanduser().resolve()
    destination = destination.expanduser().absolute()
    validate_source(source)
    if destination.is_symlink():
        raise InstallError(f"destination is a symbolic link; select its target with --dest: {destination}")
    resolved_destination = destination.resolve()
    configuration = active_config_path().resolve()
    if configuration == resolved_destination or resolved_destination in configuration.parents:
        raise InstallError(
            "configuration is inside the installation directory; move it outside the Skill "
            "and set CUSTOM_IMAGEGEN_CONFIG before updating"
        )
    if source == resolved_destination:
        return "unchanged"
    updating = destination.exists()
    if updating:
        validate_identity(destination)

    destination.parent.mkdir(parents=True, exist_ok=True)
    work = Path(tempfile.mkdtemp(prefix=f".{SKILL_NAME}-install-", dir=destination.parent))
    staged = work / "new"
    backup = work / "previous"
    installed = False
    try:
        for relative in PACKAGE_FILES:
            target = staged / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source / relative, target)
        validate_source(staged)
        if updating:
            destination.rename(backup)
        try:
            staged.rename(destination)
        except BaseException:
            if updating:
                try:
                    backup.rename(destination)
                except OSError as exc:
                    raise InstallError(
                        f"replacement and rollback failed; previous Skill preserved at {backup}"
                    ) from exc
            raise
        installed = True
    finally:
        # If rollback fails, leave the previous installation available for recovery.
        if installed or not backup.exists():
            shutil.rmtree(work, ignore_errors=True)
    return "updated" if updating else "installed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source", type=Path, default=Path(__file__).resolve().parents[1],
        help="downloaded Skill folder (default: this script's Skill folder)",
    )
    parser.add_argument(
        "--dest", type=Path, default=default_destination(),
        help="full destination Skill directory (default: $CODEX_HOME/skills/custom-imagegen)",
    )
    args = parser.parse_args()
    try:
        action = install_skill(args.source, args.dest)
    except (InstallError, OSError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps({
        "action": action,
        "skill_dir": str(args.dest.expanduser().absolute()),
        "configuration": "preserved; reuse existing external configuration and environment variables",
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
