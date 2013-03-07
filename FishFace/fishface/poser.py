#!/usr/bin/env python

import copy
import numpy as np
from scipy import ndimage

import Tkinter as tk
from PIL import ImageTk
from PIL import Image


### Both lines below do the same thing in the actual Python interpreter,
### but PyDev/Eclipse wants the second one for autocomplete and code
### analysis to work.
# import cv
#import cv2.cv as cv

import cv2


class Poser:

    def findLongAxis(self, samples=10, iterations=2):

        #  Since we're just trying to find the angle of the axis with this
        #  method, 0-180 is sufficient.  We'll decide which direction the
        #  axis points later.

        #  Having said that, I'm going to take the cheap way out to fix the
        #  overlap case (where the candidate angle is near zero) by extending
        #  the stopAngle by several steps and only considering the candidates
        #  in the "middle" 180 degrees.

        startAngle = 0
        stopAngle = 180 + (int(180 / samples) * 4)

        for dummy in range(iterations):
            stepsize = int((stopAngle - startAngle) / samples)
            for angle in range(startAngle, stopAngle, stepsize):
                self.rotate(angle)
                self.horsum(angle)

            ks = list(self.horsums.keys())
            vs = [np.amax(hs) for hs in self.horsums.values()]
            max_length = max(vs[2:-2])
            candidate = ks[vs.index(max_length)]

            startAngle = max(0, candidate - stepsize)
            stopAngle = min(180 + (4 * stepsize), candidate + stepsize)

        frhor = self.rotate(candidate)

        mid_x = int(frhor.shape[0] / 2)

        leftsum = np.sum(frhor[:, :mid_x])
        rightsum = np.sum(frhor[:, mid_x:])

        if leftsum < rightsum:
            candidate = candidate + 180 % 360

        # The actual angle of the fish is the inverse of the candidate,
        # because we rotated the whole array and then measured along one axis.
        # Also, because at this point we only know a line parallel to the long
        # axis and not the orientation of that axis, 180 is as good as 360.
        return int((-candidate) % 360)

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

    def onScreen(self, degrees=None):
        """I need something to display these things for debugging. This uses
        Tkinter to display in a no-frills, click-to-dismiss window."""

        if degrees:
            im = Image.fromarray(self.rotate(degrees))
            msg = "{} degree rotation - any key/click to continue".format(degrees)
        else:
            im = Image.fromarray(self.array)
            msg = "any key/click to continue"

        root = tk.Tk()
        root.title(msg)

        def kill_window(event):
            root.destroy()

        root.bind("<Button>", kill_window)
        root.bind("<Key>", kill_window)

        im = im.resize((int(im.size[0]),
                        int(im.size[1])))

        photo = ImageTk.PhotoImage(im)

        lbl = tk.Label(root, image=photo)
        lbl.image = photo
        lbl.pack()

        root.mainloop()

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

# Definitions of custom exceptions


class ArrayInitError(Exception):
    pass


class ArrayProcessError(Exception):
    pass
