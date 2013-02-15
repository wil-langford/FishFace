#!/usr/bin/env python

import numpy as np
import os
import Tkinter as tk
import Image, ImageTk
import copy

### Both lines below do the same thing in the actual Python interpreter,
### but PyDev/Eclipse wants the second one for autocomplete and code
### analysis to work. 
# import cv
import cv2.cv as cv
import cv2

class Frame:
    def __init__(self, image):
        self.setImage(image)
    
    def setImage(self, image, copyArray=True):
        """The frame is getting a new image.  If it's already a numpy.array with
        dtype uint8, just copy it.  If it's a string, try to load from that
        filename."""
        
        # Depending on file type, use various initializers
        
        # It's already a numpy array. Store or copy it. 
        if(type(image)==np.ndarray):
            if copyArray:
                self.array = np.copy(image)
            else:
                self.array = image

        # It's a string; treat it like a filename.
        elif(type(image)==str):
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

    def setImageFromFile(self,filename):
        """Get image from file and store as my array."""
        if os.path.isfile(filename):
            self.array = cv2.cvtColor(cv2.imread(filename), cv.CV_RGB2BGR)
        else:
            raise ImageInitError("File not found (or isn't a regular file): {}".format(filename))

    def saveImageToFile(self, filename):
        """Save the image to a file."""
        cv2.imwrite(filename, cv2.cvtColor(self.array, cv.CV_BGR2RGB))                
    
    def onScreen(self, scaleDownFactor=1, message = None):
        """I need something to display these things for debugging. This uses
        Tkinter to display in a no-frills, click-to-dismiss window."""
        
        if message == None:
            message = "image display - any key or click to close"
        
        root = tk.Tk()
        root.title(message)
        
        def kill_window(event):
            root.destroy()
        
        root.bind("<Button>", kill_window)
        root.bind("<Key>", kill_window)
        
        im = Image.fromarray(self.array)        
        im = im.resize((im.size[0]//scaleDownFactor, im.size[1]//scaleDownFactor))
        
        photo = ImageTk.PhotoImage(im)
        
        lbl = tk.Label(root, image=photo)
        lbl.image = photo
        lbl.pack()
        
        root.mainloop()

    def findEdges(self, returnArray=False, thickenEdges=True, thickener=3):
        """Uses OpenCV's Canny filter implementation to find edges."""
        
        out = cv2.Canny(self.array, 50, 100, apertureSize=3)
        
        if thickenEdges:
            se = self.kernel(thickener, shape="circle")
            out = cv2.dilate(out,se)
        
        if returnArray:
            return out
        else:
            self.setImage(out)

    def boundingBoxFromContour(self,contour,border=1):
        """Convenience method to find the bounding box of a contour. Output is a tuple
        of the form (y_min, x_min, y_max, x_max).  The border is an optional extra
        margin to include in the cropped image."""
        maxes = np.amax(contour, axis=1)[0,0]
        mins  = np.amin(contour, axis=1)[0,0]
        
        return (max(mins[1] - border, 0),
                max(mins[0] - border, 0),
                min(maxes[1] + border, self.xdim-1),
                min(maxes[0] + border, self.ydim-1))

    def deltaImage(self, calImageFrame, returnArray=False):
        """Finds the absolute difference between the calImage and my array,
        then stores/returns the result."""
        
        diff = cv2.absdiff(calImageFrame.grayImage(returnArray=True),
                           self.grayImage(returnArray=True))
        
        if returnArray:
            return diff
        else:
            self.setImage(diff)
            return None

    def threshold(self, threshold, returnArray=False):
        """Wrapper for the cv2 threshold function. Stores/returns result."""

        # The [1] at the end is because we don't care what the retval is,
        # we just want the image back.
        out = cv2.threshold(self.array, thresh=threshold,
                            maxval=255, type=cv2.THRESH_BINARY)[1]
        
        if returnArray:
            return out
        else:
            self.setImage(out)
            return None
                   
    def grayImage(self, returnArray=False, method=0):
        """If my image is grayscale, return it.  Otherwise, convert to grayscale
        and store/return the result."""
        if self.array.ndim==2:
            gray = np.copy(self.array)
        elif self.array.ndim==3:
            # I experimented with each method.  All seem to work fine with my test images
            # so I'm using the fastest by default.
            # The higher the number of the method, the longer it takes.
            if method==0: # max of all three color values
                gray = np.amax(self.array, axis=2)
            elif method==1: # min of all three color values
                gray = np.amin(self.array, axis=2)
            elif method==2: # average of max color and min color
                # this one may be broken by the use of modular addition in uint8 arrays
                gray = (np.amax(self.array, axis=2) + np.amin(self.array, axis=2)) // 2
            elif method==3: # average of all three colors
                gray = np.sum(self.array, axis=2) // 3
            elif method==4: # using the mean function and converting to integer
                gray = np.mean(self.array, axis=2)
                gray = np.uint8(gray)
        else:
            raise ImageProcessError("Image did not have either 1 or 3 channels. I don't know how to convert it to grayscale.")
        
        gray = np.uint8(gray)
        
        if returnArray:
            return gray
        else:
            self.setImage(gray)
            self.channels=1
            return None 

    def kernel(self, radius=3, shape="circle"):
        """Convenience method wrapping the cv2.getStructuringElement method.
        Radius and shape can be specified."""

        if shape=="circle":
            shp = cv2.MORPH_ELLIPSE
        elif shape=="cross":
            shp = cv2.MORPH_CROSS
        elif shape=="rectangle":        
            shp = cv2.MORPH_RECT
        else:
            raise ImageProcessError("Couldn't create a kernel with shape: {}".format(shape))
        return cv2.getStructuringElement(shp, (radius*2+1, radius*2+1) )
                
    def toTheBones(self, skelKernelRadius=1, skelKernelShape='circle', returnArray=False):
        """Finds the morphological skeleton.  Kernel parameters are passed to
        self.kernel, and the result is stored/returned."""
        src = np.copy(self.array)
        size = np.size(src)
        out = np.zeros(src.shape,np.uint8)

        se = self.kernel(radius=skelKernelRadius, shape=skelKernelShape)
        
        complete = False
        
        while(not complete):
            eroded = cv2.erode(src, se)
            eph = cv2.dilate(eroded, se)
            eph = cv2.subtract(src,eph)
            out = cv2.bitwise_or(out,eph)
            src = np.copy(eroded)
        
            zeros = size - cv2.countNonZero(src)
            if zeros == size:
                complete = True

        if returnArray:
            return out
        else:
            self.setImage(out)
            return None

    def dilate(self, kernel, dilIter, returnArray=False):
        """Morphological dilation with provided kernel. Result is stored/returned."""
        arr = np.copy(self.array)
        
        arr = cv2.dilate(arr, kernel=kernel, iterations=dilIter)

        if returnArray:
            return arr
        else:
            self.setImage(arr)
            return None

    def erode(self, kernel, erIter, returnArray=False):
        """Morphological erosion with provided kernel. Result is stored/returned."""
        arr = np.copy(self.array)

        arr = cv2.erode(arr, kernel=kernel, iterations=erIter)

        if returnArray:
            return arr
        else:
            self.setImage(arr)
            return None

    def binOpening(self, kernelRadius=3, kernelShape='circle', iterations=1, returnArray=False):
        """Morphological opening with generated kernel.  It's essentially an erosion
        followed by a dilation. Result is stored/returned."""
        out = self.copy()
        
        se = self.kernel(radius=kernelRadius, shape=kernelShape)

        out.erode(se, iterations)
        out.dilate(se, iterations)

        if returnArray:
            return out
        else:
            self.setImage(out.array)
            return None

    def binClosing(self, kernelRadius=3, kernelShape='circle', iterations=1, returnArray=False):
        """Morphological closing with generated kernel.  It's essentially a dilation
        followed by an erosion. Result is stored/returned."""
        out = self.copy()
        
        se = self.kernel(radius=kernelRadius, shape=kernelShape)

        out.dilate(se, iterations)
        out.erode(se, iterations)

        if returnArray:
            return out
        else:
            self.setImage(out.array)
            return None

    def findLargestObjectContours(self, kernelRadius=3, iterClosing=3, iterOpening=3):
        """Returns a list of lists.  Each element of the list is a single contour,
        and the elements of each contour are the ordered coordinates of the contour."""
        
        temp = self.copy()
        temp.grayImage()
        
        temp.binClosing(kernelRadius=kernelRadius, iterations=iterClosing)
        temp.binOpening(kernelRadius=kernelRadius, iterations=iterOpening)

        # the [0] at the end is because we don't care about the hierarchy
        contours = cv2.findContours(temp.array,
                                    mode=cv2.RETR_EXTERNAL,
                                    method=cv2.CHAIN_APPROX_SIMPLE
                                    )[0]
        
        areas = [cv2.contourArea(ctr) for ctr in contours]
        max_contour = [contours[areas.index(max(areas))]]

        return max_contour

    def outlineLargestObjectWithContours(self, contours, lineColor=(255,0,255), lineThickness=3, filledIn=True):
        """Actually draws the provided contours onto the image."""

        if filledIn:
            lineThickness = -abs(lineThickness)

        cv2.drawContours(image=self.array,
                         contours=contours,
                         contourIdx=-1,
                         color=lineColor,
                         thickness=lineThickness)

    def circlesAtPoints(self, points, lineColor=(255,0,255), lineThickness=3, filledIn=True, circleRadius=3):
        """Draws dots at each of the points in the list provided.  Various
        attributes of the points (e.g. color, radius) can be specified."""

        if filledIn:
            lineThickness = -abs(lineThickness)

        points = np.roll(points, 1, axis=2)
                    
        if self.array.ndim==2:
            lineColor=sum(lineColor)//3

        for point in points:
            cv2.circle(img=self.array,
                       center=tuple(point),
                       radius=circleRadius,
                       color=lineColor)

    def drawOutlineAroundLargestObject(self, calImageFrame, threshold=50, kernelRadius=3, lineColor=(255,0,255), lineThickness=3, filledIn=True):
        """Convenience method that finds the contours of the largest object
        and then draws them onto the image."""
        child = self.copy()
        
        child.deltaImage(calImageFrame)
        child.threshold(threshold)
        
        self.outlineLargestObjectWithContours(
                    child.findLargestObjectContours(kernelRadius=kernelRadius),
                    lineColor, lineThickness, filledIn)

    def crop(self, box):
        """Crops the image to the box provided."""
        print box
        print self.array.shape
        cropped_array=self.array[box[0]:box[2], box[1]:box[3]]
        self.setImage(cropped_array)

    def cropToLargestBlob(self, calImageFrame, threshold=50, kernelRadius=3, returnArray=False, lineColor=(255,0,255), lineThickness=3, filledIn=True):
        """Convenience method that crops the image to the largest object in it."""

        out = self.copy()
        
        out.deltaImage(calImageFrame)
        out.threshold(threshold)        
        ctr = out.findLargestObjectContours(kernelRadius=kernelRadius)
    
        out.setImage(out.blankImageCopy())    
        out.outlineLargestObjectWithContours(ctr, lineColor, lineThickness, filledIn=True)
                        
        out.crop(out.boundingBoxFromContour(ctr))

        if returnArray:
            return out.array
        else:
            self.setImage(out.array)
            return None

    def blankImageCopy(self, mode=None):
        """Return an array the same size as my image, optionally collapsing
        the channel dimension to one channel to create a grayscale image."""
        if mode==None:
            return np.zeros(self.shape)
        if mode=="L":
            return np.zeros(self.spatialshape)


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
        return newFrame

    def __deepcopy__(self, memodic=None):
        """The actual implementation of the object copy() method.  Named so that
        the copy module can find it."""
        newFrame = Frame(self.blankImageCopy())
        newFrame.array = np.copy(self.array)
        return newFrame


# Definitions of custom exceptions

class ImageInitError(Exception):
    pass

class ImageMismatchError(Exception):
    pass

class ImageProcessError(Exception):
    pass
