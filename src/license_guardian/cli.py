from __future__ import annotations

import datetime
from collections.abc import Sequence
from pathlib import Path

import click

from .core import ensure_license_file, ensure_spdx, iter_files


@click.command()
@click.option(
    "--path",
    "path_str",
    type=click.Path(path_type=Path, exists=True, file_okay=False),
    default=".",
    show_default=True,
    help="Ruta raíz a escanear.",
)
@click.option(
    "--ext",
    "exts",
    multiple=True,
    default=[".py"],
    show_default=True,
    help="Extensiones a validar, repetible.",
)
@click.option(
    "--mode",
    type=click.Choice(["check", "fix"], case_sensitive=False),
    default="check",
    show_default=True,
    help="Validar o insertar encabezados.",
)
@click.option(
    "--license-id",
    "license_id",
    type=str,
    default="MIT",
    show_default=True,
    help="SPDX License Identifier esperado.",
)
@click.option(
    "--require-license-file/--no-require-license-file",
    default=False,
    show_default=True,
    help="Si true, exige LICENSE presente en modo check.",
)
@click.option(
    "--author",
    type=str,
    default="CoderDeltaLAN",
    show_default=True,
    help="Autor para LICENSE al hacer --mode fix.",
)
def main(
    path_str: str,
    exts: Sequence[str],
    mode: str,
    license_id: str,
    require_license_file: bool,
    author: str,
) -> None:
    root = Path(path_str).resolve()
    missing = 0

    if mode.lower() == "fix":
        yr = str(datetime.datetime.utcnow().year)
        ensure_license_file(root, author=author, year=yr, license_id=license_id, autofix=True)
    elif require_license_file:
        ok = ensure_license_file(
            root,
            author=author,
            year=str(datetime.datetime.utcnow().year),
            license_id=license_id,
            autofix=False,
        )
        if not ok:
            click.echo("Missing LICENSE file.", err=True)
            missing += 1

    for f in iter_files(root, exts):
        ok = ensure_spdx(f, license_id=license_id, autofix=(mode.lower() == "fix"))
        if not ok:
            missing += 1

    if mode.lower() == "check":
        if missing > 0:
            click.echo(f"Missing SPDX header in {missing} file(s).", err=True)
            raise SystemExit(1)
        click.echo("All files have SPDX headers.")
        return

    if missing > 0:
        click.echo(f"Some files were not fixed: {missing}", err=True)
        raise SystemExit(1)
    click.echo("SPDX headers ensured.")
