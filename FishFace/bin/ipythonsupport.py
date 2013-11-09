import sys
import os
import shutil
import datetime
import time
import numpy as np
import cv2

sys.path.append(os.path.join('..','fishface'))
import capture, imageframe, hopper, poser

class FFiPySupport:

    INFO = 0
    WARN = 1
    ERR = 2
    FINAL = -1
    DEBUG = -2
    WRITE = -3
    CHECKPOINT = FINAL

    PREFIX = {
            INFO: '[INFO]',
            WARN: '[\x1b[31mWARNING\x1b[0m]',
            ERR: '[\x1b[31mERROR\x1b[0m]',
            DEBUG: '[DEBUG]',
            'OK': '[\x1b[32mOK\x1b[0m]'
        }

    DATE_FORMAT = "%Y-%m-%d-%H%M%S"

    def __init__(self):
        self.flag = self.INFO
        self.lastSeriesTimestamp = None
        self.wakeUpTimestamp = None

        # This line enables DEBUG output.
        self.debug = False

    def msg(self, message, messageType=INFO):

        if messageType == self.WRITE:
            sys.stdout.write(message)
            return

        if messageType == self.FINAL:
            if self.flag == self.INFO:
                print "{} {}".format(self.PREFIX['OK'], message)
            else:
                self.msg(message, self.flag)

            self.reset()

        else:
            if self.debug or messageType != self.DEBUG:
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

    def dtgRead(self, string):
        return datetime.datetime.strptime(string, self.DATE_FORMAT)


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


    def grabDataSeries(self, dataSeries, numData, expDir, dataPrefix, interval, voltage, lightType='IR'):
        self.msg("Capturing {} data points at {} second intervals.".format(numData, interval))
        self.msg("Accessing camera.")
        self.cam = capture.Camera(lightType=lightType)
        self.msg("Camera accessed.")

        self.msg("Beginning capture of {} images in data series {}.".format(numData, dataSeries))
        self.msg("One dot will print per image captured. (10 dots per group, 10 groups per line.)")

        for i in range(1, numData+1):

            now = time.time()

            if self.lastSeriesTimestamp is not None:
                self.msg("actual interval: {:03f}".format(now - self.lastSeriesTimestamp), self.DEBUG)
                if self.lastSeriesTimestamp + interval > now:
                    self.msg("on time {:03f}".format(self.lastSeriesTimestamp + interval - now), self.DEBUG)
                    self.wakeUpAt(self.lastSeriesTimestamp + interval)
                else:
                    self.msg("overtime {:03f}".format(self.lastSeriesTimestamp + interval - now), self.DEBUG)
                    self.wakeUpAt(now + interval)
            else:
                self.wakeUpAt(now + interval)
            self.lastSeriesTimestamp = now

            dataFilename = os.path.join(expDir, "{}-{:03d}-{:05d}-{}-{:0.2f}V.jpg".format(dataPrefix, dataSeries, i, self.dtg(), voltage))
            self.grabImage(dataFilename)
            self.msg("Grabbed image number {}/{} in data series {}.".format(i, numData, dataSeries), self.DEBUG)

            self.msg('.', self.WRITE)
            if i%100 == 0:
                self.msg('\n', self.WRITE)
            elif i%10 == 0:
                self.msg(' ', self.WRITE)

            self.goToSleep()

        del self.cam
        self.msg('\n', self.WRITE)

        self.msg("Camera closed.")
        self.lastSeriesTimestamp = None

    def wakeUpAt(self, timestamp):
        self.wakeUpTimestamp = timestamp

    def goToSleep(self):
        if self.wakeUpTimestamp is not None:
            while time.time() < self.wakeUpTimestamp:
                time.sleep(self.wakeUpTimestamp - time.time())
            self.wakeUpTimestamp = None

    def listExperimentDirs(self,dataDir):
        root, self.dataDirs, dataFiles = os.walk(dataDir).next()
        self.dataDirs = [os.path.join(root, dir) for dir in self.dataDirs]

        print "*" * 50
        print "Please select an experiment to analyze by number from the list below."
        for i, dir in enumerate(self.dataDirs):
            print "{}: {}".format(i,dir)

    def renderPOI(self, expDirIdx, calPrefix, POI=0):
        experimentDir = self.dataDirs[expDirIdx]
        print experimentDir
        if not os.path.exists(experimentDir):
            self.msg("Selected experiment directory does not exist.", self.ERR)
            return

        try:
            root, dirs, files = os.walk(experimentDir).next()
        except StopIteration:
                pass

        calFiles = [filename for filename in files if filename[:len(calPrefix)] == calPrefix]
        if len(calFiles) == 0:
            self.msg("Could not find a calibration file with the given prefix: {}".format(calPrefix), self.ERR)
            return
        elif len(calFiles) > 1:
            self.msg(
                "Found too many calibration files with prefix: " +
                "{}\nDelete (or rename without the '{}' prefix) all but the one you want to use to proceed.".format(calPrefix,calPrefix),
                self.ERR)
            return
        else:
            calFile = os.path.join(root,calFiles[0])
            cf = imageframe.Frame(calFile)
            self.msg("Using discovered calibration file: {}".format(calFile))

            if POI != 0:
                if len(POI) < 2:
                    self.msg("POI needs to be 0 or a list of points. If it's a list of points, there must be at least 2 points in the list.", self.ERR)
                elif len(POI)==2:
                    POI.append( [POI[0][0], POI[1][1]])
                    POI.insert(1, [POI[1][0], POI[0][1]])

                ctrs = np.array([[POI]])

                cf.drawContours({
                    "contours": ctrs,
                    "filledIn": False,
                    "lineThickness": 8
                })
            else:
                ctrs = None

            displayShape = (640,480)
            cf.applyResize({
                "newshape": displayShape
            })

            outFilename = os.path.join(root,"POI-image.jpg")
            cf.saveImageToFile(outFilename)

            return [outFilename, ctrs]

        return [None, None]

    def analyzeExperiment(self, expDirIdx, calPrefix, dataPrefix, threshold, outFilenamePrefix=None, poiContours=None):
        experimentDir = self.dataDirs[expDirIdx]
        print experimentDir
        if not os.path.exists(experimentDir):
            self.msg("Selected experiment directory does not exist.", self.ERR)
            return

        try:
            root, dirs, files = os.walk(experimentDir).next()
        except StopIteration:
            pass

        calFiles = [filename for filename in files if filename[:len(calPrefix)] == calPrefix]
        if len(calFiles) == 0:
            self.msg("Could not find a calibration file with the given prefix: {}".format(calPrefix), self.ERR)
            return
        elif len(calFiles) > 1:
            self.msg(
                "Found too many calibration files with prefix: " +
                "{}\nDelete all but the one you want to use to proceed.".format(calPrefix),
                self.ERR)
            return
        else:
            calFile = os.path.join(root,calFiles[0])
            calFrame = imageframe.Frame(calFile)
            self.msg("Using discovered calibration file: {}".format(calFile))

        self.msg("Indexing data files.")

        dataFiles = sorted([os.path.join(root,filename) for filename in files
                            if filename[:len(dataPrefix)] == dataPrefix])
        dataFiles.insert(0,"ACTUAL")

        self.msg("Found {} data files to process.".format(len(dataFiles)-1))

        chainProcessList = [
            ('deltaImage', {'calImageFrame': calFrame}),
            ('grayImage', {}),
            ('threshold', {'threshold': threshold}),
            ('closing', {'kernelRadius': 3}),
            ('opening', {'kernelRadius': 3}),
            ('cropToLargestBlob', {}),
            ('findCentroid', {})
        ]

        self.msg("Building hopper chain.")
        HC = hopper.HopperChain(dataFiles, chainProcessList)

        self.msg("Starting hopper chain.")

        if poiContours is not None:
            poiHeader = str(poiContours[0][0]).replace('\n','')
        else:
            poiHeader = "None"

        outFile = None
        if outFilenamePrefix is not None:
            bareDirName = os.path.basename(experimentDir)
            outFilename = "{}_{}_analysis-run-at-{}.csv".format(outFilenamePrefix, bareDirName, self.dtg())
            outFile = open(os.path.join(experimentDir, outFilename), 'w')
            outFile.write('"' +
                '", "'.join([
                    "Data Series",
                    "Serial Number",
                    "Timestamp",
                    "Seconds Since Series Start",
                    "Angle",
                    "Voltage",
                    "Position",
                    "POI Score (POI {})".format(poiHeader),
                    "Original Filename"
                ]) + "\"\n"
            )

        self.msg("One dot will print per image processed. (10 dots per group, 10 groups per line.)")
        i = 0
        startProcessingTimestamp = time.time()

        firstFrameTimestamp = None

        for fr in HC:

            po = poser.Poser(fr.array)
            angle = po.findLongAxis()
            position = fr.data['absoluteCentroid']
            if poiContours is not None:
                poiScore = cv2.pointPolygonTest(poiContours[0],position,True)
            else:
                poiScore = 'NA'

            filename = fr.data['originalFileName']
            filenameParsed = os.path.basename(filename)[:-5].split("-")

            prefix, series, serial, year, month, day, timeString, voltage = filenameParsed
            dt = self.dtgRead('-'.join(filenameParsed[3:7]))
            if firstFrameTimestamp is None:
                firstFrameTimestamp = dt
            timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
            deltaSeconds = (dt - firstFrameTimestamp).total_seconds()

            dataString = '{}, {}, {}, {}, {}, {}, {}, {}, "{}"\n'.format(series, serial, timestamp, deltaSeconds, angle, voltage, position, poiScore, filename)

            if outFile is not None:
                outFile.write(dataString)
                messageTarget = self.DEBUG
            else:
                messageTarget = self.INFO

            self.msg(dataString, messageTarget)

            self.msg('.', self.WRITE)

            i=i+1
            if i%100 == 0:
                self.msg('\n', self.WRITE)
            elif i%10 == 0:
                self.msg(' ', self.WRITE)

        outFile.close()

        self.msg('\n', self.WRITE)
        self.msg("Data analysis complete.", self.FINAL)
        pTime = time.time() - startProcessingTimestamp
        self.msg("Processing took {} total seconds ({} seconds per image.)".format(pTime, pTime / i))

        if outFile is not None:
            self.msg("Results have been written to the output file: {}".format(outFilename))



