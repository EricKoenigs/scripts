#!/usr/bin/python2 
'''
Author: Eric Koenigs, HCI Heidelberg

Creates masks from the output of the LayerAnnotation tool.

Invoke with -h or --help for usage.
'''

import argparse
import os

from PIL import Image, ImageDraw
from xml.etree import ElementTree

# values for colors in 8bit PIL images
WHITE = 255
BLACK = 0

# ================================= [ Main ] ==================================

def main(args):
    '''Main routine.'''
    seq = ElementTree.parse(args.xmlfile)

    # get some relevant informations out of the xml
    folder = getelem(seq, "folder").text
    framenum = int(getelem(seq, "NumFrames").text)
    files = [f.text for f in getelem(seq, "fileList")]

    imagesize = Image.open(folder + files[0]).size

    masks = createmasks(imagesize, framenum)

    objects = list(seq.iter("object"))

    # draw all polugons onto the masks
    for obj in objects:
        frames = list(obj.iter("frame"))
        for frame in frames:
            index = int(getelem(frame, "index").text)
            polygon = createpolygon(getelem(frame, "polygon"))
            addpolygon(masks[index], polygon)

    # save masks
    maskfiles = ["mask_" + filename for filename in files]
    for mask in masks:
        mask.save(args.out + maskfiles.pop(0))

# =============================== [ Functions ] ===============================

def getelem(tree, elem, n = 0):
    '''Fetch the n-th element from the tree. Defaults to the first.'''
    e = [t for t in tree.iter(elem)]
    if len(e) == 0 or n >= len(e):
        return None
    else:
        #print(e[n].text)
        return e[n]

def createmasks(size, n = 1):
    '''Create a list of n equally sized, white images.'''
    masks = []
    for _ in range(n):
        masks.append(Image.new("L", size, WHITE))
    return masks

def createpolygon(polygon_elem):
    '''Create a list of (x, y) tuples representing a polygon from a
    polygon_elem.
    '''
    polygon = []
    for point in polygon_elem.iter("pt"):
        x = float(getelem(point, "x").text)
        y = float(getelem(point, "y").text)
        polygon.append((x, y))
    return polygon

def addpolygon(mask, polygon):
    '''Add a polygon to a mask.'''
    draw = ImageDraw.Draw(mask)
    draw.polygon(polygon, fill=BLACK)

# ============================== [ Invocation ] ===============================

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("xmlfile",
            help="a xmlfile produced by the LayerAnnotation tool")
    parser.add_argument("-o", "--out", metavar="folder",
            help="where to write the generated masks. Defaults to current "
            "directory.",
            default=".")

    args = parser.parse_args()

    # if the output folder was given without a trailing seperator, add it.
    if not args.out.endswith(os.sep):
        args.out += os.sep

    main(args)
