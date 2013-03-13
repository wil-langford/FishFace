=========
Fish Face
=========

Fish Face will endeavor to analyze captured images of a plecostomus in a
water flume and determine which way it is facing relative to the flow.

STATUS
======
v1.0 is complete according to the "rough plan" outlined below.  I'm using only
the "longest axis" of the silhouette of the fish at the moment, but this worked
surprisingly well.  It also is consistent with the goal of the experiment for
which FishFace is intended.

---

Unfortunately, the outer shape is all I can really count on, because reportedly
the sucker fish's colors can shift.  If the "longest axis" method currently
used turns out to be insufficient, we'll need to identify the orientation of
the fish using only that outline.

Things I'm considering as possible ways to accomplish that:
* Using training data and statistical techniques.
* Analysis of the extrema of the sums of the axis perpendicular to the longest one.
* Graph theory applied to the contours of the morphological skeleton.
* Analysis of the convex hull.
* Convolution with specially-crafted filters.
* Some combination of the above.

ROUGH PLAN
==========
Version 1.0 will be a command-line application with batch processing.
Version 2.0 will have a GUI and better (i.e. extant) documentation.
