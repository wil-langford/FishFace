#!/usr/bin/env python

import numpy as np
import cv
import time

class Frame:
    def __init__(self, image):
        self.setImage(image)
        self.mask = None
        self.gray_image = None
    
    def newImage(self, image):
        """Object is getting a new image.  If it's already an OpenCV Mat,
        just store it.  Otherwise, try to convert it from numpy.array or
        load it from a filename string."""
        if(type(image)==np.ndarray):
            if image.dtype==np.int16:
                self.image = image
            else:
                self.image = np.int16(image)
        elif(type(image)==str):
            self.image = np.int16(Image.open(image).convert('RGB'))
        else:
            raise ImageInitError("newImage requires a numpy array or filename.")

        
        
        