#!/usr/bin/env python

import numpy as np
import os
import Tkinter as tk
import Image, ImageTk
# import copy

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
        if self.channels==1:
            cv2.imwrite(filename, self.array)              
        elif self.channels==3:
            cv2.imwrite(filename, cv2.cvtColor(self.array, cv.CV_BGR2RGB))              

    
    def onScreen(self, scaleFactor=1, message=None):
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
        im = im.resize((int(im.size[0]*scaleFactor), int(im.size[1]*scaleFactor)))
        
        photo = ImageTk.PhotoImage(im)
        
        lbl = tk.Label(root, image=photo)
        lbl.image = photo
        lbl.pack()
        
        root.mainloop()


    def applyMedianFilter(self, args=None):
        """Apply median filtering to the array with a default kernel radius of 1."""
        if 'kernelRadius' not in args:
            args['kernelRadius']=1
        
        cv2.medianBlur(src=self.array, ksize=args['kernelRadius'], dst=self.array)

    def applyCanny(self, args=None):
        """Uses OpenCV's Canny filter implementation to find edges. By default, don't thicken the
        edges, but dilate with a thickener-radius circular kernel if the thickener arg is given."""

        if 'thickener' not in args:
            args['thickener']=None
        
        self.array = cv2.Canny(src=self.array, threshold1=50, threshold2=100, apertureSize=3)
        
        if args['thickener']:
            kern = self.kernel(args['thickener'], shape="circle")
            cv2.dilate(src=self.array,kernel=kern,dst=self.array)

    def applyThreshold(self, args=None):
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

    def applyDeltaImage(self, args=None):
        """Finds the absolute difference between the calImage and my array,
        then stores/returns the result."""
        
        if 'calImageFrame' not in args:
            raise ImageProcessError("I need a calibration image to calculate the delta.")

        calFrame = args['calImageFrame']
        
        if not isinstance(calFrame,Frame):
            raise ImageProcessError("The calibration image I received is not a Frame object.")
        
        if 'gray' in args:
            if self.channels!=2:
                self.applyGrayImage()
            if calFrame.channels!=2:
                calFrame = calFrame.copy()
                calFrame.applyGrayImage()
        
        cv2.absdiff(src1=calFrame.array,
                    src2=self.array,
                    dst=self.array)
        
    def applyGrayImage(self, args=None):
        """Convert to grayscale."""
        if self.channels==3:
            cv2.cvtColor(src=self.array, code=cv.CV_RGB2GRAY, dst=self.array)

    def applyDilate(self, args=None):
        """Morphological dilation with provided kernel."""
        
        if 'kernelRadius' in args:
            args['kernel']=self.kernel(args['kernelRadius'])
        
        if 'kernel' not in args:
            raise ImageProcessError("I need a kernel with which to dilate.")
    
        if 'iter' not in args:
            args['iter']=1
        
        cv2.dilate(src=self.array, kernel=args['kernel'], dst=self.array, iterations=args['iter'])
        
    def applyErode(self, args=None):
        """Morphological erosion with provided kernel."""         
        if 'kernelRadius' in args:
            args['kernel']=self.kernel(args['kernelRadius'])
        
        if 'kernel' not in args:
            raise ImageProcessError("I need a kernel with which to dilate.")
    
        if 'iter' not in args:
            args['iter']=1
        
        cv2.erode(src=self.array, kernel=args['kernel'], dst=self.array, iterations=args['iter'])

    def applyOpening(self, args=None):
        """Morphological opening with generated kernel.  It's essentially an erosion
        followed by a dilation. Result is stored/returned."""
        if 'kernelRadius' not in args:
            args['kernelRadius']=3

        if 'kernelShape' not in args:
            args['kernelShape']='circle'
        
        if 'iterations' not in args:
            args['iterations']=1
        
        kern = self.kernel(radius=args['kernelRadius'], shape=args['kernelShape'])

        self.erode(kern, args['iterations'])
        self.dilate(kern, args['iterations'])

    def applyClosing(self, args=None):
        """Morphological closing with generated kernel.  It's essentially a dilation
        followed by an erosion. Result is stored/returned."""
        if 'kernelRadius' not in args:
            args['kernelRadius']=3

        if 'kernelShape' not in args:
            args['kernelShape']='circle'
        
        if 'iterations' not in args:
            args['iterations']=1
        
        kern = self.kernel(radius=args['kernelRadius'], shape=args['kernelShape'])

        self.dilate(kern, args['iterations'])
        self.erode(kern, args['iterations'])

    def drawCirclesAtPoints(self, args=None):
        """Draws dots at each of the points in the list provided.  Various
        attributes of the points (e.g. color, radius) can be specified."""

        if 'points' not in args:
            raise ImageProcessError("I need points at which to draw circles, but I got none.")
        
        if 'lineColor' not in args:
            args['lineColor']=(255,0,255)
        
        if 'lineThickness' not in args:
            args['lineThickness']=3

        if 'filledIn' not in args:
            args['filledIn']=True

        if 'circleRadius' not in args:
            args['circleRadius']=3

        if args['filledIn']:
            args['lineThickness'] = -abs(args['lineThickness'])

        args['points'] = np.roll(args['points'], 1, axis=2)
                    
        if self.channels==1:
            args['lineColor']=int(sum(args['lineColor'])/3)

        for point in args['points']:
            cv2.circle(img=self.array,
                       center=tuple(point),
                       radius=args['circleRadius'],
                       color=args['lineColor'])

    def applySkeletonize(self, args=None):
        """Finds the morphological skeleton."""
        
        if self.channels>1:
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
            temp = cv2.subtract(src,temp)
            self.array = cv2.bitwise_or(self.array,temp)
            src = np.copy(eroded)
        
            zeros = size - cv2.countNonZero(src)
            if zeros == size:
                complete = True

    def findAllContours(self, fr=None):
        """Returns a list of all contours in the single-channel image."""
        
        if fr=None:
            fr=self
        
        if fr.channels>1:
            raise ImageProcessError("I can only find the morphological skeleton of single-channel images, but I see {} channels.".format(self.channels))

        # I don't care about the hierarchy; I just want the contours.
        return cv2.findContours(fr.array, 
                                mode=cv2.RETR_EXTERNAL,
                                method=cv2.CHAIN_APPROX_SIMPLE
                                )[0]

    def findLargestBlobContour(self, kernelRadius=3, iterClosing=3, iterOpening=3):
        """Returns a list of lists.  Each element of the list is a single contour,
        and the elements of each contour are the ordered coordinates of the contour."""
        
        temp = self.copy()
        
        temp.applyClosing(kernelRadius=kernelRadius, iterations=iterClosing)
        temp.applyOpening(kernelRadius=kernelRadius, iterations=iterOpening)
        
        contours = temp.allContours(args)
        areas = [cv2.contourArea(ctr) for ctr in contours]
        max_contour = [contours[areas.index(max(areas))]]

        return max_contour

