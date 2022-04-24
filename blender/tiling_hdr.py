import math
import sys
import os
import bpy
import numpy as np
import pathlib

argv = sys.argv
argv = argv[argv.index("--")+1:] 

if not len(argv):
    print("No file specified!")
    quit()

srcfile = argv[0]
img = bpy.data.images.load(srcfile)
img.colorspace_settings.name = "Linear"

path = os.path.abspath(os.path.join(srcfile, os.pardir))
name=os.path.splitext(os.path.basename(srcfile))[0]
dir = pathlib.Path(path).resolve()

rset = bpy.context.scene.render
#rset.use_border = True
#rset.use_crop_to_border = True
format = rset.image_settings

extension = "exr"
dim = 1024
format.file_format = "OPEN_EXR"
format.exr_codec = "DWAA"
format.color_mode = "RGB"
format.color_depth = '32'
format.compression = 100

level = math.ceil(math.log2(img.size[0] / dim))  
width = img.size[0]
height = img.size[1]
channels = img.channels


nt = bpy.context.scene.node_tree
node = nt.nodes["Image"]
node.image = img
trafo = nt.nodes["Transform"]

if img.file_format != "OPEN_EXR" and extension == "exr" :
    rset.resolution_x = width
    rset.resolution_y = height
    rset.filepath = "{}/{}.exr".format(dir, name)
    bpy.ops.render.render(write_still=True)

while level >= 0:
    level_dir = dir / name / str(level)
    level_dir.mkdir(parents=True, exist_ok=True)
    
    w = round(width)
    h = round(height)

    print("Level", level,w,h)
    
    max_y = math.ceil(h / dim) - 1
    trafo.inputs["Scale"].default_value = w / img.size[0]
    
    for iy in range(0, math.ceil(h / dim)):
        for ix in range(0,math.ceil(w / dim)):
        
            rset.resolution_x = min(dim, w - ix * dim)
            rset.resolution_y = min(dim, h - iy * dim)
            
            trafo.inputs["X"].default_value = max(w/2 - dim/2 - ix * dim, - w/2 + rset.resolution_x / 2)
            trafo.inputs["Y"].default_value = min(-h/2 + dim/2 + iy * dim, h/2 - rset.resolution_y / 2)
            
            
            #rset.border_max_x = min(w, (ix + 1) * dim) / w
            #rset.border_max_y = min(h, (iy + 1) * dim) / h
            
            #print(rset.border_min_x, rset.border_max_x, rset.border_min_y, rset.border_max_y)
            
            tile_path = "{}/{}_{}.{}".format(level_dir, ix, iy ,extension)
            rset.filepath = tile_path
            bpy.ops.render.render(write_still=True)  # Render!
        
    level -= 1
    width /= 2
    height /= 2
    #img.resize(round(width), round(height))