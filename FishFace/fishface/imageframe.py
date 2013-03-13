#!/usr/bin/env python

import os
import Tkinter as tk
try:
    import numpy as np
    from PIL import ImageTk
    from PIL import Image
except ImportError:
    print "The imageframe module needs both numpy and PIL."
    raise

try:
    import cv2.cv as cv
    import cv2
except ImportError:
    print "The imageframe module needs OpenCV."
    raise


class Frame:

# ##
# ##  Object Initialization
# ##
    def __init__(self, image):
        self.originalFileName = None
        self.originalFileShape = None
        self.croppedTo = None
        self.preservedArrays = []

        self.setImage(image)

    def setImage(self, image, copyArray=True):
        """The frame is getting a new image.  If it's already a numpy.array with
        dtype uint8, just copy it.  If it's a string, try to load from that
        filename."""

        # Depending on file type, use various initializers

        # It's already a numpy array. Store or copy it.
        if(type(image) == np.ndarray):
            if copyArray:
                self.array = np.copy(image)
            else:
                self.array = image

        # It's a string; treat it like a filename.
        elif(type(image) == str):
            self.setImageFromFile(image)

        else:
            raise ImageInitError("setImage requires a numpy array or filename string, but I see a {}".format(type(image)))

        self.shape = self.array.shape

        if len(self.shape) > 1:
            self.spatialshape = tuple(self.shape[:2])
            self.ydim = self.spatialshape[0]
            self.xdim = self.spatialshape[1]

            if len(self.shape) == 2:
                self.channels = 1
            elif len(self.shape) == 3:
                self.channels = self.array.shape[2]

# ##
# ##  File I/O
# ##
    def setImageFromFile(self, filename):
        """Get image from file and store as my array."""
        if os.path.isfile(filename):
            self.array = cv2.cvtColor(cv2.imread(filename), cv.CV_RGB2BGR)
            self.originalFileName = filename
            self.originalFileShape = self.array.shape
        else:
            raise ImageInitError("File not found (or isn't a regular file): {}".format(filename))

    def saveImageToFile(self, filename):
        """Save the image to a file."""
        if self.channels == 1:
            cv2.imwrite(filename, self.array)
        elif self.channels == 3:
            cv2.imwrite(filename, cv2.cvtColor(self.array, cv.CV_BGR2RGB))

# ##
# ##  Debug display
# ##
    def onScreen(self, args=dict()):
        """I need something to display these things for debugging. This uses
        Tkinter to display in a no-frills, click-to-dismiss window."""

        if 'message' not in args:
            args['message'] = "image display - any key or click to close"

        if 'scaleFactor' not in args:
            args['scaleFactor'] = 1

        root = tk.Tk()
        root.title(args['message'])

        def kill_window(event):
            root.destroy()

        root.bind("<Button>", kill_window)
        root.bind("<Key>", kill_window)

        im = Image.fromarray(self.array)
        im = im.resize((int(im.size[0] * args['scaleFactor']),
                        int(im.size[1] * args['scaleFactor'])))

        photo = ImageTk.PhotoImage(im)

        lbl = tk.Label(root, image=photo)
        lbl.image = photo
        lbl.pack()

        root.mainloop()

