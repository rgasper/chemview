"""Tests for CLI rendering functions."""

from pathlib import Path

import pytest
from PIL import Image
from typer.testing import CliRunner

from chemview.cli import _smiles_to_image, app

runner = CliRunner()


class TestSmilesToImage:
    """Tests for _smiles_to_image."""

    def test_valid_smiles_returns_pil_image(self) -> None:
        """A valid SMILES should return a PIL Image of the requested size."""
        img = _smiles_to_image("CCO", width=200, height=150)
        assert isinstance(img, Image.Image)
        assert img.size == (200, 150)

    def test_invalid_smiles_raises_value_error(self) -> None:
        """An invalid SMILES should raise ValueError."""
        with pytest.raises(ValueError, match="could not parse"):
            _smiles_to_image("not_a_smiles_$$$$", width=200, height=150)


class TestViewCommand:
    """Tests for the view CLI command."""

    def test_output_flag_saves_file(self, tmp_path: "Path") -> None:
        """--output should save the image to the specified path."""
        dest = tmp_path / "mol.png"
        result = runner.invoke(app, ["CCO", "-o", str(dest)])
        assert result.exit_code == 0
        assert dest.exists()
        assert dest.stat().st_size > 0

    def test_invalid_smiles_exits_with_error(self) -> None:
        """Invalid SMILES should exit with code 1."""
        result = runner.invoke(app, ["not_valid_$$"])
        assert result.exit_code == 1
        assert "Error" in result.output
