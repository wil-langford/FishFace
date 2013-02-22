#!/usr/bin/env python

import copy
# import cv2

class Poseidon:
    """A batch processing object that handles various operations
    on lists or ranges of files/images."""

### FIXME: Everything from here to the ENDFIXME tag below is copied directly from
### imageframe.py and needs to be rewritten for Poseidon.

    def cropToLargestBlob(self, calImageFrame, threshold=50, kernelRadius=3, returnArray=False, lineColor=(255,0,255), lineThickness=3, filledIn=True):
        """Convenience method that crops the image to the largest object in it."""

        out = self.copy()
        
        out.deltaImage(calImageFrame)
        out.threshold(threshold)        
        ctr = out.findLargestBlobContours(kernelRadius=kernelRadius)
    
        out.setImage(out.blankImageCopy())    
        out.outlineLargestBlobWithContours(ctr, lineColor, lineThickness, filledIn)
                        
        out.applyCrop(out.boundingBoxFromContour(ctr))

        if returnArray:
            return out.array
        else:
            self.setImage(out.array)
            return None

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


    def shallowcopy(self):
        """Return a non-deep copy of this object."""
        return self.__copy__()

    def copy(self):
        """Return a deep copy of this object."""
        return self.__deepcopy__()
        
    def __copy__(self):
        """The actual implementation of the object shallowcopy() method.  Named so that
        the copy module can find it."""
        newPoseidon = Poseidon(self.array, copyArray=False)
        newPoseidon.rots = self.rots
        return newPoseidon

    def __deepcopy__(self, memodic=None):
        """The actual implementation of the object copy() method.  Named so that
        the copy module can find it."""
        newPoseidon = Poseidon(self.array, copyArray=True)
        newPoseidon.rots = copy.deepcopy(self.rots, memodic)
        return newPoseidon

    def __init__(self):
        pass

# Definitions of custom exceptions

class ArrayInitError(Exception):
    pass

class ArrayProcessError(Exception):
    pass
