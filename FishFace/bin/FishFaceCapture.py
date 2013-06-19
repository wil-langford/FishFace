#!/usr/bin/env python

"""
Fish Face Capture - data capture for FishFace


Example Usage
=============


"""

# import os
import sys
import argparse
import ueye
import imageframe
import time
import matplotlib.pyplot as plt

class FishFaceCaptureError(Exception):
    pass

def main(arguments):

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('outpath', type=str,
                        metavar="OUTPUT_PATH",
                        help='The path of the data files with a single string format replacement field.  For example, you could use "data/pic{}.jpg" for the path, and the {} would be replaced with the image number and the date/time stamp.',
                        action='store')
    parser.add_argument('-a', dest='startNum', type=int,
                        metavar="BATCH_START", default=1,
                        help='The first number to substitute into the input path.',
                        action='store',
                        required=False)
    parser.add_argument('-b', dest='stopNum', type=int,
                        metavar="BATCH_STOP", default=1,
                        help='The last number to substitute into the input path.',
                        action='store',
                        required=False)

    args = parser.parse_args(arguments)

    source = (args.outpath, args.startNum, args.stopNum)

    cam = ueye.Cam()
    if cam.ResetToDefault() != ueye.SUCCESS:
        #raise FishFaceCaptureError("Couldn't reset camera to defaults.")
        print "WARNING: Camera didn't confirm that we reset it to defaults, but this is apparently normal."
    if cam.SetColorMode(ueye.CM_BGR8_PACKED) != ueye.CM_BGR8_PACKED:
        raise FishFaceCaptureError("Couldn't set color mode to BGR8 (24 bit color, BGR).")
    if cam.SetColorCorrection(ueye.CCOR_DISABLE) != ueye.SUCCESS:
        raise FishFaceCaptureError("Couldn't disable color correction on camera.")
    
    if args.stopNum < args.startNum:
        raise FishFaceCaptureError("stopNum must be greater than or equal to startNum.")

    i = int(args.startNum)

    ar = cam.GrabImage()
    fr = imageframe.Frame(ar)

    while i <= args.stopNum:
        ar = cam.GrabImage()
        fr.setImage(ar)
        stamp = "{:08d}-{:010d}".format(i,int(time.time()))
        filename = args.outpath.format(stamp)
        fr.saveImageToFile(filename)
        i += 1
        time.sleep(1)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
