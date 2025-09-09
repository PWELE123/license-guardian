from __future__ import annotations

import re
import tomllib
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any

from .headers import MIT_LICENSE, header_for_path

_IGNORED_DIRS = {".git", ".venv", "__pycache__", "dist", "build", "node_modules", "vendor"}


def iter_files(root: Path, exts: Sequence[str]) -> Iterable[Path]:
    for p in root.rglob("*"):
        if p.is_dir():
            if p.name in _IGNORED_DIRS:
                continue
            continue
        if p.suffix.lower() in {e.lower() for e in exts}:
            yield p


_SPX = re.compile(r"^\s*(?:#|//)\s*SPDX-License-Identifier:\s*(?P<id>[A-Za-z0-9.\-+]+)\s*$")


def has_spdx(file: Path, license_id: str = "MIT") -> bool:
    try:
        with file.open("r", encoding="utf-8") as fh:
            for i, line in enumerate(fh):
                if i > 5:
                    break
                m = _SPX.match(line)
                if m:
                    return m.group("id") == license_id
    except FileNotFoundError:
        return False
    return False


def ensure_spdx(file: Path, license_id: str = "MIT", autofix: bool = False) -> bool:
    if has_spdx(file, license_id):
        return True
    if not autofix:
        return False
    text = file.read_text(encoding="utf-8")
    header = header_for_path(file, license_id)
    file.write_text(header + text, encoding="utf-8")
    return True


def license_file_path(root: Path) -> Path | None:
    for name in ("LICENSE", "LICENSE.txt", "LICENSE.md"):
        p = root / name
        if p.exists():
            return p
    return None


def ensure_license_file(
    root: Path,
    author: str,
    year: str,
    license_id: str = "MIT",
    autofix: bool = False,
) -> bool:
    p = license_file_path(root)
    if p:
        return True
    if not autofix:
        return False
    content = MIT_LICENSE.format(year=year, author=author)
    (root / "LICENSE").write_text(content, encoding="utf-8")
    return True


def read_license_from_pyproject(root: Path) -> str | None:
    pyproj = root / "pyproject.toml"
    if not pyproj.exists():
        return None
    data: dict[str, Any] = tomllib.loads(pyproj.read_text(encoding="utf-8"))

    tool = data.get("tool")
    if isinstance(tool, dict):
        poetry = tool.get("poetry")
        if isinstance(poetry, dict):
            lic = poetry.get("license")
            if isinstance(lic, str):
                return lic

    proj = data.get("project")
    if isinstance(proj, dict):
        lic2 = proj.get("license")
        if isinstance(lic2, str):
            return lic2
        if isinstance(lic2, dict):
            text = lic2.get("text")
            if isinstance(text, str):
                return text
            file_ = lic2.get("file")
            if isinstance(file_, str):
                try:
                    return (root / file_).read_text(encoding="utf-8")
                except Exception:
                    return None
    return None


def ping() -> str:
    return "pong"
