#!/usr/bin/env python

import copy
import Tkinter as tk
import math

try:
    import numpy as np
    from scipy import ndimage
except ImportError:
    print "The poser module requires, numpy, scipy, and PIL."
    raise

try:
    import cv2
except ImportError:
    print "The imageframe module needs OpenCV."
    raise


class Poser:

    def momentLongAxis(self):
        mu00 = self.moms['m00']
        mu20p = self.moms['mu20'] / mu00
        mu02p = self.moms['mu02'] / mu00
        mu11p = self.moms['mu11'] / mu00
        if mu11p == 0:
            return False
        else:
            return math.degrees(0.5 * math.atan((2*mu11p)/(mu20p - mu02p)))

    def fastFindLongAxis(self):

        offset = int(self.momentLongAxis())

        for candidate in range(0,360,90):
            candidate = (candidate - offset) % 360

            self.rotate(candidate)
            self.horsum(candidate)

        # find the keys for each of the horizontal sum arrays
        ks = list(self.horsums.keys())

        # find the maximum value from each horizontal sum array
        vs = [np.amax(hs) for hs in self.horsums.values()]

        # and the maximum value of all of those maximums
        max_length = max(vs)

        # and the candidate will be the angle that produces that
        # maximum value
        angle = ks[vs.index(max_length)]

        # rotate the current imageframe to the found angle and store it in frhor
        frhor = self.rotate(angle)

        # find the horizontal middle of the candidate-rotated image
        mid_x = int(frhor.shape[1] / 2)

        # find the sum of pixels on each side of that horizontal middle
        leftsum = np.sum(frhor[:, :mid_x])
        rightsum = np.sum(frhor[:, mid_x:])

        # if the leftsum is less than the rightsum, then the fish is facing
        # right and not left.  Rotate it 180 degrees so it faces left.
        if leftsum < rightsum:
            angle = angle + 180 % 360

        # let's make extra sure we have a stored rotation at the angle
        self.rotate(angle)

        # The actual angle of the fish is the inverse of the candidate,
        # because we rotated the whole array and then measured along one axis.
        return int((-angle) % 360)


    def findLongAxis(self, samples=10, iterations=3):

        #  Since we're just trying to find the angle of the axis with this
        #  method, 0-180 is sufficient.  We'll decide which direction the
        #  axis points later.

        #  Having said that, I'm going to take the cheap way out to fix the
        #  overlap case (where the candidate angle is near zero) by extending
        #  the stopAngle by several steps and only considering the candidates
        #  in the "middle" 180 degrees.

        startAngle = 0
        stopAngle = 180 + (int(180 / samples) * 4)

        # iterations to refine the angle - we just care how many, not
        # what iteration we're actually on
        for dummy in range(iterations):
            stepsize = int((stopAngle - startAngle) / samples)
            stepsize = max(stepsize,1)
            # for each of the candidate angles, compute the rotated picture
            # and the horizontal sums for each line of the rotated picture
            for angle in range(startAngle, stopAngle, stepsize):
                self.rotate(angle)
                self.horsum(angle)

            # find the keys for each of the horizontal sum arrays
            ks = list(self.horsums.keys())
            # find the maximum value from each horizontal sum array
            vs = [np.amax(hs) for hs in self.horsums.values()]
            # and the maximum value of all of those maximums
            max_length = max(vs[2:-2])
            # and the candidate will be the angle that produces that
            # maximum value
            candidate = ks[vs.index(max_length)]

            # at the next iteration, we'll start one stepsize before and
            # end one stepsize after the current candidate, and repartition
            # this new range with a new stepsize when the next iteration hits
            startAngle = max(0, candidate - stepsize)
            stopAngle = min(180 + (4 * stepsize), candidate + stepsize)

        # after the specified number of iterations, we will rotate the
        # current imageframe to the candidate angle
        frhor = self.rotate(candidate)

        # find the horizontal middle of the candidate-rotated image
        mid_x = int(frhor.shape[1] / 2)

        # find the sum of pixels on each side of that horizontal middle
        leftsum = np.sum(frhor[:, :mid_x])
        rightsum = np.sum(frhor[:, mid_x:])

        # if the leftsum is less than the rightsum, then the fish is facing
        # right and not left.  Rotate it 180 degrees so it faces left.
        if leftsum < rightsum:
            candidate = candidate + 180 % 360

        self.rotate(candidate)

        # The actual angle of the fish is the inverse of the candidate,
        # because we rotated the whole array and then measured along one axis.
        # This is tuned to spit out values in the half-open interval [-180,180),
        # where 0 is toward the right side of the image.
        return int((-candidate) % 360) - 180

    def _rotate(self, degrees):
        """Use the scipy image rotation method on my array."""
        im = ndimage.interpolation.rotate(self.array, degrees % 360)
        cv2.threshold(src=im, dst=im, thresh=128, maxval=255, type=cv2.THRESH_BINARY)
        return im

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
        if arr is None:
            arr = self.array

        return np.sum(arr, axis=1) / 255

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

    def onScreen(self, degrees=None, scaleFactor=1):
        """I need something to display these things for debugging. This uses
        OpenCV to display in a no-frills, any-key-to-dismiss window."""

        if degrees:
            im = Image.fromarray(self.rotate(degrees))
            msg = "{} degree rotation - any key/click to continue".format(degrees)
        else:
            im = Image.fromarray(self.array)
            msg = "any key/click to continue"

        caption = "image display - any key to close"

        cv2.namedWindow(caption, 0)
        shape = im.shape
        width = int(shape[1] * scaleFactor)
        height = int(shape[0] * scaleFactor)

        cv2.resizeWindow(caption, width, height)
        # cv2.setMouseCallback(caption, kill_window)
        
        cv2.imshow(caption, im)
        cv2.startWindowThread()
        cv2.waitKey(0)
        cv2.destroyWindow(caption)


    def setArray(self, array, copyArray=True):
        # It's a numpy array. Store or copy it.
        if(type(array) == np.ndarray):
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

        cv2.threshold(src=self.array, dst=self.array, thresh=128, maxval=255, type=cv2.THRESH_BINARY)

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
        newPoser.horsums = self.horsums
        return newPoser

    def __deepcopy__(self, memodic=None):
        """The actual implementation of the object copy() method.  Named so that
        the copy module can find it."""
        newPoser = Poser(self.array, copyArray=True)
        newPoser.rots = copy.deepcopy(self.rots, memodic)
        newPoser.rots = copy.deepcopy(self.horsums, memodic)
        return newPoser

    def __init__(self, array):
        self.setArray(array)
        self.rots = dict()
        self.horsums = dict()
        self.moms = cv2.moments(self.array, binaryImage=True)

# Definitions of custom exceptions


class ArrayInitError(Exception):
    pass


class ArrayProcessError(Exception):
    pass
