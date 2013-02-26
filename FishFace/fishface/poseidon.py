#!/usr/bin/env python

import hopper
import imageframe
import poser
import cv2
import os
import numpy as np
import math

class Poseidon:
    """A batch processing object that handles various operations
    on lists or ranges of files/images."""

    def saveHorizontalSilhouette(self, source, lineColor=(255,0,255), lineThickness=3):
 
        HC = hopper.HopperChain(source, [('null',{})])
        
        for fr in HC:
            
            if fr.xdim + fr.ydim <600:
                frgray = fr.copy()
                frgray.applyGrayImage()
                po = poser.Poser(frgray.array)
                
                axisAngle = po.findLongAxis()
    
                # cv2.line(fr.array, (50,50), (int(40*math.sin(axisAngle)),int(40*math.cos(axisAngle))), lineColor)
                
                frhor = imageframe.Frame(po.rotate(-axisAngle))
                # frgray.onScreen({'msg':"angle {}".format(axisAngle)})

                path = HC.chain[0].contents[HC.chain[0].cur]
                directory, filename = os.path.split(path)
                outpath = os.path.join(directory, "../horizontal","hor-" + filename)
                frhor.saveImageToFile(outpath)
                
            else:
                print "skipped {}".format(fr.originalFilename)

    def saveLargestBlobs(self, source, lineColor=(255,0,255), lineThickness=3, filledIn=True, justOutline=True):

        # FIXME: This logic would be better placed at the hopper level.

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
            print "original filename: {}".format(fr.originalFilename)
            path = HC.chain[0].contents[HC.chain[0].cur]
            directory, filename = os.path.split(path)
            outpath = os.path.join(directory, "../output", "blob-" + filename)
            fr.saveImageToFile(outpath)

    def refreshPresets(self):

        # FIXME: This logic would be better placed at the hopper level.

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

        self.DEBUG=False

        self.calImage = None

        self.presets=dict()

# Definitions of custom exceptions

class ArrayInitError(Exception):
    pass

class ArrayProcessError(Exception):
    pass
