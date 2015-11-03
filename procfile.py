import sys
import argparse as ap
import subprocess as sp
import os
import glob

import iris

sys.path.append("./image-service/")
from imageservice import procjob, imageproc

def proc_cube(cube, videoname):
    extent = [cube.coord("grid_longitude").points.min(),
              cube.coord("grid_longitude").points.max(),
              cube.coord("grid_latitude").points.min(),
              cube.coord("grid_latitude").points.max(),]
    for i, frt_cube in enumerate(cube.slices("time")):
        print "Processing timestep ", i, "...",
        img_array, proced_data = procjob.procDataToImage(frt_cube, "", ap.Namespace(extent=extent))
        print "Writing image"
        with open("data%03d.png" % i, "wb") as img:
            imageproc.writePng(img_array, img, nchannels=3, alpha=False)
    
    print "Writing video"
    sp.call(["avconv", "-y",
            "-r", "1", "-i", "data%03d.png",
            "-r", "1", "-vcodec", "libtheora", "-qscale:v", "2", videoname])
    print "Cleaning up"
    fs = glob.glob("./data???.png")
    for f in fs:
        os.remove(f)
        
if __name__=="__main__":
    varname = os.getenv("VAR_NAME")
    if varname != None:
        cube = iris.load_cube(os.getenv("FILE_IN"), iris.Constraint(varname))
    else:
        cube = iris.load_cube(os.getenv("FILE_IN"))
    proc_cube(cube, os.getenv("FILE_OUT"))