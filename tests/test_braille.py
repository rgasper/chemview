"""Tests for braille rendering of PIL images."""

from PIL import Image

from chemview.braille import image_to_braille


class TestImageToBraille:
    """Tests for image_to_braille conversion."""

    def test_all_white_image_returns_empty_braille(self) -> None:
        """A fully white image should produce only blank braille chars (U+2800)."""
        img = Image.new("L", (4, 8), color=255)
        result = image_to_braille(img, columns=2)
        # 2 columns, 2 rows (8 pixels tall / 4 dots per row)
        lines = result.strip("\n").split("\n")
        assert len(lines) == 2
        assert all(ch == "\u2800" for line in lines for ch in line)

    def test_all_black_image_returns_full_braille(self) -> None:
        """A fully black image should produce full braille chars (U+28FF)."""
        img = Image.new("L", (4, 8), color=0)
        result = image_to_braille(img, columns=2)
        lines = result.strip("\n").split("\n")
        assert len(lines) == 2
        assert all(ch == "\u28ff" for line in lines for ch in line)

    def test_single_dot_top_left(self) -> None:
        """A single black pixel at (0,0) in a 2x4 block should set dot 1 (bit 0)."""
        img = Image.new("L", (2, 4), color=255)
        img.putpixel((0, 0), 0)
        result = image_to_braille(img, columns=1)
        lines = result.strip("\n").split("\n")
        assert len(lines) == 1
        assert lines[0] == "\u2801"  # dot 1 only

    def test_output_width_matches_columns(self) -> None:
        """Each output line should have exactly `columns` characters."""
        img = Image.new("L", (20, 16), color=128)
        result = image_to_braille(img, columns=10)
        lines = result.strip("\n").split("\n")
        for line in lines:
            assert len(line) == 10

    def test_rgb_image_is_handled(self) -> None:
        """An RGB image should be converted to grayscale internally."""
        img = Image.new("RGB", (4, 8), color=(0, 0, 0))
        result = image_to_braille(img, columns=2)
        lines = result.strip("\n").split("\n")
        assert all(ch == "\u28ff" for line in lines for ch in line)
