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

from flask import Flask,render_template,request
import numpy as np
import json
from projector import project_svg_collection,write_svg
import os

app = Flask(__name__)
@app.route("/")
def init():
    return render_template("main.html")

@app.route("/project",methods=["POST"])
def project():
    args = request.json
    msg = ""
    svg = ""
    fs = [args["x_svg"],args["y_svg"],args["z_svg"]]
    success = 0
    file_absences = [(not os.path.exists(f)) for f in fs]
    if any(file_absences):
        msg = "One of the files provided does not exist: " + " ".join([f for i,f in enumerate(fs) if file_absences[i]])
    else:
        angles = [np.radians(float(args[x].strip())) for x in ["alpha","gamma"]]
        try:
            svg = project_svg_collection(*angles,*fs)
            write_svg(args["outfile"],svg)
            msg = "Saved to " + args["outfile"]
            success = 1
        except ValueError as e:
            msg = str(e)
    return json.dumps({"success":success,"svg":svg,"msg":msg})

if __name__=="__main__":
    app.run()
