import copy

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

import imageframe
import hopper

class Marker():
    def __init__(self):
        self.array = None

    def marker1(self, bgColor=255, fgColor=0):
        self.array = np.ones((750,1000), dtype=np.uint8)*bgColor

        triangle = (np.array([[0,0], [300,150], [0,300]]) + (100,100)).astype('int32')
        square = (np.array([[0,0], [300,0], [300,300], [0,300]]) + (600,100)).astype('int32')
        house = (np.array([[150,0], [300,100], [300,200], [0,200], [0,100]]) + (600,500)).astype('int32')
        chevron = (np.array([[0,125], [300,0], [200,125], [300,250]]) + (100,450)).astype('int32')

        cv2.fillPoly(self.array,[triangle],fgColor)
        cv2.fillPoly(self.array,[square],fgColor)
        cv2.fillPoly(self.array,[house],fgColor)
        cv2.fillPoly(self.array,[chevron],fgColor)

    def marker2(self, bgColor=255, fgColor=0):
        self.array = np.ones((1200,1600), dtype=np.uint8)*bgColor


        triangle1 = (np.array([[0,0], [100,200], [0,400]]) + (400,400)).astype('int32')
        triangle2 = (np.array([[0,400], [100,0], [100,400]]) + (1100,400)).astype('int32')

        border = [
            np.array([[200,200], [1400,200], [1400,1000], [200,1000]]).astype('int32'),
            np.array([[250,250], [1350,250], [1350,950], [250,950]]).astype('int32')
            ]

        cv2.fillPoly(self.array, border, fgColor)

        cv2.fillPoly(self.array, [triangle1], fgColor)
        cv2.fillPoly(self.array, [triangle2], fgColor)

    def marker3(self, bgColor=255, fgColor=0):
        self.array = np.ones((1200,1600), dtype=np.uint8)*bgColor


        triangle1 = (np.array([[0,0], [100,200], [0,400]]) + (400,400)).astype('int32')
        triangle2 = (np.array([[0,400], [100,0], [100,400]]) + (1100,400)).astype('int32')

        border = [
            np.array([[0,0], [1600,0], [1600,1200], [0,1200]]).astype('int32'),
            np.array([[250,250], [1350,250], [1350,950], [250,950]]).astype('int32')
            ]

        cv2.fillPoly(self.array, border, fgColor)

        cv2.fillPoly(self.array, [triangle1], fgColor)
        cv2.fillPoly(self.array, [triangle2], fgColor)


class FindMarker():
    def __init__(self, imageFrame):
        self.frame = imageFrame

    def findMarker3(self, threshold=30):
        self.frame.applyGrayImage()

        Y = self.frame.data['spatialShape'][0]
        X = self.frame.data['spatialShape'][1]

        # take every tenth pixel in the middle 60%x60% of the image...
        colorSamples = self.frame.array[Y*0.2:Y*0.8:10, X*0.2:X*0.8:10]

        # ... and find the median of those values
        median = np.median(colorSamples)

        ar = np.abs(self.frame.array.astype('int16') - median)

        ar = cv2.threshold(ar.astype(np.uint8),threshold,255,cv2.THRESH_BINARY_INV)[1]

        ar2 = ar.astype(np.uint8)

        outer = cv2.findContours(ar, mode=cv.CV_RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)[0]

        outer = cv2.approxPolyDP(outer[0],100,True)

        outer = cv2.minAreaRect(outer)

        return outer, ar2

        # polygons = []
        #
        # for c in ctrs:
        #     polygons.append(cv2.approxPolyDP(c,5,True))
        #
        # polygons = [[list(point[0]) for point in shape] for shape in polygons]
        #
        # polygons = [(polygon, len(polygon)) for polygon in polygons if len(polygon)>1]
        #
        # return polygons











