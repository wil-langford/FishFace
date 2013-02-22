#!/usr/bin/env python

import copy
import imageframe
import os

class Hopper:
    """An iterable that returns Frame objects from files or a list of Frame objects."""
    
    def fillFromListOfFilenames(self, filenameList, directory=None):
        if directory:
            filenameList = [os.path.join(directory, filename)
                             for filename in filenameList]
        self.dict = dict(enumerate(filenameList))
        self.first = 0
        self.last = len(filenameList)-1
        self.parentHopper = None
    
    def fillWithGeneratedList(self, form, first, last, directory=None):
        filenameList = [form.format(n) for n in range(first, last+1)]
        self.fillFromListOfFilenames(filenameList,directory=directory)
    
    def __init__(self, origInput, directory=None):
        self.origInput = origInput
        if type(origInput)==list:
            self.fillFromListOfFilenames(origInput, directory)

        elif type(origInput)==tuple:
            if len(origInput)==2:
                first = 0
                form, last = origInput
            elif len(origInput)==3:
                form, first, last = origInput
            else:
                raise HopperError("If passing a tuple, it must be either (form, first, last) or (form, last).  I see a length {} tuple.".format(len(origInput)))
            
            self.fillWithGeneratedList(form, first, last, directory)
            
        elif isinstance(origInput,Hopper):
            self.parentHopper = origInput
            
        else:
            raise HopperError("I don't know how to fill myself from this {}.".format(type(origInput)))    
        
        self.cur = None
            
    def shallowcopy(self):
        """Return a non-deep copy of this object."""
        return self.__copy__()

    def copy(self):
        """Return a deep copy of this object."""
        return self.__deepcopy__()
        
    def __copy__(self):
        """The actual implementation of the object shallowcopy() method.  Named so that
        the copy module can find it."""
        newHopper = Hopper([])
        if self.parentHopper:
            newHopper.parentHopper = self.parentHopper
        else:
            newHopper.dict = self.dict
        newHopper.cur = self.cur
        return newHopper

    def __deepcopy__(self, memodic=None):
        """The actual implementation of the object copy() method.  Named so that
        the copy module can find it."""
        newHopper = Hopper([])
        if self.parentHopper:
            newHopper.parentHopper = self.parentHopper
        else:
            newHopper.dict = copy.deepcopy(self.dict, memodic)
        newHopper.cur = self.cur
        return newHopper

class HopperError(Exception):
    pass