# ##
# ##  Array-alterations
# ##
    def applyNull(self, args=dict()):
        pass

    def applyMedianFilter(self, args=dict()):
        """Apply median filtering to the array with a default kernel radius of 1."""
        if 'kernelRadius' not in args:
            args['kernelRadius'] = 1

        cv2.medianBlur(src=self.array, ksize=args['kernelRadius'], dst=self.array)

    def applyCanny(self, args=dict()):
        """Uses OpenCV's Canny filter implementation to find edges. By default, don't thicken the
        edges, but dilate with a thickener-radius circular kernel if the thickener arg is given."""

        if 'thickener' not in args:
            args['thickener'] = None

        self.array = cv2.Canny(src=self.array, threshold1=50, threshold2=100, apertureSize=3)

        if args['thickener']:
            kern = self.kernel(args['thickener'], shape="circle")
            cv2.dilate(src=self.array, kernel=kern, dst=self.array)

    def applyThreshold(self, args=dict()):
        """Wrapper for the cv2 threshold function."""

        if 'threshold' not in args:
            raise ImageProcessError("I need a threshold to apply.")

        # The [1] at the end is because we don't care what the retval is,
        # we just want the image back.
        cv2.threshold(src=self.array,
                      thresh=args['threshold'],
                      maxval=255,
                      type=cv2.THRESH_BINARY,
                      dst=self.array)

    def applyDeltaImage(self, args=dict()):
        """Finds the absolute difference between the calImage and my array,
        then stores/returns the result."""

        if 'calImageFrame' not in args:
            raise ImageProcessError("I need a calibration image to calculate the delta.")

        calFrame = args['calImageFrame']

        # if not isinstance(calFrame,Frame):
        #     raise ImageProcessError("The calibration image I received is not a Frame object.")

        if 'gray' in args:
            if self.channels != 2:
                self.applyGrayImage()
            if calFrame.channels != 2:
                calFrame = calFrame.copy()
                calFrame.applyGrayImage()

        cv2.absdiff(src1=calFrame.array,
                    src2=self.array,
                    dst=self.array)

    def applyGrayImage(self, args=dict()):
        """Convert to grayscale."""
        if self.channels == 3:
            self.setImage(cv2.cvtColor(src=self.array, code=cv.CV_RGB2GRAY))

    def applyDilate(self, args=dict()):
        """Morphological dilation with provided kernel."""

        if 'kernelRadius' in args:
            args['kernel'] = self.kernel(args['kernelRadius'])

        if 'kernel' not in args:
            raise ImageProcessError("I need a kernel with which to dilate.")

        if 'iter' not in args:
            args['iter'] = 1

        cv2.dilate(src=self.array, kernel=args['kernel'], dst=self.array, iterations=args['iter'])

    def applyErode(self, args=dict()):
        """Morphological erosion with provided kernel."""
        if 'kernelRadius' in args:
            args['kernel'] = self.kernel(args['kernelRadius'])

        if 'kernel' not in args:
            raise ImageProcessError("I need a kernel with which to dilate.")

        if 'iter' not in args:
            args['iter'] = 1

        cv2.erode(src=self.array, kernel=args['kernel'], dst=self.array, iterations=args['iter'])

    def applyOpening(self, args=dict()):
        """Morphological opening with generated kernel.  It's essentially an erosion
        followed by a dilation. Result is stored/returned."""
        if 'kernelRadius' not in args:
            args['kernelRadius'] = 3

        if 'kernelShape' not in args:
            args['kernelShape'] = 'circle'

        if 'iterations' not in args:
            args['iterations'] = 1

        args['kernel'] = self.kernel(radius=args['kernelRadius'], shape=args['kernelShape'])

        self.applyErode(args)
        self.applyDilate(args)

    def applyClosing(self, args=dict()):
        """Morphological closing with generated kernel.  It's essentially a dilation
        followed by an erosion. Result is stored/returned."""
        if 'kernelRadius' not in args:
            args['kernelRadius'] = 3

        if 'kernelShape' not in args:
            args['kernelShape'] = 'circle'

        if 'iterations' not in args:
            args['iterations'] = 1

        kern = self.kernel(radius=args['kernelRadius'], shape=args['kernelShape'])

        self.dilate(kern, args['iterations'])
        self.erode(kern, args['iterations'])

    def applySkeletonize(self, args=dict()):
        """Finds the morphological skeleton."""

        if self.channels > 1:
            raise ImageProcessError("I can only find the morphological skeleton of single-channel images, but I see {} channels.".format(self.channels))

        if 'skelKernelRadius' not in args:
            args['skelKernelRadius'] = 1

        if 'skelKernelShape' not in args:
            args['skelKernelShape'] = 1

        src = np.copy(self.array)
        size = np.size(src)

        kern = self.kernel(radius=args['skelKernelRadius'], shape=args['skelKernelShape'])

        complete = False

        while(not complete):
            eroded = cv2.erode(src, kern)
            temp = cv2.dilate(eroded, kern)
            temp = cv2.subtract(src, temp)
            self.array = cv2.bitwise_or(self.array, temp)
            src = np.copy(eroded)

            zeros = size - cv2.countNonZero(src)
            if zeros == size:
                complete = True

    def applyCrop(self, args=dict()):
        """Crops the image to the box provided."""

        if 'box' not in args:
            raise ImageProcessError("I need to know the crop boundaries before I can crop.")

        box = args['box']

        # save the last shape and the bounding box for future reference
        self.last_shape = self.shape

        if self.croppedTo:
            sct = self.croppedTo
            addme = (sct[0], sct[1], sct[0], sct[1])
            self.croppedTo = [a + b for a, b in zip(box, addme)]
        else:
            self.croppedTo = box

        self.setImage(self.array[box[0]:box[2], box[1]:box[3]])

    def applyCropToLargestBlob(self, args=dict()):
        contours = self.findAllContours()
        areas = [cv2.contourArea(ctr) for ctr in contours]
        if len(areas):
            max_contour = [contours[areas.index(max(areas))]]
            self.drawContours({'contours': max_contour})

            boundingBox = self.boundingBoxFromContour(max_contour)
            self.applyCrop({'box': boundingBox})
        else:
            print "No contours found in this frame."