### FIXME: This is where I paused in the code-refactoring pass.

    def outlineLargestBlobWithContours(self, contours, lineColor=(255,0,255), lineThickness=3, filledIn=True):
        """Actually draws the provided contours onto the image."""

        if filledIn:
            lineThickness = -abs(lineThickness)

        cv2.drawContours(image=self.array,
                         contours=contours,
                         contourIdx=-1,
                         color=lineColor,
                         thickness=lineThickness)


    def drawOutlineAroundLargestBlob(self, calImageFrame, threshold=50, kernelRadius=3, lineColor=(255,0,255), lineThickness=3, filledIn=True):
        """Convenience method that finds the contours of the largest object
        and then draws them onto the image."""
        child = self.copy()
        
        child.deltaImage(calImageFrame)
        child.threshold(threshold)
        
        self.outlineLargestBlobWithContours(
                    child.findLargestBlobContours(kernelRadius=kernelRadius),
                    lineColor, lineThickness, filledIn)

    def crop(self, box):
        """Crops the image to the box provided."""

        # save the last shape and the bounding box for future reference
        self.last_shape = self.shape
        self.cropped_to = box

        cropped_array=self.array[box[0]:box[2], box[1]:box[3]]
        self.setImage(cropped_array)

    def cropToLargestBlob(self, calImageFrame, threshold=50, kernelRadius=3, returnArray=False, lineColor=(255,0,255), lineThickness=3, filledIn=True):
        """Convenience method that crops the image to the largest object in it."""

        out = self.copy()
        
        out.deltaImage(calImageFrame)
        out.threshold(threshold)        
        ctr = out.findLargestBlobContours(kernelRadius=kernelRadius)
    
        out.setImage(out.blankImageCopy())    
        out.outlineLargestBlobWithContours(ctr, lineColor, lineThickness, filledIn)
                        
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
