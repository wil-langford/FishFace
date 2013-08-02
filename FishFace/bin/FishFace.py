#!/usr/bin/env python

"""
Fish Face - for all your fish finding and orienting needs.


Example Usage
=============

python FishFace.py 'data/calimage-00000006-1234513565.jpg' \\
                   'data/fish_image-{}.jpg' \\
                    51 2783

Using the calibration image data/calimage-00000006-1234513565.jpg, process image
numbers 51 through 2783 of the format data/fish_image-NNNNNNNN-TTTTTTTTTT.jpg,
where the Ns represent the image serial number (i.e. 51 through 2783) and the Ts
represent a machine-readable timestamp.

"""

# system libraries
import os
import sys
import argparse

# add library directory to path
sys.path.append(os.path.join(os.path.dirname(sys.path[0]), "fishface"))

try:
    import poser
    import hopper
    import imageframe
except ImportError:
    print "Couldn't find FishFace libraries (poser.py, hopper.py, etc.)"
    raise

def main(arguments):

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('calFile', type=str,
                        metavar="CAL_FILENAME",
                        help='Specify the calibration image here.  The calibration image is the experimental image without a fish.  The difference between this image and images containing a fish is central to the current fish-finding algorithm.',
                        action='store')
    parser.add_argument('batchPath', type=str,
                        metavar="BATCH_PATH",
                        help='The path of the data files for batch processing with a single string format replacement field.  For example, if you had files pic0001.jpg through pic0031.jpg in the data directory, you could use "data/pic00{:02d}.jpg" or "data/pic{:04d}.jpg" for the path.',
                        action='store')
    parser.add_argument('startNum', type=int,
                        metavar="BATCH_START", default=1,
                        help='The first image number to process.',
                        action='store')
    parser.add_argument('stopNum', type=int,
                        metavar="BATCH_STOP", default=1,
                        help='The last image number to process.',
                        action='store')

    parser.add_argument('-o', '--output-file', dest='outfile', type=str,
                        metavar="OUTPUT_FILENAME",
                        help='To store the results in a file instead of printing them, specify a filename here.',
                        action='store')

    parser.add_argument('--crop-input-box', dest='crop_input_box', type=str,
                        metavar="CROP_INPUT_BOX", default=None,
                        help='The area of the input image to use.  Of the form "Y_MIN x X_MIN - Y_MAX x X_MAX. Example: "0x0 - 100x200" uses only the first 200 pixels of the first 100 rows of the image.',
                        action='store')

    parser.add_argument('--skip-threshold', dest='skipthresh', type=int,
                        metavar="SKIP_THRESHOLD", default=1000,
                        help='After cropping, if the sum of the fish silhouette''s bounding box dimensions is larger than this, skip the image.  Setting this lower reduces false positives in fish identification, but at the cost of potentially discarding valid images.',
                        action='store')
    parser.add_argument('--threshold-value', dest='threshold', type=int,
                        metavar="THRESHOLD", default=35,
                        help='During image difference processing, what should the threshold be for filtering out the parts of the image that are similar?',
                        action='store')
    parser.add_argument('--kernel-radius', dest='ksize', type=int,
                        metavar="KERNEL_RADIUS", default=3,
                        help='How large should our dilation/erosion kernel be when opening/closing?',
                        action='store')
#    parser.add_argument('--line-thickness', dest='thickness', type=int,
#                        metavar="THICKNESS", default=3,
#                        help = 'How thick (in pixels) should lines be drawn.',
#                        action='store')
#    parser.add_argument('--annotation-color', dest='color', type=tuple,
#                        metavar="RGB_COLOR", default=(255,0,255),
#                        help = 'An RGB 3-tuple specifying the color to draw annotations.',
#                        action='store')

    parser.add_argument('-Q', '--suppress-output', dest='quiet',
                        help='Suppress all output for testing purposes.',
                        action='store_true')

    args = parser.parse_args(arguments)

    source = (args.batchPath, args.startNum, args.stopNum)

    calFrame = imageframe.Frame(args.calFile)

    preCropBox = None
    chainProcessList = []

    if args.crop_input_box:
        mins, maxes = args.crop_input_box.split('-')
        mins = [int(x) for x in mins.split("x")]
        maxes = [int(x) for x in maxes.split("x")]
        preCropBox = (mins[0], mins[1], maxes[0], maxes[1])
        calFrame.applyCrop({'box': preCropBox})

    if preCropBox is not None:
        chainProcessList.append(('crop', {'box': preCropBox}))

    chainProcessList.extend([
        ('deltaImage', {'calImageFrame': calFrame}),
        ('grayImage', {}),
        ('threshold', {'threshold': args.threshold}),
        ('closing', {'kernelRadius': args.ksize}),
        ('opening', {'kernelRadius': args.ksize}),
        ('cropToLargestBlob', {})
    ])

    HC = hopper.HopperChain(source, chainProcessList)

    for fr in HC:

        if fr.xdim + fr.ydim < args.skipthresh:
            frgray = fr.copy()
            frgray.applyGrayImage()

            po = poser.Poser(frgray.array)
            angle = po.findLongAxis()

            po2 = poser.Poser(frgray.array)
            angle2 = po2.fastFindLongAxis()

            if args.outfile:
                with open(args.outfile, 'a') as f:
                    # f.write("{}: angle {}\n".format(fr.data['originalFileName'], angle))
                    f.write("{}: moment angle {}\n".format(fr.data['originalFileName'], angle2))
            else:
                # print "{}: angle {}".format(fr.data['originalFileName'], angle)
                # print "{}: moment angle {}".format(fr.data['originalFileName'], angle2)
                print "{} Angle diff: {}\tAngle: {}\tAngle2: {}".format(fr.data['originalFileName'], (angle-angle2+180)%360-180,angle,angle2)

        else:
            print "skipped {}".format(fr.data['originalFileName'])

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


class FishFaceCLIError(Exception):
    pass
