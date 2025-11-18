import numpy as np
from numpy import cos,sin,tan
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-a","--alpha",default=45,type=float,help="alpha angle (angle counterclockwise about the z axis), in degrees")
parser.add_argument("-g","--gamma",default=np.degrees(np.arctan(np.sqrt(2))),type=float,help="gamma angle (angle counterclockwise about the x axis), in degrees")

args = parser.parse_args()
alpha = np.radians(args.alpha)
gamma = np.radians(args.gamma)

# All anchors are at top left (so the y face requires a translation).
transform = np.array([[cos(alpha),sin(alpha),0],
                      [-sin(alpha)*cos(gamma),cos(alpha)*cos(gamma),sin(gamma)]])
subtransform = lambda i_a,i_b : np.array([transform[:,i_a],transform[:,i_b]]).T
transform_x = subtransform(1,2)
transform_y = subtransform(0,2)
transform_z = subtransform(0,1)

t_str = lambda t,translate : "matrix(" + ",".join(np.concatenate([t.T.flatten(),translate]).astype(str)) + ")"

t_dict = {"x":transform_x,
          "y":transform_y,
          "z":transform_z}

svg_dims = dict()
for p in t_dict:
    with open(p+".svg") as infile:
        svg = infile.read()
    svg_props = re.search(r"<svg[\S\s]+?>",svg).group(0)
    width = float(re.search(r"width=\"([0-9\.]+)",svg_props).group(1))
    height = float(re.search(r"height=\"([0-9\.]+)",svg_props).group(1))
    svg_dims[p] = (width,height)


svg_out = ['<svg height="100px" width="100px">']
for p,t in t_dict.items():
    with open(p+".svg") as infile:
        svg = infile.read()
    # Ensure everything is captured by a toplevel group.
    defs_start = [m.start() for m in re.finditer(r"<defs[\S\s]+?/>",svg)][0]
    svg = svg[:defs_start] + "<g>" + svg[defs_start:]
    svg = svg.replace("</svg>","</g></svg>")
    group_starts = [m.start() for m in re.finditer("<g",svg)]
    group_ends = [m.end() for m in re.finditer("</g>",svg)]
    main_group = svg[group_starts[0]:group_ends[-1]]
    main_props = re.search(r"<g[\S\s]*?>",main_group).group(0)
    translate = np.array([0,0])
    if p=="y":
        # Translate by the top right of the x face (i.e. translate the transformed point: transform_x . (y=width,z=0)
        translate = np.dot(transform_x,np.array([svg_dims["x"][0],0]))
    transform_new = "transform=\"%s\"" % t_str(t,translate)
    main_props_repl = re.sub("transform=\".+?\"",transform_new,main_props)
    if "transform" not in main_props:
        main_props_repl = main_props[:-1] + " " + transform_new + ">"
    main_group = main_group.replace(main_props,main_props_repl)
    svg_out.append(main_group)
svg_out.append("</svg>")
with open("out.svg","w") as outfile:
    outfile.write("\n".join(svg_out))
