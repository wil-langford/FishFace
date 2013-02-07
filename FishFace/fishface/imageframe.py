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
    
    def setImage(self, image, copyImage=False):
        """Object is getting a new image.  If it's already an OpenCV Mat,
        just store it.  Otherwise, try to convert it from numpy.array or
        load it from a filename string."""
        
        # Depending on file type, use various initializers
        if (type(image)==cv.cvmat):
            if copyImage:
                self.cvmat = cv.CreateMat(image.rows,image.cols,image.type)
                cv.Copy(image, self.cvmat)
            else:
                self.cvmat = image

        elif(type(image)==np.ndarray):
            self.setImageFromNumpyArray(image)

        elif(type(image)==str):
            self.setImageFromFile(image)
        
        else:
            raise ImageInitError("newImage requires a cvMat, numpy array, or filename string.")

        self.mask = None

    def setImageFromFile(self,filename):
        """Get image from file and store as CvMat."""
        if os.path.isfile(filename):
            self.cvmat = cv.LoadImageM(filename)
        else:
            raise ImageInitError("File not found: {}".format(filename))

    def setImageFromNumpyArray(self,image):
        """Convert Numpy array to CvMat."""
        if image.dtype==np.uint8:
            self.cvmat = cv.fromarray(image)
        else:
            raise ImageInitError("Image must have 8 bits per channel.")

    def saveImageToFile(self, filename):
        """Save the image to a file."""
        cv.SaveImage(filename, self.cvmat)
    
    def onScreen(self, scaleDownFactor=2):
        """I need something to display these things for debugging."""
        
        root = tk.Tk()
        root.title("image display - click to close")
        
        def kill_window(event):
            root.destroy()
        
        root.bind("<Button>", kill_window)
        
        fmts = ["L","RGB"]
        im = Image.fromstring(
                              fmts[self.cvmat.channels-2],
                              cv.GetSize(self.cvmat),
                              self.cvmat.tostring(),
                              "raw",
                              "BGR",
                              self.cvmat.width*3,
                              0
                              )
        
        im = im.resize((im.size[0]//scaleDownFactor, im.size[1]//scaleDownFactor))
        
        photo = ImageTk.PhotoImage(im)
        
        lbl = tk.Label(root, image=photo)
        lbl.image = photo
        lbl.pack()
        
        root.mainloop()

        
class ImageInitError(Exception):
    pass

class ImageMismatchError(Exception):
    pass
