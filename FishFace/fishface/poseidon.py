#!/usr/bin/env python

import os
import math

import hopper
import imageframe
import poser

try:
    import numpy as np
except ImportError:
    print "Poseidon requires numpy."
    raise


class Poseidon:
    """A batch processing object that handles various operations
    on lists or ranges of files/images."""

    def saveLeftFacingSilhouette(self, source, lineColor=(255, 0, 255), lineThickness=3, justOutline=True):

        chainProcessList = []

        if not justOutline:
            chainProcessList.append(('preserveArray', {}))

        if self.precropBox:
            chainProcessList.append(('crop', {'box': self.precropBox}))

        self.refreshPresets()
        chainProcessList.extend(self.presets['LARGEST_BLOB'])

        if self.DEBUG:
            chainProcessList.append(('onScreen', {}))

        HC = hopper.HopperChain(source, chainProcessList)

        for fr in HC:

            if fr.xdim + fr.ydim < 600:
                frgray = fr.copy()
                frgray.applyGrayImage()
                po = poser.Poser(frgray.array)

                axisAngle = po.findLongAxis()

                frleft = imageframe.Frame(po.rotate(-axisAngle))

                path = HC.chain[0].contents[HC.chain[0].cur]
                directory, filename = os.path.split(path)
                outpath = os.path.join(directory, "../output", "leftface-" + filename)
                frleft.saveImageToFile(outpath)

            else:
                print "skipped {}".format(fr.originalFileName)

    def extremaAnalysis(self, array, alsoReturnMinima=False):
                array = np.copy(array)
                array[array > 0] = 1

                perpSum = np.int32(np.sum(array, axis=0))
                deltas = np.diff(perpSum)

                minima = []
                maxima = []

                last_d = deltas[0]
                for d_enum in enumerate(deltas):
                    d = d_enum[1]
                    if math.copysign(1, d) > math.copysign(1, last_d):
                        # local minimum
                        minima.append([d_enum[0], perpSum[d_enum[0]]])

                    if math.copysign(1, d) < math.copysign(1, last_d):
                        # local maximum
                        maxima.append([d_enum[0], perpSum[d_enum[0]]])

                    # If we're not on a plateau or a flat valley,
                    # save d to last_d; otherwise, carry over the last_d
                    # to next time.
                    if d:
                        last_d = d

                if alsoReturnMinima:
                    return maxima, minima
                else:
                    return maxima

    def saveLargestBlobs(self, source, lineColor=(255, 0, 255), lineThickness=3, filledIn=True, justOutline=True):

        # FIXME: This logic would be better placed at the hopper or even imageframe level.

        chainProcessList = []

        if not justOutline:
            chainProcessList.append(('preserveArray', {}))

        if self.precropBox:
            chainProcessList.append(('crop', {'box': self.precropBox}))

        self.refreshPresets()
        chainProcessList.extend(self.presets['LARGEST_BLOB'])

        if self.DEBUG:
            chainProcessList.append(('onScreen', {}))

        HC = hopper.HopperChain(source, chainProcessList)

        for fr in HC:
            print "original filename: {}".format(fr.originalFileName)
            path = HC.chain[0].contents[HC.chain[0].cur]
            directory, filename = os.path.split(path)
            outpath = os.path.join(directory, "../output", "blob-" + filename)
            fr.saveImageToFile(outpath)

    def refreshPresets(self):

        # FIXME: This logic would be better placed at the hopper level.

        self.presets['LARGEST_BLOB'] = [
            ('deltaImage', {'calImageFrame': self.calImage}),
            ('grayImage', {}),
            ('threshold', {'threshold': 60}),
            ('closing', {'kernelRadius': 3}),
            ('opening', {'kernelRadius': 3}),
            ('cropToLargestBlob', {})
        ]

    def __init__(self):
        # FIXME: this is hard coded because it's valid for all the test data I have
        print "WARNING: Preprocessing crop box is hard coded!"
        self.precropBox = (107, 126, 1302, 1292)

        self.DEBUG = False

        self.calImage = None

        self.presets = dict()

# Definitions of custom exceptions


class ArrayInitError(Exception):
    pass


class ArrayProcessError(Exception):
    pass
