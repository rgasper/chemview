"""Display images inline in the terminal via Kitty or Sixel graphics protocols.

Detection order:
    1. Kitty graphics protocol (TERM_PROGRAM=kitty or TERM contains "kitty")
    2. Sixel (TERM_PROGRAM in known sixel-capable terminals, or SIXEL_SUPPORT env)
    3. None — caller should fall back to opening with system viewer.

The Kitty protocol sends PNG data as base64-encoded chunks inside APC escape
sequences. Sixel converts the image to the Sixel bitmap format and writes it
directly to stdout.
"""

from __future__ import annotations

import base64
import io
import os
import sys
from enum import Enum, auto
from typing import TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    from PIL import Image


class GraphicsProtocol(Enum):
    """Supported terminal graphics protocols."""

    KITTY = auto()
    SIXEL = auto()
    NONE = auto()


def detect_protocol() -> GraphicsProtocol:
    """Detect which terminal graphics protocol is available.

    Checks environment variables to determine the running terminal emulator
    and returns the best available graphics protocol.

    Returns:
        The detected graphics protocol, or ``NONE`` if no inline image
        protocol is available.

    Example:
        >>> protocol = detect_protocol()
        >>> protocol
        GraphicsProtocol.KITTY
    """
    term_program = os.environ.get("TERM_PROGRAM", "").lower()
    term = os.environ.get("TERM", "").lower()

    # Kitty graphics protocol
    if "kitty" in term_program or "kitty" in term:
        logger.debug("Detected Kitty graphics protocol")
        return GraphicsProtocol.KITTY

    # Terminals known to support Kitty protocol
    kitty_capable = {"wezterm", "ghostty", "konsole"}
    if term_program in kitty_capable:
        logger.debug("Detected Kitty-capable terminal: {}", term_program)
        return GraphicsProtocol.KITTY

    # Sixel support — check for known sixel-capable terminals or explicit env
    sixel_capable = {"iterm2", "iterm.app", "mintty", "foot", "mlterm"}
    if term_program in sixel_capable:
        logger.debug("Detected Sixel-capable terminal: {}", term_program)
        return GraphicsProtocol.SIXEL

    if os.environ.get("SIXEL_SUPPORT", "") == "1":
        logger.debug("Detected Sixel support via SIXEL_SUPPORT env var")
        return GraphicsProtocol.SIXEL

    # xterm with sixel support
    if "xterm" in term and os.environ.get("XTERM_VERSION", ""):
        logger.debug("Detected xterm, assuming Sixel support")
        return GraphicsProtocol.SIXEL

    logger.debug("No terminal graphics protocol detected")
    return GraphicsProtocol.NONE


def display_kitty(img: Image.Image) -> None:
    """Display a PIL Image inline using the Kitty graphics protocol.

    The image is encoded as PNG and sent in base64 chunks via APC escape
    sequences.

    Args:
        img: The PIL Image to display.

    Example:
        >>> from PIL import Image
        >>> img = Image.new("RGB", (100, 100), "red")
        >>> display_kitty(img)  # image appears inline in Kitty terminal
    """
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.standard_b64encode(buf.getvalue()).decode("ascii")

    chunk_size = 4096
    chunks = [b64[i : i + chunk_size] for i in range(0, len(b64), chunk_size)]

    write = sys.stdout.write
    for i, chunk in enumerate(chunks):
        is_last = i == len(chunks) - 1
        if i == 0:
            header = f"\033_Ga=T,f=100,t=d,m={'0' if is_last else '1'};"
        else:
            header = f"\033_Gm={'0' if is_last else '1'};"
        write(header + chunk + "\033\\")

    write("\n")
    sys.stdout.flush()


def display_sixel(img: Image.Image) -> None:
    """Display a PIL Image inline using the Sixel graphics protocol.

    The image is quantized to 256 colors and converted to Sixel format.
    Sixel encodes rows of 6 pixels at a time, with each column represented
    as a character offset from '?' (0x3F).

    Args:
        img: The PIL Image to display.

    Example:
        >>> from PIL import Image
        >>> img = Image.new("RGB", (100, 100), "blue")
        >>> display_sixel(img)  # image appears inline in Sixel-capable terminal
    """
    # Quantize to 256 colors max for sixel
    rgb = img.convert("RGB")
    quantized = rgb.quantize(colors=256)
    palette = quantized.getpalette()
    if palette is None:
        logger.warning("Failed to quantize image for Sixel output")
        return

    width, height = quantized.size
    pixels = quantized.load()
    if pixels is None:
        logger.warning("Failed to load pixel data for Sixel output")
        return

    # Count actual colors used
    num_colors = len(palette) // 3

    write = sys.stdout.write

    # Sixel start: DCS q
    write("\033Pq\n")

    # Define color palette: #index;2;r%;g%;b%
    for i in range(num_colors):
        r = palette[i * 3] * 100 // 255
        g = palette[i * 3 + 1] * 100 // 255
        b = palette[i * 3 + 2] * 100 // 255
        write(f"#{i};2;{r};{g};{b}")

    # Encode pixel data in bands of 6 rows
    for band_top in range(0, height, 6):
        for color_idx in range(num_colors):
            # Check if this color is used in this band
            has_pixel = False
            for y in range(band_top, min(band_top + 6, height)):
                for x in range(width):
                    if pixels[x, y] == color_idx:
                        has_pixel = True
                        break
                if has_pixel:
                    break

            if not has_pixel:
                continue

            # Select color
            write(f"#{color_idx}")

            # Encode each column in this band for this color
            for x in range(width):
                sixel_val = 0
                for dy in range(6):
                    y = band_top + dy
                    if y < height and pixels[x, y] == color_idx:
                        sixel_val |= 1 << dy
                write(chr(0x3F + sixel_val))

        # End of band (newline in sixel = $-)
        write("$-")

    # Sixel end: ST
    write("\033\\")
    write("\n")
    sys.stdout.flush()


def display_image(img: Image.Image) -> bool:
    """Try to display an image inline in the terminal.

    Detects the available graphics protocol and uses it. Returns whether
    display was successful.

    Args:
        img: The PIL Image to display.

    Returns:
        True if the image was displayed inline, False if no protocol is
        available and the caller should fall back to another method.

    Example:
        >>> from PIL import Image
        >>> img = Image.new("RGB", (100, 100), "green")
        >>> displayed = display_image(img)
    """
    protocol = detect_protocol()

    if protocol == GraphicsProtocol.KITTY:
        display_kitty(img)
        return True

    if protocol == GraphicsProtocol.SIXEL:
        display_sixel(img)
        return True

    return False
