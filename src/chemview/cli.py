"""CLI for rendering SMILES strings as 2D molecule images."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
from typing import TYPE_CHECKING, Annotated, Optional

if TYPE_CHECKING:
    from PIL import Image

import typer
from loguru import logger
from rich.console import Console

app = typer.Typer(help="Visualize SMILES strings as 2D molecule images.")
console = Console()


def _smiles_to_image(
    smiles: str,
    width: int,
    height: int,
) -> Image.Image:
    """Parse a SMILES string and render it to a PIL Image.

    Args:
        smiles: A valid SMILES string, e.g. "CCO" for ethanol.
        width: Image width in pixels.
        height: Image height in pixels.

    Returns:
        A PIL Image of the rendered molecule.

    Raises:
        ValueError: If the SMILES string cannot be parsed by RDKit.

    Example:
        >>> img = _smiles_to_image("CCO", 400, 300)
        >>> img.size
        (400, 300)
    """
    from rdkit import Chem
    from rdkit.Chem import Draw

    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"RDKit could not parse SMILES: {smiles!r}")

    return Draw.MolToImage(mol, size=(width, height))


def _render_smiles(
    smiles: str,
    output_path: Path,
    width: int,
    height: int,
) -> None:
    """Render a SMILES string to a PNG image file.

    Args:
        smiles: A valid SMILES string, e.g. "CCO" for ethanol.
        output_path: Filesystem path where the PNG will be written.
        width: Image width in pixels.
        height: Image height in pixels.

    Raises:
        ValueError: If the SMILES string cannot be parsed by RDKit.

    Example:
        >>> _render_smiles("CCO", Path("/tmp/ethanol.png"), 400, 300)
        # writes a 400x300 PNG of ethanol to /tmp/ethanol.png
    """
    img = _smiles_to_image(smiles, width, height)
    img.save(str(output_path))


def _open_image(path: Path) -> None:
    """Open an image using the platform's default viewer.

    Args:
        path: Path to the image file to open.
    """
    if sys.platform == "darwin":
        subprocess.Popen(["open", str(path)])
    elif sys.platform == "linux":
        subprocess.Popen(["xdg-open", str(path)])
    elif sys.platform == "win32":
        subprocess.Popen(["start", str(path)], shell=True)
    else:
        logger.warning(f"Unsupported platform {sys.platform!r}; image saved to {path}")


@app.command()
def view(
    smiles: Annotated[str, typer.Argument(help="SMILES string to visualize")],
    width: Annotated[
        int, typer.Option("--width", "-w", help="Image width in pixels")
    ] = 400,
    height: Annotated[
        int, typer.Option("--height", "-h", help="Image height in pixels")
    ] = 300,
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output", "-o", help="Save image to this path instead of opening"
        ),
    ] = None,
) -> None:
    """Render a SMILES string and open the resulting image.

    By default the image is written to a temporary file and opened with the
    system viewer. Pass --output/-o to save to a specific location instead.

    Example:
        chemview "CCO"
        chemview "c1ccccc1" --width 600 --height 400
        chemview "CCO" -o ethanol.png
    """
    if output is not None:
        dest = output
    else:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".png", delete=False, prefix="chemview_"
        )
        dest = Path(tmp.name)
        tmp.close()

    try:
        _render_smiles(smiles, dest, width, height)
    except ValueError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc

    console.print(f"[green]Rendered[/green] {smiles!r} -> {dest}")

    if output is None:
        _open_image(dest)
