# chemview

CLI for visualizing SMILES strings as 2D molecule images using RDKit.

<video src="caffeine.mov" autoplay loop muted playsinline></video>

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

By default, images are displayed inline in the terminal using the Kitty or
Sixel graphics protocol. If your terminal doesn't support either, chemview
falls back to opening the image in your system viewer.

```bash
# render a molecule inline in the terminal
uv run chemview "CCO"

# benzene, custom dimensions
uv run chemview "c1ccccc1" --width 600 --height 400

# save to a specific file instead of displaying
uv run chemview "CC(=O)Oc1ccccc1C(=O)O" -o aspirin.png
```

Run `uv run chemview --help` for all options.

## Global install

To make `chemview` available from anywhere on your system:

```bash
# editable — stays linked to source, code changes take effect immediately
uv tool install -e .

# or, frozen copy — requires re-install to pick up changes
uv tool install .
```

Then just run `chemview "CCO"` from any directory.

To uninstall: `uv tool uninstall chemview`.
