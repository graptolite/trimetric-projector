# Usage
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

Each face of the cuboid net (see Figure 1 of `derivation/derivation.pdf`) must go up to the page margins exactly (i.e., no rounded corners from boundary/edge paths, which should be put on afterwards). The SVG files must be named `x.svg`, `y.svg` and `z.svg` where the axis label (e.g., `x`) is the axis that the face is normal to.

Tested for SVG files (including bitmaps-containing SVG) created and saved by Inkscape.
