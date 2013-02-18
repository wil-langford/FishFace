#!/usr/bin/env python

import copy

import numpy as np
from scipy import ndimage

### Both lines below do the same thing in the actual Python interpreter,
### but PyDev/Eclipse wants the second one for autocomplete and code
### analysis to work. 
# import cv
import cv2.cv as cv
import cv2

class Poser:
    
    def setArray(self, array, copyArray=True):
        # It's a numpy array. Store or copy it. 
        if(type(array)==np.ndarray):
            if copyArray:
                self.array = np.copy(array)
            else:
                self.array = image
        else:
            raise ArrayInitError("setArray requires a numpy array, but I see a {}".format(type(image)))

        self.shape = self.array.shape

        if len(self.shape) == 2:
            self.ydim = self.spatialshape[0]
            self.xdim = self.spatialshape[1]
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
        return Poser(self.array, copyArray=False)

    def __deepcopy__(self, memodic=None):
        """The actual implementation of the object copy() method.  Named so that
        the copy module can find it."""
        return Poser(np.copy(self.array))

    def __init__(self, array):
        self.setArray(array)


# Definitions of custom exceptions

class ArrayInitError(Exception):
    pass

class ArrayProcessError(Exception):
    pass
