'''
    Trimetric Projector | Project a collection of faces (in SVG format)
 forming a cuboid net into trimetric/dimetric/isometric view
    Copyright (C) 2025  Yingbo Li

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import numpy as np
from numpy import cos,sin,tan
import re
import argparse

# Handle commandline args.
parser = argparse.ArgumentParser()
parser.add_argument("-a","--alpha",default=45,type=float,help="alpha angle (angle counterclockwise about the z axis), in degrees")
parser.add_argument("-g","--gamma",default=np.degrees(np.arctan(np.sqrt(2))),type=float,help="gamma angle (angle counterclockwise about the x axis), in degrees")
parser.add_argument("-o","--outfile",default="out.svg",type=str,help="path to save projected diagram")
args = parser.parse_args()
alpha = np.radians(args.alpha)
gamma = np.radians(args.gamma)

# All anchors are at top left of each side plane of the cuboid (so the y face requires a translation).
# Define the overall combined-rotation transformation (see `derivation/derivation.pdf` for details).
transform = np.array([[cos(alpha),sin(alpha),0],
                      [-sin(alpha)*cos(gamma),cos(alpha)*cos(gamma),sin(gamma)]])
# Define the transformations for each of the cuboid faces.
subtransform = lambda i_a,i_b : np.array([transform[:,i_a],transform[:,i_b]]).T
transform_x = subtransform(1,2)
transform_y = subtransform(0,2)
transform_z = subtransform(0,1)
t_dict = {"x":transform_x,
          "y":transform_y,
          "z":transform_z}

# Define formatting for combining a transformation for the cuboid face to project it onto the plane with a translation in the projected plane.
t_str = lambda t,translate : "matrix(" + ",".join(np.concatenate([t.T.flatten(),translate]).astype(str)) + ")"

# Identify the dimensions in each of the svg files (`x.svg`, `y.svg` and `z.svg`).
svg_dims = dict()
for p in t_dict:
    with open(p+".svg") as infile:
        svg = infile.read()
    svg_props = re.search(r"<svg[\S\s]+?>",svg).group(0)
    width = float(re.search(r"width=\"([0-9\.]+)",svg_props).group(1))
    height = float(re.search(r"height=\"([0-9\.]+)",svg_props).group(1))
    svg_dims[p] = (width,height)

# Start output svg with arbitrary header.
svg_out = ['<svg height="10mm" width="10mm">']
# Interate through each face of the cuboid.
for p,t in t_dict.items():
    with open(p+".svg") as infile:
        svg = infile.read()
    # Construct a toplevel group containing everything.
    defs_start = [m.start() for m in re.finditer(r"<defs[\S\s]+?/>",svg)][0]
    svg = svg[:defs_start] + "<g>" + svg[defs_start:]
    svg = svg.replace("</svg>","</g></svg>")
    # Identify the contents of the toplevel group (including the toplevel group tags).
    ## This could be simplified...
    group_starts = [m.start() for m in re.finditer("<g",svg)]
    group_ends = [m.end() for m in re.finditer("</g>",svg)]
    main_group = svg[group_starts[0]:group_ends[-1]]
    main_props = re.search(r"<g[\S\s]*?>",main_group).group(0)
    # Default to no translation after projection.
    translate = np.array([0,0])
    # If the active plane is the y plane, then a transformation does need applying (see `derivation/derivation.pdf` for details).
    if p=="y":
        translate = np.dot(transform_x,np.array([svg_dims["x"][0],0]))
    # Update the toplevel group with the projection transformation.
    transform_new = "transform=\"%s\"" % t_str(t,translate)
    main_props_repl = re.sub("transform=\".+?\"",transform_new,main_props)
    if "transform" not in main_props:
        main_props_repl = main_props[:-1] + " " + transform_new + ">"
    main_group = main_group.replace(main_props,main_props_repl)
    # Store the toplevel group contents to the output svg.
    svg_out.append(main_group)
# Close the output svg.
svg_out.append("</svg>")

# Save output svg.
outfile = args.outfile
if not outfile.endswith(".svg"):
    print("Appended .svg to outfile")
    outfile += ".svg"
with open(outfile,"w") as outfile:
    outfile.write("\n".join(svg_out))
