import copy
import math

try:
    import numpy as np
except ImportError:
    print "Couldn't import numpy."
    raise

try:
    import cv2
except ImportError:
    print "Couldn't import OpenCV."
    raise

import imageframe
import hopper

class Marker():
    def __init__(self):
        self.array = None

    def setMarker1(self, bgColor=255, fgColor=0):
        self.array = np.ones((750,1000), dtype=np.uint8)*bgColor

        triangle = (np.array([[0,0], [300,150], [0,300]]) + (100,100)).astype('int32')
        square = (np.array([[0,0], [300,0], [300,300], [0,300]]) + (600,100)).astype('int32')
        house = (np.array([[150,0], [300,100], [300,200], [0,200], [0,100]]) + (600,500)).astype('int32')
        chevron = (np.array([[0,125], [300,0], [200,125], [300,250]]) + (100,450)).astype('int32')

        cv2.fillPoly(self.array,[triangle],fgColor)
        cv2.fillPoly(self.array,[square],fgColor)
        cv2.fillPoly(self.array,[house],fgColor)
        cv2.fillPoly(self.array,[chevron],fgColor)

    def setMarker2(self, bgColor=255, fgColor=0):
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

    def setMarker3(self, bgColor=255, fgColor=0):
        self.array = np.ones((1200,1600), dtype=np.uint8)*bgColor

        self.shapes = dict()

        self.shapes['triangles'] = []

        self.shapes['triangles'].append((np.array([[0,0], [100,100], [0,400]]) + (400,400)).astype('int32'))
        self.shapes['triangles'].append((np.array([[0,400], [100,0], [100,400]]) + (1100,400)).astype('int32'))
        self.shapes['triangles'].append((np.array([[50,0], [300,100], [0,200]]) + (600,700)).astype('int32'))
        self.shapes['triangles'].append((np.array([[150,0], [250,200], [0,250]]) + (750,300)).astype('int32'))

        self.shapes['border'] = [
            np.array([[0,0], [1600,0], [1600,1200], [0,1200]]).astype('int32'),
            np.array([[250,250], [1350,250], [1350,950], [250,950]]).astype('int32')
            ]


        cv2.fillPoly(self.array, self.shapes['border'], fgColor)
        cv2.fillPoly(self.array, self.shapes['triangles'], fgColor)

    def findMarker3(self, frame, threshold=30, cropEdges=0.25, outerHullTolerance=50, innerPolyTolerance=5):
        frame.applyGrayImage()

        Y = frame.data['spatialShape'][0]
        X = frame.data['spatialShape'][1]

        # take every tenth pixel in the middle 60%x60% of the image...
        colorSamples = frame.array[Y*cropEdges:Y*(1-cropEdges):10, X*cropEdges:X*(1-cropEdges):10]

        # ... and find the median of those values
        median = np.median(colorSamples)

        ar = cv2.threshold(cv2.absdiff(frame.array,median),threshold,255,cv2.THRESH_BINARY_INV)[1]

        outerContours = cv2.findContours(ar.copy(), mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)[1][0]

        outerHull = cv2.approxPolyDP(cv2.convexHull(outerContours),outerHullTolerance,True)
        box = cv2.boxPoints(cv2.minAreaRect(outerHull))

        allContours = cv2.findContours(ar.copy(), mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)[1]

        polygons = []

        for ctr in allContours:
            polygons.append(cv2.approxPolyDP(ctr,innerPolyTolerance,True))

        polygons = [[list(point[0]) for point in shape] for shape in polygons]

        triangles = [polygon for polygon in polygons if len(polygon)==3]

        matchedPoints = []

        for known in self.shapes['triangles']:
            matchScores = []
            for triangle in triangles:
                matchScore = cv2.matchShapes(np.array(known),
                        np.array(triangle),
                        method=1, parameter=0.0)
                matchScores.append(matchScore)

            if min(matchScores) < 1:
                found = np.array(triangles[matchScores.index(min(matchScores))])

                foundAnglesRaw = np.array(self.anglesFromTriangleVertices(found))
                knownAngles = np.array(self.anglesFromTriangleVertices(known))

                symmetries = [np.array(x) for x in
                        [[0,1,2], [1,2,0], [2,0,1], [0,2,1], [2,1,0], [1,0,2]]
                        ]

                minScore = None
                for symmetry in symmetries:
                    foundAngles = foundAnglesRaw[symmetry]

                    score = sum([(a-b)**2 for (a,b) in zip(foundAngles, knownAngles)])

                    if minScore is None:
                        minScore = score

                    if minScore >= score:
                        minScore = score
                        orderedCorners = found[symmetry]

                matchedPoints.extend(zip(orderedCorners.tolist(), known.tolist()))
                # print "*** {}".format(matchedPoints)


        # scaleneScores = []
        #
        # for triangle in triangles:
        #     scaleneScores.append(
        #         cv2.matchShapes(np.array(self.shapes['scalene']),
        #         np.array(triangle),
        #         method=1, parameter=0.0)
        #         )
        #
        # fs = np.array(triangles[scaleneScores.index(min(scaleneScores))])
        #
        # ks = np.array(self.shapes['scalene'][0])
        #
        # fsa = np.array(self.anglesFromTriangleVertices(fs))
        #
        # ksa = np.array(self.anglesFromTriangleVertices(ks))
        #
        # spossibles = []
        #
        # for i in range(3):
        #     spossibles.append([np.roll(fs,i, axis=0),np.roll(fsa,i)])
        #     spossibles.append([np.roll(fs[::-1],i, axis=0),np.roll(fsa[::-1],i)])
        #
        #
        # minsScore = 1000000
        # for sp in spossibles:
        #     score = sum([(a-b)**2 for (a,b) in zip(sp[1],ksa)])
        #     if minsScore > score:
        #         minsScore = score
        #         sVerts = sp[0].tolist()
        #
        # points = zip(rVerts, kr.tolist())
        # points.extend(zip(sVerts,ks.tolist()))

        return matchedPoints


    def anglesFromTriangleVertices(self, vertices):
        vertices = np.array(vertices)

        vects = []
        for i in range(3):
            vects.append(vertices[i] - vertices[(i+1)%3])

        sideLengths = [math.hypot(x[0], x[1]) for x in vects]

        def angleFromSides(a, b, c):
            angle = math.acos((a**2 + b**2 - c**2)/(2*a*b))
            return math.degrees(angle)

        angles = []
        for i in range(3):
            angles.append(angleFromSides(sideLengths[i], sideLengths[(i+1) % 3], sideLengths[(i+2) % 3]))

        return angles






