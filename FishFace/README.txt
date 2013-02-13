=========
Fish Face
=========

Fish Face will endeavor to analyze captured images of a plecostomus in a
water flume and determine which way it is facing relative to the flow.

STATUS
======
Getting there.  I've managed to isolate the fish using a calibration image
containing no fish and basic image processing techniques.  Basically, I've
reduced the entire image of the fish to just the silhouette.  Unfortunately,
the outer shape is all I can really count on, because reportedly the sucker
fish's colors can shift.  I'm currently looking into how to identify the
orientation of the fish using only that outline.

Things I'm considering as possible ways to accomplish that:
* Using training data and statistical techniques.
* Graph theory applied to the contours of the morphological skeleton.
* Analysis of the convex hull.
* Convolution with specially-crafted filters.
* Some combination of the above.

ROUGH PLAN
==========
Version 1.0 will be a command-line application with batch processing.
Version 2.0 will have a GUI and better (i.e. extant) documentation.