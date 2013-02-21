#!/usr/bin/env python

import copy
# import cv2

class Nugget:
    """A batch processing object that handles various operations
    on lists or ranges of files/images."""

    def shallowcopy(self):
        """Return a non-deep copy of this object."""
        return self.__copy__()

    def copy(self):
        """Return a deep copy of this object."""
        return self.__deepcopy__()
        
    def __copy__(self):
        """The actual implementation of the object shallowcopy() method.  Named so that
        the copy module can find it."""
        newNugget = Nugget(self.array, copyArray=False)
        newNugget.rots = self.rots
        return newNugget

    def __deepcopy__(self, memodic=None):
        """The actual implementation of the object copy() method.  Named so that
        the copy module can find it."""
        newNugget = Nugget(self.array, copyArray=True)
        newNugget.rots = copy.deepcopy(self.rots, memodic)
        return newNugget

    def __init__(self, array):
        pass

# Definitions of custom exceptions

class ArrayInitError(Exception):
    pass

class ArrayProcessError(Exception):
    pass
