#!/usr/bin/env python

"""
Fish Face - for all your fish finding and orienting needs.


Example Usage
=============


"""

# import os
import sys
import argparse
import imageframe
 
def main(arguments):
 
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-i','--input-image', dest='infile', type=str,
                        metavar="INPUT_FILENAME",
                        help = 'If we''re not running in batch processing mode, specify the filename of the input image here.',
                        action='store')
    parser.add_argument('-c','--cal-image', dest='calfile', type=str,
                        metavar="CAL_FILENAME",
                        help = 'If you''re doing something that requires a calibration image, specify its filename here.',
                        action='store')
    parser.add_argument('-o','--output-image', dest='outfile', type=str,
                        metavar="OUTPUT_FILENAME",
                        help = 'If you want to save the result, specify a filename here. If no file is specified, the results will be briefly displayed.',
                        action='store')

    parser.add_argument('-p','--batch-path', dest='batchpath', type=str,
                        metavar="BATCH_PATH",
                        help = 'The path of the data files for batch processing with a single string format replacement field.  For example, if you had files pic0001.jpg through pic0031.jpg in the data directory, you could use "data/pic00{:02d}.jpg" or "data/pic{:04d}.jpg" for the path.',
                        action='store')

    parser.add_argument('--line-thickness', dest='thickness', type=int,
                        metavar="THICKNESS", default=3,
                        help = 'How thick (in pixels) should lines be drawn.',
                        action='store')    
    parser.add_argument('--threshold-value', dest='threshold', type=int,
                        metavar="THRESHOLD", default=60,
                        help = 'During image difference processing, what should the threshold be for filtering out the parts of the image that are similar?',
                        action='store')    
    parser.add_argument('--kernel-radius', dest='ksize', type=int,
                        metavar="KERNEL_RADIUS", default=1,
                        help = 'How large should our dilation/erosion kernel be when opening/closing?',
                        action='store')    
    parser.add_argument('--annotation-color', dest='color', type=tuple,
                        metavar="RGB_COLOR", default=(255,0,255),
                        help = 'An RGB 3-tuple specifying the color to draw annotations.',
                        action='store')
    parser.add_argument('--crop-input-box', dest='crop_input_box', type=str,
                        metavar="CROP_INPUT_BOX", default=None,
                        help = 'The area of the input image to use.  Of the form "Y_MIN x X_MIN - Y_MAX x X_MAX. Example: "0x0 - 100x200" uses only the first 200 pixels of the first 100 rows of the image.',
                        action='store')

    parser.add_argument('-Q','--supress-output', dest='quiet',
                        help = 'A command to supress all output for testing purposes.',
                        action='store_true')


    parser.add_argument('-B','--batch-mode', dest='batch',
                        help = 'Engage batch mode.  Use with -a, -b, and -p arguments.',
                        action='store_true')
    parser.add_argument('-C','--crop-to-foreground-object', dest='crop',
                        help = 'A command that crops the image to the foreground object.',
                        action='store_true')
    parser.add_argument('-O','--outline-foreground-object', dest='outline',
                        help = 'A command that outlines the foreground object.',
                        action='store_true')

    args = parser.parse_args(arguments)

    if args.crop_input_box:
        mins,maxes = args.crop_input_box.split('-')
        mins = [int(x) for x in mins.split("x")]
        maxes = [int(x) for x in maxes.split("x")]
        crop_box = (mins[0], mins[1], maxes[0], maxes[1])

    if not args.batch:
        if args.crop:
            crop(args)

        if args.outline:
            outline(args)

def crop(args):
    im_in = imageframe.Frame(args.infile)
    im_cal = imageframe.Frame(args.calfile)

    if crop_box:
        im_in.crop(crop_box)
        im_cal.crop(crop_box)

    im_in.cropToLargestBlob(im_cal,
                            threshold=args.threshold,
                            kernelRadius=args.ksize,
                            lineColor=args.color,
                            lineThickness=args.thickness)

    if not args.quiet:        
        if args.outfile:
            im_in.saveImageToFile(args.outfile)
        else:
            im_in.onScreen(1, "Isolated largest object versus provided calibration image.")        
    
def outline(args):
    im_in = imageframe.Frame(args.infile)
    im_cal = imageframe.Frame(args.calfile)

    if crop_box:
        im_in.crop(crop_box)
        im_cal.crop(crop_box)
    
    im_in.drawOutlineAroundLargestBlob(calImageFrame=im_cal,
                                        threshold=args.threshold,
                                        kernelRadius=args.ksize,
                                        lineColor=args.color,
                                        lineThickness=args.thickness)

    if not args.quiet:        
        if args.outfile:
            im_in.saveImageToFile(args.outfile)
        else:
            im_in.onScreen(2, "Outlined largest object versus provided calibration image.")        
    

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
