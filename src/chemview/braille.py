"""Convert PIL images to Unicode braille art for terminal display.

Braille characters (U+2800-U+28FF) encode a 2-wide x 4-tall dot grid.
The dot numbering and corresponding bit positions are:

    (0,0)=bit0  (1,0)=bit3
    (0,1)=bit1  (1,1)=bit4
    (0,2)=bit2  (1,2)=bit5
    (0,3)=bit6  (1,3)=bit7

A threshold is applied to decide whether each pixel is "on" (dark) or "off"
(light), and the bits are OR-ed together to form the codepoint offset from
U+2800.
"""

from PIL import Image

# Bit position for each (dx, dy) offset within a 2x4 braille cell.
_BRAILLE_DOT_BITS: dict[tuple[int, int], int] = {
    (0, 0): 0x01,
    (0, 1): 0x02,
    (0, 2): 0x04,
    (1, 0): 0x08,
    (1, 1): 0x10,
    (1, 2): 0x20,
    (0, 3): 0x40,
    (1, 3): 0x80,
}

_BRAILLE_BASE: int = 0x2800
_DEFAULT_THRESHOLD: int = 128


def image_to_braille(
    img: Image.Image,
    columns: int = 80,
    threshold: int = _DEFAULT_THRESHOLD,
) -> str:
    """Convert a PIL Image to a Unicode braille string.

    The image is resized so its width maps to ``columns`` braille characters
    (each 2 pixels wide) and the height scales proportionally (rounded up to
    a multiple of 4 so every row is complete).

    Args:
        img: Source image (any mode - converted to grayscale internally).
        columns: Number of braille characters per output line.
        threshold: Grayscale value below which a pixel is considered "on"
            (dark). Range 0-255, default 128.

    Returns:
        A multi-line string of braille characters, one ``\\n`` per row.

    Example:
        >>> from PIL import Image
        >>> img = Image.new("L", (4, 8), color=0)
        >>> print(image_to_braille(img, columns=2))
        ⣿⣿
        ⣿⣿
    """
    if columns <= 0:
        raise ValueError(f"columns must be positive, got {columns}")
    if not (0 <= threshold <= 255):
        raise ValueError(f"threshold must be in 0-255, got {threshold}")

    gray = img.convert("L")

    pixel_w = columns * 2
    scale = pixel_w / gray.width
    pixel_h = int(gray.height * scale)
    # Round height up to a multiple of 4.
    pixel_h += (4 - pixel_h % 4) % 4

    gray = gray.resize((pixel_w, pixel_h), Image.Resampling.LANCZOS)
    pixels = gray.load()
    assert pixels is not None, "Failed to load pixel access for grayscale image"

    rows: list[str] = []
    for cell_y in range(0, pixel_h, 4):
        row_chars: list[str] = []
        for cell_x in range(0, pixel_w, 2):
            code = 0
            for (dx, dy), bit in _BRAILLE_DOT_BITS.items():
                px = cell_x + dx
                py = cell_y + dy
                if pixels[px, py] < threshold:
                    code |= bit
            row_chars.append(chr(_BRAILLE_BASE + code))
        rows.append("".join(row_chars))

    return "\n".join(rows) + "\n"
