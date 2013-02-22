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
        self.contents = filenameList
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
    
    def next(self):
        if self.cur==None:
            self.cur=0
        else:
            self.cur = self.cur + 1
        
        if self.parentHopper:
            self.parentHopper.cur = self.cur - 1
            self.frame = self.parentHopper.next()
            self.processFrame()
        else:
            try:
                self.frame = imageframe.Frame(self.contents[self.cur])
                self.processFrame()
            except IndexError:
                raise StopIteration("End of the list.")
    
        return self.frame
    
    def __iter__(self):
        return self
            
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
            newHopper.contents = self.contents
        newHopper.cur = self.cur
        return newHopper

    def __deepcopy__(self, memodic=None):
        """The actual implementation of the object copy() method.  Named so that
        the copy module can find it."""
        newHopper = Hopper([])
        if self.parentHopper:
            newHopper.parentHopper = self.parentHopper
        else:
            newHopper.contents = copy.deepcopy(self.contents, memodic)
        newHopper.cur = self.cur
        return newHopper

class HopperError(Exception):
    pass