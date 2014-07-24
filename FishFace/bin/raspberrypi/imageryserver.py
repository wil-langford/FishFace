#!/usr/bin/env python

"""
This module is a small program intended to run on a Raspberry Pi with
attached camera module.  It sends one full-resolution frame per second
to any client that requests imagery via a Pyro4 interface.
"""

import picamera
import Pyro4
import threading
import time
import io
import numpy as np

Pyro4.config.HOST = 'mystaticip'
Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED.add('pickle')

class ImageryServer(object):
    """
    """

    def __init__(self):
        self.camera = picamera.PiCamera()
        self.camera.resolution = (2048,1536)

        self.pyro_daemon = Pyro4.Daemon()
        self.pyro_uri = self.pyro_daemon.register(self)

        self.nameserver = Pyro4.locateNS()
        self.nameserver.register("fishface.raspi_imagery_server", self.pyro_uri)

        self._current_frame = None

    def _capture_new_current_frame(self):
        stream = io.BytesIO()

        self.camera.capture(
                            stream,
                            format='jpeg'
        )

        data = np.fromstring(stream.getvalue(), dtype=np.uint8)
        self._current_frame = data

    def get_current_frame(self):
        return self._current_frame
        print "Served frame."

    def awb_mode(self, mode=None):
        if mode is None:
            return self.camera.awb_mode

        if mode in ['off', 'auto']:
            self.camera.awb_mode = mode
        else:
            raise Exception("Invalid AWB mode for raspi camera: {}".format(mode))

    def brightness(self, br=None):
        if br is None:
            return self.camera.brightness

        if br>=0 and br<=100:
            self.camera.brightness = br
        else:
            raise Exception("Invalid brightness setting for raspi camera: {}".format(br))


    def run(self):
        def image_capture_loop():
            while True:

                self._capture_new_current_frame()
                time.sleep(1)

        thread = threading.Thread(target=image_capture_loop)
        thread.setDaemon(True)
        thread.start()



def main():
    imagery_server = ImageryServer()

    imagery_server.run()

    imagery_server.pyro_daemon.requestLoop()

    print "exiting"


if __name__ == '__main__':
    main()