# ##
# ##  Drawing methods
# ##
    def drawCirclesAtPoints(self, args=dict()):
        """Draws dots at each of the points in the list provided.  Various
        attributes of the points (e.g. color, radius) can be specified."""

        if 'points' not in args:
            raise ImageProcessError("I need points at which to draw circles, but I got none.")

        if 'lineColor' not in args:
            args['lineColor'] = (255, 0, 255)

        if 'lineThickness' not in args:
            args['lineThickness'] = 3

        if 'filledIn' not in args:
            args['filledIn'] = True

        if 'circleRadius' not in args:
            args['circleRadius'] = 3

        if args['filledIn']:
            args['lineThickness'] = -abs(args['lineThickness'])

        args['points'] = np.roll(args['points'], 1, axis=2)

        if self.channels == 1:
            args['lineColor'] = int(sum(args['lineColor']) / 3)

        for point in args['points']:
            cv2.circle(img=self.array,
                       center=tuple(point),
                       radius=args['circleRadius'],
                       color=args['lineColor'])

    def drawContours(self, args=dict()):
        """Actually draws the provided contours onto the image."""

        if 'contours' not in args:
            raise ImageProcessError("Can't draw contours without a list of contours.")
        if 'lineColor' not in args:
            args['lineColor'] = (255, 0, 255)
        if 'lineThickness' not in args:
            args['lineThickness'] = 3
        if 'filledIn' not in args:
            args['filledIn'] = True

        if args['filledIn']:
            args['lineThickness'] = -abs(args['lineThickness'])

        cv2.drawContours(image=self.array,
                         contours=args['contours'],
                         contourIdx= -1,
                         color=args['lineColor'],
                         thickness=args['lineThickness'])

# ##
# ##  Information and convenience methods
# ##

    def preserveArray(self, args=None):
        self.preservedArrays.append(np.copy(self.array))

    def findAllContours(self):
        """Returns a list of all contours in the single-channel image."""

        if self.channels > 1:
            raise ImageProcessError("I can only find contours in single-channel images, but I see {} channels.".format(self.channels))

        # I don't care about the hierarchy; I just want the contours.
        return cv2.findContours(self.array,
                                mode=cv2.RETR_EXTERNAL,
                                method=cv2.CHAIN_APPROX_SIMPLE
                                )[0]

    def boundingBoxFromContour(self, contour, border=1):
        """Convenience method to find the bounding box of a contour. Output is a tuple
        of the form (y_min, x_min, y_max, x_max).  The border is an optional extra
        margin to include in the cropped image."""
        maxes = np.amax(contour, axis=1)[0, 0]
        mins = np.amin(contour, axis=1)[0, 0]

        return (max(mins[1] - border, 0),
                max(mins[0] - border, 0),
                min(maxes[1] + border, self.xdim - 1),
                min(maxes[0] + border, self.ydim - 1))

    def kernel(self, radius=3, shape="circle"):
        """Convenience method wrapping the cv2.getStructuringElement method.
        Radius and shape can be specified."""

        if shape == "circle":
            shp = cv2.MORPH_ELLIPSE
        elif shape == "cross":
            shp = cv2.MORPH_CROSS
        elif shape == "rectangle":
            shp = cv2.MORPH_RECT
        else:
            raise ImageProcessError("Couldn't create a kernel with shape: {}".format(shape))
        return cv2.getStructuringElement(shp, (radius * 2 + 1, radius * 2 + 1))

# ##
# ##  Copy methods
# ##
    def shallowcopy(self):
        """Return a non-deep copy of this object."""
        return self.__copy__()

    def copy(self):
        """Return a deep copy of this object."""
        return self.__deepcopy__()

    def __copy__(self):
        """The actual implementation of the object shallowcopy() method.  Named so that
        the copy module can find it."""
        newFrame = Frame(self.array, copyArray=False)
        newFrame.originalFileName = self.originalFileName
        newFrame.originalFileShape = self.originalFileShape
        newFrame.croppedTo = self.croppedTo
        return newFrame

    def __deepcopy__(self, memodic=None):
        """The actual implementation of the object copy() method.  Named so that
        the copy module can find it."""
        newFrame = Frame(np.zeros(self.shape))
        newFrame.array = np.copy(self.array)
        newFrame.originalFileName = self.originalFileName
        newFrame.originalFileShape = self.originalFileShape
        newFrame.croppedTo = self.croppedTo
        return newFrame


# Definitions of custom exceptions

class ImageInitError(Exception):
    pass


class ImageMismatchError(Exception):
    pass


class ImageProcessError(Exception):
    pass
