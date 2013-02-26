#!/usr/bin/env python

import imageframe
import os

class HopperChain:
    """An iterable that constructs a chain of Hopper objects to perform a specific
    set of image processing operations.  Each time HopperChain.next() is called,
    it returns the next frame from the last hopper in the chain."""

    def __init__(self, firstHopperInput, processList):
        self.chain = [Hopper(firstHopperInput)]

        if type(processList)!=list:
            raise HopperChainError("I need a list of processes (and their arguments) but I got a(n) {} instead.".format(type(processList)))
        else:
            for process in processList:
                if len(process)!=2:
                    raise HopperChainError("The processList must contain 2-element lists or tuples whose elements are the name of the process and its arguments.")
                else:
                    self.chain.append(Hopper(self.chain[-1]))
                    self.chain[-1].setProcess(process)

    def __iter__(self):
        return self

    def next(self):
        return self.chain[-1].next()
    

class Hopper:
    """An iterable that returns imageframe.Frame objects from files or another
    Hopper object."""
    def setProcess(self, process=None):
        if type(process)!=tuple or len(process)!=2 or type(process[0])!=str or type(process[1])!=dict:
            raise HopperError("I need a 2-tuple containing the string name of the process to apply and its args dictionary.")
        else:
            self.processName = process[0]
            self.processArgs = process[1]

    def processFrame(self):
        try:
            processes = {
                'canny' : self.frame.applyCanny,
                'closing' : self.frame.applyClosing,
                'crop' : self.frame.applyCrop,
                'cropToLargestBlob' : self.frame.applyCropToLargestBlob,
                'deltaImage' : self.frame.applyDeltaImage,
                'dilate' : self.frame.applyDilate,
                'erode' : self.frame.applyErode,
                'grayImage' : self.frame.applyGrayImage,
                'medianFilter' : self.frame.applyMedianFilter,
                'onScreen' : self.frame.onScreen,
                'opening' : self.frame.applyOpening,
                'preserveArray' : self.frame.preserveArray,
                'skeletonize' : self.frame.applySkeletonize,
                'threshold' : self.frame.applyThreshold
            }

            processes[self.processName](self.processArgs)
        except AttributeError:
            pass
    
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

class HopperChainError(Exception):
    pass

class HopperError(Exception):
    pass
