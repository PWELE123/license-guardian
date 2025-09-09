from __future__ import annotations

from pathlib import Path

from license_guardian.core import ensure_spdx, has_spdx


def test_spdx_insert_and_check(tmp_path: Path) -> None:
    f = tmp_path / "a.py"
    f.write_text("print('hi')\n", encoding="utf-8")
    assert not has_spdx(f, "MIT")
    assert ensure_spdx(f, "MIT", autofix=True)
    assert has_spdx(f, "MIT")
    # idempotente
    assert ensure_spdx(f, "MIT", autofix=True)
