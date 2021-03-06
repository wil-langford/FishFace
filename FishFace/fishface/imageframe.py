#!/usr/bin/env python
"""
The imageframe module provides the imageframe.Frame object (and some supporting objects).
"""

import os
import copy
import math

try:
    import numpy as np
except ImportError:
    print "The imageframe module needs numpy."
    print "In debian, install the python-numpy package to meet this requirements."
    raise

try:
    import cv2
except ImportError:
    print "The imageframe module needs OpenCV."
    raise


class Frame:
    """
The Frame object is the workhorse of the image processing done by FishFace.
It has two main attributes:
    Frame.array - a numpy array that contains the current image data
    Frame.data - a dictionary that stores metadata about the current image
        Some notable dictionary elements:
        * originalFileName - the filename of the source image
        * originalFileShape - the resolution and number of channels of the source image
        * croppedTo - if we have cropped the image, this is the box that we cropped to
        * shape - current shape of the image (includes number of channels)
        * spatialShape - current shape of the image (just the 2D shape, not the number of channels)
"""

# ##
# ##  Object Initialization
# ##
    def __init__(self, image):
        self.data = { 'preservedArrays':[] }

        self.setImage(image)

    def setImage(self, image, copyArray=True):
        """The frame is getting a new image.  If it's already a numpy.array with
        dtype uint8, just copy it.  If it's a string, try to load from that
        filename."""

        # Depending on file type, use various initializers:

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

        self.data['shape'] = self.array.shape

        if len(self.data['shape']) > 1:
            self.data['spatialShape'] = tuple(self.data['shape'][:2])
            self.ydim = self.data['spatialShape'][0]
            self.xdim = self.data['spatialShape'][1]

            if len(self.data['shape']) == 2:
                self.data['channels'] = 1
            elif len(self.data['shape']) == 3:
                self.data['channels'] = self.array.shape[2]

# ##
# ##  File I/O
# ##
    def setImageFromFile(self, filename):
        """Get image from file and store as my array."""
        if os.path.isfile(filename):
            self.array = cv2.cvtColor(cv2.imread(filename), cv2.COLOR_RGB2BGR)
            self.data['originalFileName'] = filename
            self.data['originalFileShape'] = self.array.shape
            if len(self.array.shape) == 2:
                self.data['channels'] = 1
            else:
                self.data['channels'] = self.array.shape[-1]
        else:
            raise ImageInitError("File not found (or isn't a regular file): {}".format(filename))

    def saveImageToFile(self, filename):
        """Save the image to a file."""
        if self.data['channels'] == 1:
            cv2.imwrite(filename, self.array)
        elif self.data['channels'] == 3:
            cv2.imwrite(filename, cv2.cvtColor(self.array, cv2.COLOR_BGR2RGB))

# ##
# ##  Debug display
# ##
    def onScreen(self, args=dict()):
        """I need something to display these things for debugging. This uses
        OpenCV to display in a no-frills, any-key-to-dismiss window."""

        if 'windowHeight' not in args:
            args['windowHeight'] = 500

        if 'delayAutoClose' not in args:
            args['delayAutoClose'] = 10000

        if 'scaleFactor' not in args:
            height = float(self.data['spatialShape'][0])
            args['scaleFactor'] = float(args['windowHeight'])/height

        if 'message' not in args:
            args['message'] = "image display - any key to close"

        # def kill_window(event):
        #     cv2.destroyWindow(args['message'])

        cv2.namedWindow(args['message'], 0)
        shape = self.data['spatialShape']
        width = int(shape[1] * args['scaleFactor'])
        height = int(shape[0] * args['scaleFactor'])

        cv2.resizeWindow(args['message'], width, height)
        # cv2.setMouseCallback(args['message'], kill_window)

        cv2.imshow(args['message'], self.array)
        cv2.startWindowThread()
        cv2.waitKey(args['delayAutoClose'])
        cv2.destroyWindow(args['message'])

