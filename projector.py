import numpy as np
from numpy import cos,sin,tan
import re

gamma = np.radians(30)
alpha = np.radians(40)

transform = np.array([[cos(gamma),sin(gamma),0],
                      [-sin(gamma)*cos(alpha),cos(gamma)*cos(alpha),sin(alpha)]])
subtransform = lambda i_a,i_b : np.array([transform[:,i_a],transform[:,i_b]]).T
transform_x = subtransform(1,2)
transform_y = subtransform(0,2)
transform_z = subtransform(0,1)

t_str = lambda t,translate : "matrix(" + ",".join(np.concatenate([t.T.flatten(),translate]).astype(str)) + ")"

t_dict = {"x":transform_x,
          "y":transform_y,
          "z":transform_z}

translate_dict = dict()
groups_dict = dict()
props_dict = dict()

svg_out = ['<svg height="100px" width="100px">']
for p in t_dict:
    with open(p+".svg") as infile:
        svg = infile.read()
    group_starts = [m.start() for m in re.finditer("<g",svg)]
    group_ends = [m.end() for m in re.finditer("</g>",svg)]
    main_group = svg[group_starts[0]:group_ends[-1]]
    main_props = re.search("<g[\S\s]+?>",main_group).group(0)
    translate = re.search("transform=\"(.+?)\"",main_props).group(1)
    groups_dict[p] = main_group
    props_dict[p] = main_props
    translate_dict[p] = translate

for p,t in t_dict.items():
    main_group = groups_dict[p]
    main_props = props_dict[p]
    translate = translate_dict[p]
    if p == "y":
        translate_z = np.array(translate_dict["z"].split("(")[1].split(")")[0].split(",")).astype(float)
        translate_y = np.array(translate_dict["y"].split("(")[1].split(")")[0].split(",")).astype(float)
        t_y = np.dot(transform_y,translate_y)
        t_z = np.dot(transform_z,translate_z)
        translate = t_y+t_z
        main_props_repl = re.sub("transform=\".+?\"","transform=\"%s\"" % t_str(t,translate),main_props)
    else:
        main_props_repl = re.sub("transform=\".+?\"","transform=\"%s,%s\"" % (t_str(t,np.array([0,0])),translate),main_props)
    main_group = main_group.replace(main_props,main_props_repl)
    svg_out.append(main_group)
svg_out.append("</svg>")
with open("out.svg","w") as outfile:
    outfile.write("\n".join(svg_out))
