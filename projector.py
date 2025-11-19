#!/usr/bin/env python3
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

class AxonometricProjector():
    def __init__(self,alpha,gamma):
        '''
        alpha | float | alpha angle in radians
        gamma | float | gamma angle in radians
        '''
        self.alpha = alpha
        self.gamma = gamma
        # All anchors are at top left of each side plane of the cuboid (so the y face requires a translation).
        # Define the overall combined-rotation transformation (see `derivation/derivation.pdf` for details).
        self.transform = np.array([[cos(alpha),sin(alpha),0],
                                   [-sin(alpha)*cos(gamma),cos(alpha)*cos(gamma),sin(gamma)]])
        # Define the transformations for each of the cuboid faces.
        subtransform = lambda i_a,i_b : np.array([self.transform[:,i_a],self.transform[:,i_b]]).T
        self.transform_x = subtransform(1,2)
        self.transform_y = subtransform(0,2)
        self.transform_z = subtransform(0,1)
        self.t_dict = {"x":self.transform_x,
                       "y":self.transform_y,
                       "z":self.transform_z}
        return
    def transform_xyz(self,xyz_vec):
        return np.dot(self.transform,xyz_vec)
    def compute_foreshortening(self):
        return np.linalg.norm(self.transform,axis=0)

class FaceCollection():
    def __init__(self,f_xface,f_yface,f_zface):
        self.f_map = {"x":f_xface,
                      "y":f_yface,
                      "z":f_zface}
        self.svgs = dict()
        for p,f in self.f_map.items():
            with open(f) as infile:
                svg = infile.read()
            self.svgs[p] = svg
        return
    def get_dimensions(self):
        # Identify the dimensions in each of the svg files (`x.svg`, `y.svg` and `z.svg`).
        svg_dims = dict()
        for p,svg in self.svgs.items():
            svg_props = re.search(r"<svg[\S\s]+?>",svg).group(0)
            width = float(re.search(r"width=\"([0-9\.]+)",svg_props).group(1))
            height = float(re.search(r"height=\"([0-9\.]+)",svg_props).group(1))
            svg_dims[p] = (width,height)
        return svg_dims
    def get_toplevel_contents(self):
        toplevel_content = dict()
        for p,svg in self.svgs.items():
            # Construct a toplevel group containing everything under the assumption that the start of the defs is the start of the actual SVG content.
            defs_start = [m.start() for m in re.finditer(r"<defs[\S\s]+?/>",svg)][0]
            # Isolate only the toplevel contents without the svg tags.
            main_group = svg[defs_start:].replace("</svg>","")
            toplevel_content[p] = main_group
        return toplevel_content

def format_t_matrix(t,translate):
    # Define formatting for combining a transformation for the cuboid face to project it onto the plane with a translation in the projected plane.
    t_str = "matrix(" + ",".join(np.concatenate([t.T.flatten(),translate]).astype(str)) + ")"
    return t_str

def project_svg_collection(alpha,gamma,f_xface,f_yface,f_zface):
    check_bad_angle = lambda ang : (ang < 0) or (ang > 90)
    if any([check_bad_angle(ang) for ang in [alpha,gamma]]):
        raise ValueError("Angles alpha and gamma must both be in the range [0,90] degrees.")
    proj = AxonometricProjector(alpha,gamma)
    faces = FaceCollection(f_xface,f_yface,f_zface)
    svg_dims = faces.get_dimensions()
    toplevel_content = faces.get_toplevel_contents()
    # Start output svg with arbitrary header.
    svg_out = ['<svg height="10mm" width="10mm">']
    # Interate through each face of the cuboid.
    for p,t in proj.t_dict.items():
        # Default to no translation after projection.
        translate = np.array([0,0])
        # If the active plane is the y plane, then a transformation does need applying (see `derivation/derivation.pdf` for details).
        if p=="y":
            translate = np.dot(proj.transform_x,np.array([svg_dims["x"][0],0]))
        # Construct toplevel group with the projection transformation matrix.
        t_str = format_t_matrix(t,translate)
        toplevel_group_header = '<g transform="%s" id="%s-face">' % (t_str,p)
        # Store the grouped toplevel contents to the output svg.
        svg_out.append(toplevel_group_header + toplevel_content[p] + "</g>")
    # Close the output svg.
    svg_out.append("</svg>")
    return "\n".join(svg_out)

def write_svg(outfile,svg):
    # Save svg to an output file.
    if not outfile.endswith(".svg"):
        print("Appended .svg to outfile")
        outfile += ".svg"
    with open(outfile,"w") as outfile:
        outfile.write(svg)
    return

if __name__=="__main__":
    # Handle commandline args.
    parser = argparse.ArgumentParser()
    parser.add_argument("-a","--alpha",default=45,type=float,help="alpha angle (angle counterclockwise about the z axis), in degrees")
    parser.add_argument("-g","--gamma",default=np.degrees(np.arctan(np.sqrt(2))),type=float,help="gamma angle (angle counterclockwise about the x axis), in degrees")
    parser.add_argument("-o","--outfile",default="out.svg",type=str,help="path to save projected diagram")
    args = parser.parse_args()
    alpha = np.radians(args.alpha)
    gamma = np.radians(args.gamma)
    outfile = args.outfile
    svg = project_svg_collection(alpha,gamma,"x.svg","y.svg","z.svg")
    write_svg(outfile,svg)
