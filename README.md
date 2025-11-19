# Usage

## GUI
Run `gui.py` to open a Flask browser application.

## CLI
```
usage: ./projector.py [-h] [-a ALPHA] [-g GAMMA] [-o OUTFILE]

  -h, --help            show this help message and exit
  -a ALPHA, --alpha ALPHA
                        alpha angle (angle counterclockwise about the z axis), in degrees
  -g GAMMA, --gamma GAMMA
                        gamma angle (angle counterclockwise about the x axis), in degrees
  -o OUTFILE, --outfile OUTFILE
                        path to save projected diagram
```

If no `-a` and `-g` are supplied, they will default to angles that result in an isometric view (45 and ~54.7 degrees, respectively). If this script is added to path, then the `./` at the start is not needed, otherwise this script can be run in this directory with the svg files copied here.

Each face of the cuboid net (see Figure 1 of `derivation/derivation.pdf`) must go up to the page margins exactly (i.e., no rounded corners from boundary/edge paths, which should be put on afterwards). The SVG files must be named `x.svg`, `y.svg` and `z.svg` where the axis label (e.g., `x`) is the axis that the face is normal to.

Tested for SVG files (including bitmaps-containing SVG) created and saved by Inkscape.

# Dependencies
Python packages CLI: `numpy`, `re`, `argparse`

Additional Python packages for GUI: `flask`, `json`, `os`
