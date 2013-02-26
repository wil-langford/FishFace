#!/usr/bin/env python

import hopper
import imageframe
import cv2
import os

class Poseidon:
    """A batch processing object that handles various operations
    on lists or ranges of files/images."""

### FIXME: Everything from here to the ENDFIXME tag below is copied directly from
### imageframe.py and needs to be rewritten for Poseidon.

    def cropToLargestBlob(self, source, lineColor=(255,0,255), lineThickness=3, filledIn=True, justOutline=True):

        chainProcessList = []

        if not justOutline:
            chainProcessList.append(('preserveArray', {}))

        if self.precropBox:
            chainProcessList.append(('crop', {'box':self.precropBox}))

        self.refreshPresets()
        chainProcessList.extend(self.presets['LARGEST_BLOB'])

        if self.DEBUG:
            chainProcessList.append(('onScreen',{}))

        HC = hopper.HopperChain(source, chainProcessList)

        for fr in HC:
            path = HC.chain[0].contents[HC.chain[0].cur]
            directory, filename = os.path.split(path)
            outpath = os.path.join(directory, "../output", "blob-" + filename)
            fr.saveImageToFile(outpath)



    def drawOutlineAroundLargestBlob(self, calImageFrame, threshold=50, kernelRadius=3, lineColor=(255,0,255), lineThickness=3, filledIn=True):
        """Convenience method that finds the contours of the largest object
        and then draws them onto the image."""
        child = self.copy()
        
        child.deltaImage(calImageFrame)
        child.threshold(threshold)
        
        self.outlineLargestBlobWithContours(
                    child.findLargestBlobContours(kernelRadius=kernelRadius),
                    lineColor, lineThickness, filledIn)

    def findLargestBlobContour(self, kernelRadius=3, iterClosing=3, iterOpening=3):
        """Returns a list of lists.  Each element of the list is a single contour,
        and the elements of each contour are the ordered coordinates of the contour."""
        # I'm creating a temporary Frame because this isn't an apply* method.
        temp = self.copy()

        temp.applyClosing(kernelRadius=kernelRadius, iterations=iterClosing)
        temp.applyOpening(kernelRadius=kernelRadius, iterations=iterOpening)
        
        contours = temp.allContours(args)
        areas = [cv2.contourArea(ctr) for ctr in contours]
        max_contour = [contours[areas.index(max(areas))]]

        return max_contour

### ENDFIXME

    def refreshPresets(self):
        self.presets['LARGEST_BLOB']=[
            ('deltaImage', {'calImageFrame':self.calImage}),
            ('grayImage', {}),
            ('threshold',{'threshold':60}),
            ('closing',{'kernelRadius':3}),
            ('opening',{'kernelRadius':3}),
            ('cropToLargestBlob',{})
            ]


    def __init__(self):
        # FIXME: this is hard coded becuase it's valid for all the test data
        self.precropBox = (107,126,1302,1292)

        self.DEBUG=True

        self.calImage = None

        self.presets=dict()

# Definitions of custom exceptions

class ArrayInitError(Exception):
    pass

class ArrayProcessError(Exception):
    pass
