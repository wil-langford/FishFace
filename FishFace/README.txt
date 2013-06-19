=========
Fish Face
=========

Fish Face endeavors to analyze captured images of a plecostomus in a
water flume and determine which way it is facing relative to the flow.

STATUS
======
v1.1 is expected by the end of June, 2013.  The access conflict that we had with
the flume has been resolved, and development is now active again.  The planned GUI
has been tabled for now in favor of improvements to the actual function of the
software.

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
Version 1.1 will have an improved orientation/location determination algorithm.
