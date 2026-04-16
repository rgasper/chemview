"""Tests for terminal graphics protocol detection and display."""

import os
from unittest.mock import patch

from chemview.terminal import GraphicsProtocol, detect_protocol


class TestDetectProtocol:
    """Tests for detect_protocol."""

    def test_detects_kitty_from_term_program(self) -> None:
        """Should detect Kitty when TERM_PROGRAM contains 'kitty'."""
        with patch.dict(os.environ, {"TERM_PROGRAM": "kitty"}, clear=False):
            assert detect_protocol() == GraphicsProtocol.KITTY

    def test_detects_kitty_from_term(self) -> None:
        """Should detect Kitty when TERM contains 'kitty'."""
        env = {"TERM": "xterm-kitty", "TERM_PROGRAM": ""}
        with patch.dict(os.environ, env, clear=False):
            assert detect_protocol() == GraphicsProtocol.KITTY

    def test_detects_wezterm_as_kitty(self) -> None:
        """WezTerm supports Kitty graphics protocol."""
        with patch.dict(os.environ, {"TERM_PROGRAM": "wezterm"}, clear=False):
            assert detect_protocol() == GraphicsProtocol.KITTY

    def test_detects_ghostty_as_kitty(self) -> None:
        """Ghostty supports Kitty graphics protocol."""
        with patch.dict(os.environ, {"TERM_PROGRAM": "ghostty"}, clear=False):
            assert detect_protocol() == GraphicsProtocol.KITTY

    def test_detects_sixel_from_term_program(self) -> None:
        """Should detect Sixel for known Sixel-capable terminals."""
        env = {"TERM_PROGRAM": "foot", "TERM": ""}
        with patch.dict(os.environ, env, clear=False):
            assert detect_protocol() == GraphicsProtocol.SIXEL

    def test_detects_sixel_from_env_var(self) -> None:
        """Should detect Sixel when SIXEL_SUPPORT=1 is set."""
        env = {"SIXEL_SUPPORT": "1", "TERM_PROGRAM": "", "TERM": ""}
        with patch.dict(os.environ, env, clear=False):
            assert detect_protocol() == GraphicsProtocol.SIXEL

    def test_returns_none_for_unknown_terminal(self) -> None:
        """Should return NONE for unrecognized terminals."""
        env = {
            "TERM_PROGRAM": "",
            "TERM": "dumb",
            "SIXEL_SUPPORT": "",
            "XTERM_VERSION": "",
        }
        with patch.dict(os.environ, env, clear=False):
            assert detect_protocol() == GraphicsProtocol.NONE
