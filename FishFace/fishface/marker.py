import math
from numpy.core.tests.test_unicode import test_create_values_2_ucs2

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

class Marker():
    def __init__(self):
        """Initialization of the object and hard coded definition of the shapes used in the marker.
        """
        self.array = None
        self.rawShapes = dict()

        # These are the definitions of the triangles used in the marker.
        # The vertices are given in fractions of the full width and height
        # of the marker image.  For example, [0.0, 0.0] is the upper-left
        # corner and [1.0, 1.0] is the lower-right corner.

        # The shapes are defined first, and then they are added to separate
        # offset values to yield the actual coordinates.

        # Since these are hard-coded, no checking is done during this process.
        # If you change them, please make sure you check that the sum of each
        # coordinate and offset is between 0 and 1.

        self.rawShapes['triangles'] =np.array([
                [[ 0.        ,  0.        ],  # triangle 1 shape
                 [ 0.0625    ,  0.08333333],
                 [ 0.        ,  0.33333333]],

                [[ 0.        ,  0.33333333],  # triangle 2 shape
                 [ 0.0625    ,  0.        ],
                 [ 0.0625    ,  0.33333333]],

                [[ 0.03125   ,  0.        ],  # triangle 3 shape
                 [ 0.1875    ,  0.08333333],
                 [ 0.        ,  0.16666667]],

                [[ 0.09375   ,  0.        ],  # triangle 4 shape
                 [ 0.15625   ,  0.16666667],
                 [ 0.        ,  0.20833333]]
            ], dtype=np.float)

        offsets = np.array ([
                [ 0.25      ,  0.33333333],   # triangle 1 offset
                [ 0.6875    ,  0.33333333],   # triangle 2 offset
                [ 0.375     ,  0.58333333],   # triangle 3 offset
                [ 0.46875   ,  0.25      ]    # triangle 4 offset
            ], dtype=np.float)

        for i, triangle in enumerate(self.rawShapes['triangles']):
            self.rawShapes['triangles'][i] = triangle + offsets[i]
            # The triangle contains points in (x,y) form.  We need (y,x) form.
            np.roll(self.rawShapes['triangles'][i], 1, axis=0)


        # The border is defined here using the same fractional coordinate system
        # as above. The outer edge of the border is defined first, and the "hole"
        # that will contain the triangles is defined second.

        self.rawShapes['border'] = np.array([
             [[ 0.        ,  0.        ], # outer border
              [ 1.        ,  0.        ],
              [ 1.        ,  1.        ],
              [ 0.        ,  1.        ]],

             [[ 0.15625   ,  0.20833333], # inner border aka "hole"
              [ 0.84375   ,  0.20833333],
              [ 0.84375   ,  0.79166667],
              [ 0.15625   ,  0.79166667]]
            ], dtype=np.float)

    def setMarker(self, imageSize=(1600,1200), bgColor=255, fgColor=0):
        """Setup the marker.  By default the marker will be 1600x1200, with a white background and a black
        foreground.
        """


        imageSizeScale = np.array(imageSize, dtype=np.float)

        # We have to reverse the X and Y sizes for numpy's benefit.
        self.array = np.ones((imageSize[1], imageSize[0]), dtype=np.uint8) * bgColor

        self.shapes = dict()

        # Turn the fractional coordinates of the triangles in self.rawShapes['triangles'] into
        # actual coordinates now that we know the size of the image.
        self.shapes['triangles'] = [
            (triangle * imageSizeScale).astype('int32')
            for triangle in self.rawShapes['triangles']
        ]

        # Turn the fractional coordinates of the points in self.rawShapes['border'] into
        # actual coordinates now that we know the size of the image.
        self.shapes['border'] = [
            (border * imageSizeScale).astype('int32')
            for border in self.rawShapes['border']
        ]

        # Actually draw the shapes in the image.
        cv2.fillPoly(self.array, self.shapes['triangles'], fgColor)
        cv2.fillPoly(self.array, self.shapes['border'], fgColor)


    def findMarkerPoints(self, frame, threshold = 30, cropEdges = 0.35,
                         outerHullTolerance = 50, innerPolyTolerance = 5,
                         matchScoreThreshold=0.5, minimumTriangleArea=5000):

        # We are working with IR images, so color is meaningless.  Make sure we've got a single-channel image.
        frame.applyGrayImage()

        Y, X = frame.data['spatialShape']

        # Sample every tenth pixel in the image after chopping cropEdges off of each side, and find the
        # median color of all of those pixels.
        medianColor = np.median(frame.array[
            Y * cropEdges : Y * (1-cropEdges) : 10,
            X * cropEdges : X * (1-cropEdges) : 10
        ])

        # Filter out all of the pixels that aren't within threshold color values from the medianColor.
        # The [1] is because we just want the filtered array, not the autodetermined threshold value that
        # some of the snootier thresholding algorithms provide.
        filteredArray = cv2.threshold(
            cv2.absdiff(frame.array, medianColor),
            threshold, 255, cv2.THRESH_BINARY_INV
        )[1]

        # # Look for the rectangular "hole" in the border.
        # # Work with a copy of filteredArray because cv2.findContours apparently alters its input array.
        # # [1] because we just want the contours and [0] because we just want the first one.
        # #
        # # The current implementation doesn't use the border or the hole for alignment, but
        # # this was kind of a pain to get working so I'm keeping it around for sentimental reasons.
        # # Also it may be useful someday, but mainly it's sentiment.
        # outerContours = cv2.findContours(filteredArray.copy(),
        #                                  mode=cv2.RETR_EXTERNAL,
        #                                  method=cv2.CHAIN_APPROX_SIMPLE
        #                                  )[1][0]
        # outerHull = cv2.approxPolyDP(cv2.convexHull(outerContours),outerHullTolerance,True)
        # box = cv2.boxPoints(cv2.minAreaRect(outerHull))

        # Find all of the contours in the image.
        # Work with a copy of filteredArray because cv2.findContours apparently alters its input array.
        # The [1] is because we don't care about the contour hierarchy, just the contours.
        allContours = cv2.findContours(filteredArray.copy(),
                            mode=cv2.RETR_LIST, method=cv2.CHAIN_APPROX_SIMPLE)[1]

        # Build a list of polygons approximated from the contours found above.
        polygons = []
        for ctr in allContours:
            polygons.append(cv2.approxPolyDP(ctr, innerPolyTolerance, True))

        # Snip out the bit we need from the polygons approximated above, rewriting the polygons
        # list in a better format as we go.
        polygons = [
            [list(point[0]) for point in shape]
            for shape in polygons
        ]

        # Pick out all the triangles.
        triangles = [polygon for polygon in polygons if len(polygon)==3]

        # To be used later.  Defined here to avoid redundant redefinitions later.
        # Just the rotational symmetries, please.
        symmetries = [np.array(x) for x in
            [[0,1,2], [1,2,0], [2,0,1]]
        ]

        # The goal is in sight.  We now build the list of corresponding points that are
        # matched between the camera image and the marker.
        matchedPoints = []

        # For each known marker triangle, we'll try to match a found triangle from the image.
        for known in self.shapes['triangles']:
            matchScores = []
            for matchMe in triangles:
                # Current OpenCV version doesn't have the proper method constants defined, so
                # I'm hard coding in the value I want: method=1.  The "parameter" is meaningless,
                # but apparently required.
                matchScore = cv2.matchShapes(np.array(known),
                                             np.array(matchMe),
                                             method=1, parameter=0.0)
                matchScores.append(matchScore)

            # If we have at least one found triangle that is a pretty good match for the known triangle, then...
            if min(matchScores) < matchScoreThreshold:
                # ... let found be the best match.
                found = np.array(triangles[matchScores.index(min(matchScores))])
                orderedCorners = []

                if cv2.moments(found)['m00'] > minimumTriangleArea:
                    foundAnglesRaw = np.array(self.anglesFromTriangleVertices(found))
                    knownAngles = np.array(self.anglesFromTriangleVertices(known))

                    minScore = None
                    for symmetry in symmetries:
                        # Index the angles numpy array with the symmetry numpy array to "rotate" it.
                        foundAngles = foundAnglesRaw[symmetry]

                        score = sum([(a-b)**2 for (a,b) in zip(foundAngles, knownAngles)])

                        if minScore is None:
                            minScore = score

                        # If we have a new minimum (i.e. better) score, then remember that this arrangement of
                        # found triangle corners was the best match.
                        if minScore >= score:
                            minScore = score
                            orderedCorners = found[symmetry]

                # Add the corresponding (found, known) coordinate pairs to the list of matched points.
                if len(orderedCorners) > 0:
                    matchedPoints.extend(zip(orderedCorners.tolist(), known.tolist()))

        return matchedPoints


    def findDeltaImage(self, frame):
        """
        Finds the marker in the input frame, maps it spatially to the stored marker, then
        returns the absolute difference between the stored marker and the mapped input.
        """

        # FIXME: still needs to do color matching - waiting on camera-specific calibration for that

        matchedPoints = self.findMarkerPoints(frame)

        if len(matchedPoints) >=6:
            # Python idioms to "unzip" the zipped matchPoints list.
            srcPoints = np.float32(zip(*matchedPoints)[0])
            dstPoints = np.float32(zip(*matchedPoints)[1])

            # frcopy = frame.copy()
            # frcopy.drawCirclesAtPoints({'points':srcPoints, 'circleRadius':10})
            # frcopy.onScreen({'delayAutoClose':0})
            #
            # xdmin = np.amin(dstPoints[:,0])
            # ydmin = np.amin(dstPoints[:,1])
            # xsmin = np.amin(srcPoints[:,0])
            # ysmin = np.amin(srcPoints[:,1])
            #
            # print "found {} matched points".format(len(srcPoints))
            # for pair in matchedPoints:
            #     pr = pair - np.array([[xsmin,ysmin],[xdmin, ydmin]])
            #     print pr[0], pr[1]

            homography = cv2.findHomography(srcPoints,dstPoints)[0]

            arraySize = (self.array.shape[1], self.array.shape[0])

            srcArray = frame.array.astype(np.float64) / 255
            dstArray = (cv2.warpPerspective(srcArray, homography, arraySize) * 255).astype(np.uint8)

            diffArray = cv2.absdiff(dstArray, self.array)
        else:
            diffArray = np.ones(frame.array.shape, dtype=np.uint8) * 255

        return diffArray

    def anglesFromTriangleVertices(self, vertices):
        """
        A utility method that, given a list of vertices of a triangle, will give you a list of the
        angles corresponding to those vertices.
        """
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