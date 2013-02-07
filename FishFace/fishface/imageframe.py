#!/usr/bin/env python

import numpy as np
import os
import Tkinter as tk
import Image, ImageTk

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
        """Object is getting a new image.  If it's already a numpy.array with
        dtype uint8, just copy it.  If it's a string, try to load from that
        filename."""
        
        # Depending on file type, use various initializers
        if(type(image)==np.ndarray):
            if copyArray:
                self.array = np.copy(image)
            else:
                self.array = image

        elif(type(image)==str):
            self.setImageFromFile(image)
        
        else:
            raise ImageInitError("setImage requires a cvMat, numpy array, or filename string, but I see a {}".format(type(image)))

    def setImageFromFile(self,filename):
        """Get image from file and store as my array."""
        if os.path.isfile(filename):
            self.array = cv2.cvtColor(cv2.imread(filename), cv.CV_RGB2BGR)
        else:
            raise ImageInitError("File not found: {}".format(filename))

    def saveImageToFile(self, filename):
        """Save the image to a file."""
        cv2.imwrite(filename, cv2.cvtColor(self.array, cv.CV_BGR2RGB))                
    
    def onScreen(self, scaleDownFactor=2, message = None):
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
            se = self.slider(thickener, shape="circ")
            out = cv2.dilate(out,se)
        
        if returnArray:
            return out
        else:
            self.array = out

    def shallowcopy(self):
        return self.__copy__()

    def copy(self):
        return self.__deepcopy__()

    def blankCopy(self, mode=None):
        if mode==None:
            return np.zeros(self.array.shape)
        if mode=="L":
            return np.zeros(self.array.shape[0:1])

    def deltaImage(self, calImage, returnArray=False):
        """Finds the absolute difference between the calImage and my array,
        then stores/returns the result."""
        
        diff = cv2.absdiff(calImage.grayImage(returnArray=True),
                           self.grayImage(returnArray=True))
        
        if returnArray:
            return diff
        else:
            self.array = diff
            return None

    def threshold(self, threshold, returnArray=False):
        # The [1] at the end is because we don't care what the retval is,
        # we just want the image back.
        out = cv2.threshold(self.array, thresh=threshold,
                            maxval=255, type=cv2.THRESH_BINARY)[1]
        
        if returnArray:
            return out
        else:
            self.array = out
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
            raise ImageProcessError("Image did not have either 1 or 3 channels. Can't convert to grayscale.")
        
        gray = np.uint8(gray)
        
        if returnArray:
            return gray
        else:
            self.array = gray
            return None 

    def slider(self, radius=3, shape="circ"):
        if shape=="circ":
            shp = cv2.MORPH_ELLIPSE
        elif shape=="cross":
            shp = cv2.MORPH_CROSS
        elif shape=="rect":        
            shp = cv2.MORPH_RECT
        else:
            raise ImageProcessError("Couldn't create a slider with shape: {}".format(shape))
        return cv2.getStructuringElement(shp, (radius*2+1, radius*2+1) )
                
    def findLargestObjectContours(self, sliderRadius=3, iterClosing=3, iterOpening=3):
        
        out = np.copy(self.array)
        
        # dilation followed by erosion fills in holes
        # this process is called closing
        se = self.slider(sliderRadius)
        out = cv2.dilate(out, kernel=se, iterations=iterClosing)        
        out = cv2.erode(out, kernel=se, iterations=iterClosing)

        # erosion followed by dilation removes smaller objects
        # this process is called opening
        se = self.slider(sliderRadius)
        out = cv2.erode(out, kernel=se, iterations=iterOpening)
        out = cv2.dilate(out, kernel=se, iterations=iterOpening)        

        # the [0] at the end is because we don't care about the hierarchy
        contours = cv2.findContours(out,
                                    mode=cv2.RETR_EXTERNAL,
                                    method=cv2.CHAIN_APPROX_SIMPLE
                                    )[0]
        
        areas = [cv2.contourArea(ctr) for ctr in contours]
        max_contour = [contours[areas.index(max(areas))]]

        return max_contour

    def outlineLargestObjectWithContours(self, contours, lineColor=(255,100,100), lineThickness=3):
        cv2.drawContours(image=self.array,
                         contours=contours,
                         contourIdx=-1,
                         color=lineColor,
                         thickness=lineThickness)
        
    def __copy__(self):
        newFrame = Frame(self.array)
        return newFrame

    def __deepcopy__(self, memodic=None):
        newFrame = Frame(self.blankCopy())
        newFrame.array = np.copy(self.array)
        return newFrame


class ImageInitError(Exception):
    pass

class ImageMismatchError(Exception):
    pass

class ImageProcessError(Exception):
    pass
