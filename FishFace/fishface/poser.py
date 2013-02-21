#!/usr/bin/env python

import copy

import numpy as np
from scipy import ndimage

### Both lines below do the same thing in the actual Python interpreter,
### but PyDev/Eclipse wants the second one for autocomplete and code
### analysis to work. 
# import cv
# import cv2.cv as cv
# import cv2

class Poser:
    def _rotate(self, degrees):
        """Use the scipy image rotation method on my array."""
        return ndimage.interpolation.rotate(self.array, degrees)

    def rotate(self, degrees):
        """Caching rotation finder.  Stores the result of each rotation to
        quickly retrieve it instead of recalculating if it's needed again."""
        if type(degrees) != int:
            raise ArrayProcessError("You tried to rotate by {} degrees, but only integer angles are supported for rotation at this time.".format(degrees))

        if not degrees in self.rots:
            self.rots[degrees] = self._rotate(degrees)

        return self.rots[degrees]

    def _horsum(self, arr=None):
        """Use numpy to sum along the horizontal axis of the provided array."""
        if arr==None:
            arr=self.array

        return np.sum(arr, axis=1)

    def horsum(self, degrees):
        """Caching horizontal sum finder.  Stores the result of each horizontal
        sum to quickly retrieve it instead of recalculating if it's needed
        again."""
        if type(degrees) != int:
            raise ArrayProcessError("Only integer angles are supported for horizontal sums at this time.")
         
        if not degrees in self.horsums:
            if not degrees in self.rots:
                self.rotate(degrees)
            self.horsums[degrees] = self._horsum(self.rots[degrees])

        return self.horsums[degrees]

    def findLongAxis(self, samples=10, iterations=2):

        #  Since we're just trying to find the angle of the axis with this
        #  method, 0-180 is sufficient.  We'll decide which direction the
        #  axis points later with analysis of the extrema.
        startAngle = 0
        stopAngle = 180

        for i in range(iterations):
            stepsize = int((stopAngle - startAngle)/samples)
            for angle in range(startAngle,stopAngle,stepsize):
                self.rotate(angle)
                self.horsum(angle)

            ks = list(self.horsums.keys())
            vs = [np.amax(hs) for hs in self.horsums.values()]
            max_length = max(vs)
            candidate = ks[vs.index(max_length)]


            ### FIXME: This doesn't handle the cases where the candidate
            ### window overlaps the 0/180 rotation.
            startAngle = max(0, candidate - stepsize)
            stopAngle = min(180, candidate + stepsize)
            
            # So I stop getting unused variable warnings.
            i += 0

        # The actual angle of the fish is the inverse of the candidate,
        # because we rotated the whole array and then measured along one axis.
        # Also, because at this point we only know a line parallel to the long
        # axis and not the orientation of that axis, 180 is as good as 360.
        return 180 - candidate


    
    def setArray(self, array, copyArray=True):
        # It's a numpy array. Store or copy it. 
        if(type(array)==np.ndarray):
            if copyArray:
                self.array = np.copy(array)
            else:
                self.array = array
        else:
            raise ArrayInitError("setArray requires a numpy array, but I see a {}".format(type(array)))

        self.shape = self.array.shape

        if len(self.shape) == 2:
            self.ydim = self.shape[0]
            self.xdim = self.shape[1]
        else:
            raise ArrayInitError("setArray requires a two-dimensional numpy array, but I see {} dimensions.".format(len(self.shape)))

    def shallowcopy(self):
        """Return a non-deep copy of this object."""
        return self.__copy__()

    def copy(self):
        """Return a deep copy of this object."""
        return self.__deepcopy__()
        
    def __copy__(self):
        """The actual implementation of the object shallowcopy() method.  Named so that
        the copy module can find it."""
        newPoser = Poser(self.array, copyArray=False)
        newPoser.rots = self.rots
        return newPoser

    def __deepcopy__(self, memodic=None):
        """The actual implementation of the object copy() method.  Named so that
        the copy module can find it."""
        newPoser = Poser(self.array, copyArray=True)
        newPoser.rots = copy.deepcopy(self.rots, memodic)
        return newPoser

    def __init__(self, array):
        self.setArray(array)
        self.rots = dict()
        self.horsums = dict()

# Definitions of custom exceptions

class ArrayInitError(Exception):
    pass

class ArrayProcessError(Exception):
    pass
