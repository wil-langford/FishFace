import sys
import os
import shutil
import datetime
import time

sys.path.append(os.path.join('..','fishface'))
import capture, imageframe, hopper

class FFiPySupport:

    INFO = 0
    WARN = 1
    ERR = 2
    FINAL = -1
    CHECKPOINT = FINAL

    PREFIX = {
            INFO: '[INFO]',
            WARN: '[\x1b[31mWARNING\x1b[0m]',
            ERR: '[\x1b[31mERROR\x1b[0m]',
            'OK': '[\x1b[32mOK\x1b[0m]'
        }

    DATE_FORMAT = "%Y-%m-%d-%H%M%S"

    def __init__(self):
        self.flag = self.INFO

    def msg(self, message, messageType=INFO):

        if messageType == self.FINAL:
            if self.flag == self.INFO:
                print "{} {}".format(self.PREFIX['OK'], message)
            else:
                self.msg(message, self.flag)

            self.reset()

        else:
            print "{} {}".format(self.PREFIX[messageType], message)

            self.flag = max(self.flag, messageType)

    def reset(self):
        self.flag = self.INFO

    def ephemeraDirectory(self):

        try:
            ephPath = os.path.join(".","ephemera")
            if os.path.exists(ephPath):
                if os.path.isdir(ephPath):
                    shutil.rmtree(ephPath)
                else:
                    os.remove(ephPath)
            os.mkdir(ephPath)
            self.msg("Reset ephemera directory.")
        except:
            self.msg("Couldn't reset ephemera directory.", self.WARN)

    def dtg(self, timestamp=None):
        """Returns a date-time-group according to the DATE_FORMAT string specified at the top of this file.
        """

        if timestamp is None:
            timestamp = time.time()

        dt = datetime.datetime.fromtimestamp(timestamp)

        return dt.strftime(self.DATE_FORMAT)

    def grabImage(self, filename, isCal=False, lightType='IR'):
        if isCal:
            try:
                if os.path.exists(self.oldCalFilename):
                    os.remove(self.oldCalFilename)
                self.oldCalFilename = filename
            except:
                pass

        try:
            frame = imageframe.Frame(self.cam.grabFrame())
            frame.saveImageToFile(filename)
        except:
            self.cam = capture.Camera(lightType=lightType)
            frame = imageframe.Frame(self.cam.grabFrame())
            frame.saveImageToFile(filename)
            del self.cam


    def grabDataFrames(self, dataSeries, numData, expDir, dataPrefix, interval):
        for i in range(numData):
            self.wakeUpAt(time.time() + interval)
            dataFilename = os.path.join(expDir,
                                        "{}-{:03d}-{}.jpg".format(dataPrefix, dataSeries, self.dtg()))

            self.grabImage(dataFilename)

            self.goToSleep()
            self.msg("Grabbed image number {} in data series {}.".format(i, dataSeries))

    def wakeUpAt(self, timestamp):
        self.wakeUpTimestamp = timestamp

    def goToSleep(self):
        if self.wakeUpTimestamp is not None:
            while time.time() < self.wakeUpTimestamp:
                time.sleep(self.wakeUpTimestamp - time.time())
            self.wakeUpTimestamp = None