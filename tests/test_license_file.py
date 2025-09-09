from __future__ import annotations

from pathlib import Path

from license_guardian.core import ensure_license_file, license_file_path


def test_license_creation(tmp_path: Path) -> None:
    assert license_file_path(tmp_path) is None
    assert ensure_license_file(
        tmp_path, author="CoderDeltaLAN", year="2025", license_id="MIT", autofix=True
    )
    p = license_file_path(tmp_path)
    assert p is not None
    text = p.read_text(encoding="utf-8")
    assert "MIT License" in text
    assert "Permission is hereby granted" in text
