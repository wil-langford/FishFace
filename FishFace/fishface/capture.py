#!/usr/bin/env python
"""
The capture module provides camera interface objects for FishFace.

Supported cameras:
* The IDS 1461 camera in the lab that appears to be a prototype and quite possibly unique.

This is a problem, so I'm going to add some support for the more general, non-proprietary
camera interface provided by Linux.  (V4L?  Something else?  We'll see.)
"""

try:
    import ueye
except ImportError:
    print "Couldn't find the pyueye library.  Is it installed?"
    raise

try:
    import cv2
except ImportError:
    print "The capture module needs OpenCV."
    raise



class IDSCamera():
    """
This object provides IDS-specific camera interface features.
    """

    def __init__(self, lightType=None):
        self.cam = ueye.Cam()

        self.resetToDefault()

        if lightType == 'visible':
            self.setColorCorrection()
            self.setColorMode(mode=ueye.CM_MONO8)
            self.camPixClock = self.cam.SetPixelClock(25)
            self.camFrameRate = self.cam.SetFrameRate(6)
            self.exposureTime = self.cam.SetExposureTime(130)
            self.setHardwareGain(30)

        if lightType == 'IR' or lightType is None:
            self.setColorCorrection()
            self.setColorMode(mode=ueye.CM_MONO8)
            self.camPixClock = self.cam.SetPixelClock(25)
            self.camFrameRate = self.cam.SetFrameRate(6)
            self.exposureTime = self.cam.SetExposureTime(80)
            self.setHardwareGain(100)

    def resetToDefault(self):
        self.cam.ResetToDefault()

    def setColorMode(self, mode=ueye.CM_BGR8_PACKED):
        if self.cam.SetColorMode(mode) != mode:
            raise IDSCameraError("Couldn't set color mode.")

    def setColorCorrection(self,mode=ueye.CCOR_DISABLE):
        if self.cam.SetColorCorrection(mode) != ueye.SUCCESS:
            raise IDSCameraError("Couldn't set color correction on camera.")

    def setHardwareGain(self, gain=0):
        if gain < 0 or gain > 100:
            raise IDSCameraError("Gain must be between 0 and 100 (inclusive.)")

        if self.cam.SetHardwareGain(gain,0,0,0) != ueye.SUCCESS:
            raise IDSCameraError("Couldn't set hardware gain on camera.")

    def grabFrame(self):
        ar = self.cam.GrabImage()

        return ar

class OpenCVCamera():
    """
NOT FULLY IMPLEMENTED; DO NOT USE
This object provides generic OpenCV camera interface features.

It currently uses the default camera with no provision to select among
multiple cameras.

This object is currently not fully implemented, and should not yet be used.
I thought at one point that the IDS camera would not work, and started working
on more generic capture routines.
    """

    def __init__(self, lightType=None):
        self.cam = cv2.VideoCapture()
        self.cam.open(-1)

        if lightType is None:
            pass

    def grabFrame(self):
        ar = self.cam.read()[1]

        return ar

class Camera():
    """
The Camera object is FishFace's generic view of all supported cameras.  Its
primary method is grabFrame().
    """

    def __init__(self, camType='IDS', lightType=None):
        self.method=camType

        if camType=='IDS':
            self.cam = IDSCamera(lightType = lightType)
        elif camType=='OpenCV':
            self.cam = OpenCVCamera(lightType = lightType)
        else:
            raise CaptureError("Unsupported camera type: {}".format(camType))


    def grabFrame(self):
        return self.cam.grabFrame()




class CaptureError(Exception):
    pass

class IDSCameraError(Exception):
    pass