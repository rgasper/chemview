"""Tests for CLI rendering functions."""

from PIL import Image

from chemview.cli import _smiles_to_image


class TestSmilesToImage:
    """Tests for _smiles_to_image."""

    def test_valid_smiles_returns_pil_image(self) -> None:
        """A valid SMILES should return a PIL Image of the requested size."""
        img = _smiles_to_image("CCO", width=200, height=150)
        assert isinstance(img, Image.Image)
        assert img.size == (200, 150)

    def test_invalid_smiles_raises_value_error(self) -> None:
        """An invalid SMILES should raise ValueError."""
        import pytest

        with pytest.raises(ValueError, match="could not parse"):
            _smiles_to_image("not_a_smiles_$$$$", width=200, height=150)
