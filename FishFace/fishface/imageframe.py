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

class Frame:
    def __init__(self, image):
        self.setImage(image)
    
    def setImage(self, image, copyCvMat=True):
        """Object is getting a new image.  If it's already an OpenCV Mat,
        just store it.  Otherwise, try to convert it from numpy.array or
        load it from a filename string."""
        
        # Depending on file type, use various initializers
        if (type(image)==cv.cvmat):
            if copyCvMat:
                self.cvmat = cv.CreateMat(image.rows,image.cols,image.type)
                cv.Copy(image, self.cvmat)
            else:
                self.cvmat = image

        elif(type(image)==np.ndarray):
            self.fromArray(image)

        elif(type(image)==str):
            self.setImageFromFile(image)
        
        else:
            raise ImageInitError("setImage requires a cvMat, numpy array, or filename string, but I see a {}".format(type(image)))

    def setImageFromFile(self,filename):
        """Get image from file and store as CvMat."""
        if os.path.isfile(filename):
            self.cvmat = cv.LoadImageM(filename)
        else:
            raise ImageInitError("File not found: {}".format(filename))

    def fromArray(self,image):
        """Convert Numpy array to my CvMat and store as my image."""
        if image.dtype==np.uint8:
            self.cvmat = cv.fromarray(image)
        else:
            raise ImageInitError("Image must have 8 bits per channel.")
    
    def toArray(self):
        """Convert my image from CvMat to Numpy array and return it."""
        return np.asarray(self.cvmat)

    def saveImageToFile(self, filename):
        """Save the image to a file."""
        cv.SaveImage(filename, self.cvmat)                
    
    def onScreen(self, scaleDownFactor=2):
        """I need something to display these things for debugging. This uses
        Tkinter to display in a no-frills, click-to-dismiss window."""
        
        root = tk.Tk()
        root.title("image display - any key or click to close")
        
        def kill_window(event):
            root.destroy()
        
        root.bind("<Button>", kill_window)
        root.bind("<Key>", kill_window)
        
        if self.cvmat.channels==3:
            im = Image.fromstring(
                                  'RGB',
                                  cv.GetSize(self.cvmat),
                                  self.cvmat.tostring(),
                                  "raw",
                                  "BGR",
                                  self.cvmat.width*3,
                                  0
                              )
        else:
            im = Image.fromstring(
                                  'L',
                                  cv.GetSize(self.cvmat),
                                  self.cvmat.tostring()
                              )
        
        im = im.resize((im.size[0]//scaleDownFactor, im.size[1]//scaleDownFactor))
        
        photo = ImageTk.PhotoImage(im)
        
        lbl = tk.Label(root, image=photo)
        lbl.image = photo
        lbl.pack()
        
        root.mainloop()

    def findEdges(self, returnMat=False, thickenEdges=True, thickener=3):
        """Uses OpenCV's Canny filter implementation to find edges."""
        
        out = self.blankCopy(mode="L")
        
        cv.Canny(self.cvmat, out, 50, 100, 3)
        
        if thickenEdges:
            se = self.slider(thickener, shape="circle")
            cv.Dilate(out,out,se)
        
        if returnMat:
            return out
        else:
            self.cvmat = out

    def shallowcopy(self):
        return self.__copy__()

    def copy(self):
        return self.__deepcopy__()

    def blankCopy(self, mode=None):
        if mode=="RGB":
            mode=cv.CV_8UC3
        elif mode=="L":
            mode=cv.CV_8UC1
        else:
            mode=self.cvmat.type
        
        blank = cv.CreateMat(self.cvmat.rows, self.cvmat.cols, mode)
        cv.SetZero(blank)
        return blank

    def deltaImage(self, calImage, returnMat=False):
        """Subtracts the provided calImage from my image, takes the absolute
        value, then stores/returns the result."""
        
        cg = calImage.grayImage(returnMat=True)
        sg = self.grayImage(returnMat=True)
        
        diff = self.blankCopy(mode="L")
        
        cv.AbsDiff(cg,sg,diff)
        
        if returnMat:
            return diff
        else:
            self.cvmat = diff
            return None

    def threshold(self, threshold, returnMat=False):
        out = self.blankCopy(mode="L")
        
        cv.Threshold(self.cvmat, out, threshold, 255, cv.CV_THRESH_BINARY)
        
        if returnMat:
            return out
        else:
            self.cvmat = out
            return None
                   
    def grayImage(self, returnMat=False):
        """If my image is grayscale, return it.  Otherwise, convert to grayscale
        and store/return the result."""
        if self.cvmat.channels==1:
            if returnMat:
                return self.cvmat
            else:
                return None
        elif self.cvmat.channels==3:
            gray_mat = cv.CreateMat(self.cvmat.rows, self.cvmat.cols, cv.CV_8UC1)                
            cv.CvtColor(self.cvmat, gray_mat, cv.CV_RGB2GRAY)
            
            if returnMat:
                return gray_mat
            else:
                self.cvmat = gray_mat
                return None
        else:
            raise ImageProcessError("Image did not have either 1 or 3 channels. Can't convert to grayscale.") 

    def slider(self, radius=3, shape="circ"):
        if shape=="circ":
            shp = cv.CV_SHAPE_ELLIPSE
        elif shape=="cross":
            shp = cv.CV_SHAPE_RECT
        elif shape=="rect":        
            shp = cv.CV_SHAPE_RECT
        else:
            raise ImageProcessError("Couldn't create a slider with shape: {}".format(shape))
        return cv.CreateStructuringElementEx(radius*2+1, radius*2+1,
                                            radius, radius,
                                            shp)
                
    def findLargestObject(self, returnMat=False, sliderRadius=3, iterClosing=2, iterOpening=3):
        #out = self.blankCopy()
        #cv.Copy(self.cvmat, out)
        
        out = self.cvmat

        # dilation followed by erosion fills in holes
        # this process is called closing
        se = self.slider(sliderRadius)
        cv.Dilate(out, out, se, iterClosing)        
        cv.Erode(out,out, se, iterClosing)
        
        # erosion followed by dilation removes smaller objects
        # this process is called opening
        se = self.slider(sliderRadius)
        cv.Erode(out,out, se, iterOpening)
        cv.Dilate(out, out, se, iterOpening)
    
        contours = cv.FindContours(out,cv.CreateMemStorage(),mode=cv.CV_RETR_EXTERNAL)
        
        ctr = contours
        
        print len(ctr)
        while(ctr.h_next()!=None):
            print len(ctr)
            ctr = ctr.h_next()
        
    def __copy__(self):
        newFrame = Frame(self.cvmat)
        return newFrame

    def __deepcopy__(self, memodic=None):
        newFrame = Frame(self.blankCopy())
        cv.Copy(self.cvmat, newFrame.cvmat)
        return newFrame


class ImageInitError(Exception):
    pass

class ImageMismatchError(Exception):
    pass

class ImageProcessError(Exception):
    pass
