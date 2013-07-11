try:
    import numpy as np
except ImportError:
    print "Couldn't import numpy."
    raise

try:
    import cv2.cv as cv
    import cv2
except ImportError:
    print "Couldn't import OpenCV."
    raise

class Marker():
    def __init__(self):
        self.array = np.zeros((750,1000,3), dtype=np.int32)

        self.triangle = np.array([[0,0], [300,150], [0,300]], dtype=np.int32)
        self.square = np.array([[0,0], [300,0], [300,300], [0,300]], dtype=np.int32)
        self.house = np.array([[150,0], [300,100], [300,200], [0,200], [0,100]], dtype=np.int32)
        self.chevron = np.array([[0,125], [300,0], [200,125], [300,250]], dtype=np.int32)


    def marker1(self):

        triangle = (self.triangle + (100,100)).astype('int32')
        square = (self.square + (600,100)).astype('int32')
        house = (self.house + (600,500)).astype('int32')
        chevron = (self.chevron + (100,450)).astype('int32')

        cv2.fillPoly(self.array,[triangle],(255,255,255))
        cv2.fillPoly(self.array,[square],(255,255,255))
        cv2.fillPoly(self.array,[house],(255,255,255))
        cv2.fillPoly(self.array,[chevron],(255,255,255))

