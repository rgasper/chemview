# chemview

CLI for visualizing SMILES strings as 2D molecule images using RDKit.

## Setup

Requires [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

```bash
# render and open a molecule (writes to /tmp, opens in default viewer)
uv run chemview "CCO"

# benzene, custom dimensions
uv run chemview "c1ccccc1" --width 600 --height 400

# save to a specific file instead of opening
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
