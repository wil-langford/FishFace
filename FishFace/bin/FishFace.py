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
    parser.add_argument('--line-thickness', dest='thickness', type=int,
                        metavar="THICKNESS", default=3,
                        help = 'How thick (in pixels) should lines be drawn.',
                        action='store')    
    parser.add_argument('--threshold-value', dest='threshold', type=int,
                        metavar="THRESHOLD", default=50,
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
    parser.add_argument('-O','--outline-foreground-object', dest='outline',
                        help = 'A command that outlines the foreground object.',
                        action='store_true')
    parser.add_argument('-Q','--supress-output', dest='quiet',
                        help = 'A command to supress all output for testing purposes.',
                        action='store_true')

    args = parser.parse_args(arguments)
    
    if args.outline:
        im_in = imageframe.Frame(args.infile)
        im_cal = imageframe.Frame(args.calfile)
        
        im_in.drawOutlineAroundLargestObject(calImageFrame=im_cal,
                                            threshold=args.threshold,
                                            kernelRadius=args.ksize,
                                            lineColor=args.color,
                                            lineThickness=args.thickness)

        if not args.quiet:        
            if args.outfile:
                im_in.saveImageToFile(args.outfile)
            else:
                im_in.onScreen(1, "Outlined largest object versus provided calibration image.")        
    

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))