# ##
# ##  Array-alterations
# ##
    def applyNull(self, args=dict()):
        pass

    def applyRevertToSource(self,args=dict()):
        if 'saveCurrent' in args:
            if args['saveCurrent']:
                self.preserveArray()

        if 'originalFileName' in self.data:
            self.setImageFromFile(self.data['originalFileName'])

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
            if self.data['channels'] != 2:
                self.applyGrayImage()
            if calFrame.data['channels'] != 2:
                calFrame = calFrame.copy()
                calFrame.applyGrayImage()

        cv2.absdiff(src1=calFrame.array,
                    src2=self.array,
                    dst=self.array)

    def applyRotate(self, args=dict()):
        """Rotate the image array."""
        if 'aroundPoint' not in args:
            shape = np.array([self.data['spatialShape'][1], self.data['spatialShape'][0]])
            args['aroundPoint'] = tuple((shape/2.0).astype(np.int32))

        if 'scale' not in args:
            args['scale'] = 1/(2.0 ** 0.5)

        if 'angleDegrees' not in args:
            args['angleDegrees'] = 0

        if 'borderMode' not in args:
            args['borderMode'] = cv2.BORDER_REPLICATE

        if 'borderValue' not in args:
            args['borderValue'] = 0

        rotMatrix = cv2.getRotationMatrix2D(args['aroundPoint'], args['angleDegrees'], args['scale'])

        self.array = cv2.warpAffine(self.array, rotMatrix, tuple(shape), borderMode=args['borderMode'],
                                    borderValue=args['borderValue'])

    def applyGrayImage(self, args=dict()):
        """Convert to grayscale."""
        if self.data['channels'] == 3:
            self.setImage(cv2.cvtColor(src=self.array, code=cv2.COLOR_RGB2GRAY))

    def applyDilate(self, args=dict()):
        """Morphological dilation with provided kernel."""

        if 'kernelRadius' in args:
            args['kernel'] = self.kernel(args['kernelRadius'])

        if 'kernel' not in args:
            raise ImageProcessError("I need a kernel with which to dilate.")

        if 'iterations' not in args:
            args['iterations'] = 1

        cv2.dilate(src=self.array, kernel=args['kernel'], dst=self.array, iterations=args['iterations'])

    def applyErode(self, args=dict()):
        """Morphological erosion with provided kernel."""
        if 'kernelRadius' in args:
            args['kernel'] = self.kernel(args['kernelRadius'])

        if 'kernel' not in args:
            raise ImageProcessError("I need a kernel with which to dilate.")

        if 'iterations' not in args:
            args['iterations'] = 1

        cv2.erode(src=self.array, kernel=args['kernel'], dst=self.array, iterations=args['iterations'])

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

        args['kernel'] = self.kernel(radius=args['kernelRadius'], shape=args['kernelShape'])

        self.applyDilate(args)
        self.applyErode(args)

    def applySkeletonize(self, args=dict()):
        """Finds the morphological skeleton."""

        if self.data['channels'] > 1:
            raise ImageProcessError("I can only find the morphological skeleton of single-channel images, but I see {} channels.".format(self.data['channels']))

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
        self.data['last_shape'] = self.data['shape']

        if 'croppedTo' in self.data:
            sct = self.data['croppedTo']
            addme = (sct[0], sct[1], sct[0], sct[1])
            self.data['croppedTo'] = [a + b for a, b in zip(box, addme)]
        else:
            self.data['croppedTo'] = box

        if 'centroid' in self.data:
            sct = self.data['croppedTo']
            addme = (sct[0],sct[1])
            self.data['centroid'] = (self.data['centroid'][0] + addme[0],
                                     self.data['centroid'][1] + addme[1])

        self.setImage(self.array[box[0]:box[2], box[1]:box[3]])

    def applyCropToLargestBlob(self, args=dict()):
        contours = self.findAllContours()
        areas = [cv2.contourArea(ctr) for ctr in contours]
        if len(areas):
            max_contour = [contours[areas.index(max(areas))]]
            self.drawContours({'contours': max_contour})

            boundingBox = self.boundingBoxFromContour(max_contour)
            self.applyCrop({'box': boundingBox})

            self.data['moments'] = cv2.moments(self.array)
        else:
            print "No contours found in this frame."

    def applyResize(self, args=dict()):
        """Resizes the image to the new shape provided."""

        if 'newshape' not in args:
            raise ImageProcessError("I need to know the new shape before I can resize.")

        shp = args['newshape']

        # save the last shape and the new shape for future reference
        self.data['last_shape'] = self.data['shape']
        self.data['new_shape'] = shp
        self.data['spatialShape'] = tuple(shp)
        self.ydim = self.data['spatialShape'][0]
        self.xdim = self.data['spatialShape'][1]

        self.setImage(cv2.resize(self.array, shp))


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

        if len(args['points'].shape)>2:
            args['points'] = np.roll(args['points'], 1, axis=2)

        if self.data['channels'] == 1:
            args['lineColor'] = int(sum(args['lineColor']) / 3)

        for point in args['points']:
            cv2.circle(img=self.array,
                       center=tuple(point),
                       thickness=args['lineThickness'],
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

    def drawOrientation(self,args=dict()):
        if 'centerPoint' not in args:
            raise ImageProcessError("I need to know the point to draw from.")

        if 'angle' not in args:
            raise ImageProcessError("I need to know what angle to draw.")

        if 'length' not in args:
            args['length']=75

        if 'lineColor' not in args:
            args['lineColor'] = (255, 0, 255)

        if 'lineThickness' not in args:
            args['lineThickness'] = 2

        if 'circleRadius' not in args:
            args['circleRadius'] = 4

        angle = math.radians((args['angle'] - 90) % 360)

        cp = args['centerPoint']
        ncp = (int(cp[0] + args['length']*math.sin(angle)),
                          int(cp[1] + args['length']*math.cos(angle)))

        pts = [np.array([[cp],[ncp]],dtype=np.int32)]

        self.drawContours({'contours':pts,
                           'lineColor':args['lineColor'],
                           'lineThickness':args['lineThickness'],
                           'filledIn':False
                          })
        self.drawCirclesAtPoints({'points':np.array([cp]),
                                  'circleRadius':args['circleRadius'],
                                  'lineColor':args['lineColor'],
                                  'lineThickness':args['lineThickness']
                                  })

# ##
# ##  Information and convenience methods
# ##

    def preserveArray(self, args=None):
        self.data['preservedArrays'].append(np.copy(self.array))

    def findAllContours(self):
        """Returns a list of all contours in the single-channel image."""

        if self.data['channels'] > 1:
            raise ImageProcessError("I can only find contours in single-channel images, but I see {} channels.".format(self.data['channels']))

        # I don't care about the hierarchy; I just want the contours.

        self.data['allContours'] =  cv2.findContours(self.array,
                                    mode=cv2.RETR_EXTERNAL,
                                    method=cv2.CHAIN_APPROX_SIMPLE
                                    )[1]

        return self.data['allContours']

    def boundingBoxFromContour(self, contour, border=1):
        """Convenience method to find the bounding box of a contour. Output is a tuple
        of the form (y_min, x_min, y_max, x_max).  The border is an optional extra
        margin to include in the cropped image."""

        xCorner, yCorner, width, height = cv2.boundingRect(contour[0])

        xMin = max(0, xCorner - border)
        yMin = max(0, yCorner - border)
        xMax = min(self.xdim - 1, xCorner + width + border)
        yMax = min(self.ydim - 1, yCorner + height + border)

        return (yMin, xMin, yMax, xMax)

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

    def findCentroid(self, args=dict()):
        if 'moments' not in self.data:
            raise ImageProcessError("You must applyCropToLargestBlob before computing the centroid.")

        m00 = self.data['moments']['m00']
        m10 = self.data['moments']['m10']
        m01 = self.data['moments']['m01']

        x = int(m10/m00)
        y = int(m01/m00)

        self.data['centroid'] = (x,y)
        if 'croppedTo' in self.data:
            sct = self.data['croppedTo']
            addme = (sct[1],sct[0])
            self.data['absoluteCentroid'] = (x+addme[0], y+addme[1])

        return self.data['centroid']

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
        newFrame.data = copy.copy(self.data)
        return newFrame

    def __deepcopy__(self, memodic=None):
        """The actual implementation of the object copy() method.  Named so that
        the copy module can find it."""
        newFrame = Frame(np.zeros(self.data['shape']))
        newFrame.array = np.copy(self.array)
        newFrame.data = copy.deepcopy(self.data)
        return newFrame


# Definitions of custom exceptions

class ImageInitError(Exception):
    pass


class ImageMismatchError(Exception):
    pass


class ImageProcessError(Exception):
    pass
