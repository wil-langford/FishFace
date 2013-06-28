#!/usr/bin/env python

"""
Fish Face - for all your fish finding and orienting needs.


Example Usage
=============


"""

# import os
import sys
import argparse
import poser
import hopper
import imageframe


def main(arguments):

    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-c', '--cal-image', dest='calFile', type=str,
                        metavar="CAL_FILENAME",
                        help='If you''re doing something that requires a calibration image, specify its filename here.',
                        action='store',
                        required=True)
    parser.add_argument('-i', '--input-path', dest='batchpath', type=str,
                        metavar="BATCH_PATH",
                        help='The path of the data files for batch processing with a single string format replacement field.  For example, if you had files pic0001.jpg through pic0031.jpg in the data directory, you could use "data/pic00{:02d}.jpg" or "data/pic{:04d}.jpg" for the path.',
                        action='store',
                        required=True)
    parser.add_argument('-o', '--output-file', dest='outfile', type=str,
                        metavar="OUTPUT_FILENAME",
                        help='To store the results in a file instead of printing them, specify a filename here.',
                        action='store')
    parser.add_argument('-a', dest='startNum', type=int,
                        metavar="BATCH_START", default=1,
                        help='The first number to substitute into the input path.',
                        action='store',
                        required=True)
    parser.add_argument('-b', dest='stopNum', type=int,
                        metavar="BATCH_START", default=1,
                        help='The last number to substitute into the input path.',
                        action='store',
                        required=True)

    parser.add_argument('--crop-input-box', dest='crop_input_box', type=str,
                        metavar="CROP_INPUT_BOX", default=None,
                        help='The area of the input image to use.  Of the form "Y_MIN x X_MIN - Y_MAX x X_MAX. Example: "0x0 - 100x200" uses only the first 200 pixels of the first 100 rows of the image.',
                        action='store')

    parser.add_argument('--skip-threshold', dest='skipthresh', type=int,
                        metavar="SKIP_THRESHOLD", default=600,
                        help='After cropping, if the sum of the fish silhouette''s bounding box dimensions is larger than this, skip the image.  Setting this lower reduces false positives in fish identification, but at the cost of potentially discarding valid images.',
                        action='store')
    parser.add_argument('--threshold-value', dest='threshold', type=int,
                        metavar="THRESHOLD", default=60,
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
                        help='A command to suppress all output for testing purposes.',
                        action='store_true')

    args = parser.parse_args(arguments)

    source = (args.batchpath, args.startNum, args.stopNum)

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

            if args.outfile:
                with open(args.outfile, 'a') as f:
                    f.write("{}: angle {}\n".format(fr.originalFileName, angle))
            else:
                print "{}: angle {}".format(fr.originalFileName, angle)

        else:
            print "skipped {}".format(fr.originalFileName)

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))


class FishFaceCLIError(Exception):
    pass
