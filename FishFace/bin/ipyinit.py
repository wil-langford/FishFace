import ipythonsupport
import sys, os, time
import cv2
import IPython.display as ipd

ips = ipythonsupport.FFiPySupport()
ips.msg("Starting initial environment setup.")
sys.path.append(os.path.join('..','fishface'))
try:
    import capture, imageframe, hopper, poser
    ips.msg("Imported FishFace Libraries.")
except:
    ips.msg("Couldn't import the FishFace libraries.  You may need to reinstall FishFace.", ips.ERR)
# ips.ephemeraDirectory()
ips.msg("Initial environment setup complete.", ips.FINAL)