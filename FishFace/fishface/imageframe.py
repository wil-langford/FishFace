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
        self.mask = None
    
    def setImage(self, image, copyCvMat=False):
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

        self.mask = None

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
        root.title("image display - click to close")
        
        def kill_window(event):
            root.destroy()
        
        root.bind("<Button>", kill_window)
        
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
            se = cv.CreateStructuringElementEx(2*thickener+1, 2*thickener+1,
                                                thickener, thickener,
                                                 cv.CV_SHAPE_ELLIPSE)
            cv.Dilate(out,out,se)
        
        if returnMat:
            return out
        else:
            self.mask = out
        
    def mask2image(self):
        self.setImage(self.mask)
    
    def image2mask(self):
        self.mask = self.grayImage(returnMat=True)   
        
    def blankMask(self):
        self.mask = self.blankCopy()

    def blankCopy(self, mode='L'):
        if mode=="RGB":
            mode=cv.CV_8UC3
        else:
            mode=cv.CV_8UC1
        
        blank = cv.CreateMat(self.cvmat.rows, self.cvmat.cols, mode)
        cv.SetZero(blank)
        return blank

    def deltaImage(self, calImage, threshold=40, returnMat=False):
        """Subtracts the provided calImage from my image, then thresholds
        and stores/returns the result."""
        
        cg = calImage.grayImage(returnMat=True)
        sg = self.grayImage(returnMat=True)
        
        diff = self.blankCopy(mode="L")
        
        cv.AbsDiff(cg,sg,diff)
        
        if returnMat:
            return diff
        else:
            self.cvmat = diff
            return None
            
    def grayImage(self, returnMat=False, method=0):
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
                
    def largestObjectInMask(self, mask=None, returnMat=False):
        pass




class ImageInitError(Exception):
    pass

class ImageMismatchError(Exception):
    pass

class ImageProcessError(Exception):
    pass
