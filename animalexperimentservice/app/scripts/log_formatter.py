#!/usr/bin/env python
# coding: utf8

# Copyright 2016 SoftBank Robotics

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# 	http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Project     : None
# Author      : Maxime Busy
# Departement : Innovation Software

import sys
import os
import time
from threading import Thread
from termcolor import colored, cprint

DEBUG    = 0
INFO     = 1
WARNING  = 2
ERROR    = 3
CRITICAL = 4

class LogFormatter(Thread):
    """
    Class printing the colored logs
    """

    def __init__(self, filename, level=DEBUG):
        """
        Constructor

        Parameters :
                filename - The name of the log file (that will be displayed on
                the fly)
                level - The level of the logs to be seen, by priority. For
                instance, if log_formatter.INFO is specified, the formatter
                will display the logs of the INFO level and above

        """
        Thread.__init__(self)

        self.level                 = level

        self.debugTxtColor         = "red"
        self.infoTxtColor          = "yellow"
        self.warningTxtColor       = "red"
        self.errorTxtColor         = "blue"
        self.criticalTxtColor      = "white"

        self.debugTxtHighlights    = "on_green"
        self.infoTxtHighlights     = "on_blue"
        self.warningTxtHighlights  = "on_yellow"
        self.errorTxtHighlights    = "on_red"
        self.criticalTxtHighlights = "on_red"

        self.debugTxtAttributes    = []
        self.infoTxtAttributes     = []
        self.warningTxtAttributes  = ["bold"]
        self.errorTxtAttributes    = ["blink", "bold"]
        self.criticalTxtAttributes = ["blink", "bold"]

        self.readLogs              = True
        self.filename              = filename


    def formatAndDisplayLogs(self, filename):
        """
        Methode used to format and display the logs at the end of the program

        Parameters :
                filename - The name of the log file
        """

        with open(filename, 'r') as logFile:
            logs = logFile.readlines()
            logFile.close()

        for logLine in logs:
            formattedLogLine = logLine.split()

            if formattedLogLine[0] == 'DEBUG' and self.level < 1:
                print colored(formattedLogLine[0], self.debugTxtColor, self.debugTxtHighlights, attrs=self.debugTxtAttributes) + "   " + " ".join(formattedLogLine[1:])

            elif formattedLogLine[0] == 'INFO' and self.level < 2:
                print colored(formattedLogLine[0], self.infoTxtColor, self.infoTxtHighlights, attrs=self.infoTxtAttributes) + "   " + " ".join(formattedLogLine[1:])

            elif formattedLogLine[0] == 'WARNING' and self.level < 3:
                print colored(formattedLogLine[0], self.warningTxtColor, self.warningTxtHighlights, attrs=self.warningTxtAttributes) + "   " + " ".join(formattedLogLine[1:])

            elif formattedLogLine[0] == 'ERROR' and self.level < 4:
                print colored(formattedLogLine[0], self.errorTxtColor, self.errorTxtHighlights, attrs=self.errorTxtAttributes) + "   " + " ".join(formattedLogLine[1:])

            elif formattedLogLine[0] == 'CRITICAL':
                print colored(formattedLogLine[0], self.criticalTxtColor, self.criticalTxtHighlights, attrs=self.criticalTxtAttributes) + "   " + " ".join(formattedLogLine[1:])



    def followAndDisplayLogs(self):
        """
        Method used to format and display the logs on the fly
        """

        logFile = open(self.filename, 'r')

        logFile.seek(0.2)

        while self.readLogs:
            logLine = logFile.readline()
            
            if not logLine:
                time.sleep(0.1)
                continue

            formattedLogLine = logLine.split()

            if formattedLogLine[0] == 'DEBUG' and self.level < 1:
                print colored(formattedLogLine[0], self.debugTxtColor, self.debugTxtHighlights, attrs=self.debugTxtAttributes) + "   " + " ".join(formattedLogLine[1:])

            elif formattedLogLine[0] == 'INFO' and self.level < 2:
                print colored(formattedLogLine[0], self.infoTxtColor, self.infoTxtHighlights, attrs=self.infoTxtAttributes) + "   " + " ".join(formattedLogLine[1:])

            elif formattedLogLine[0] == 'WARNING' and self.level < 3:
                print colored(formattedLogLine[0], self.warningTxtColor, self.warningTxtHighlights, attrs=self.warningTxtAttributes) + "   " + " ".join(formattedLogLine[1:])

            elif formattedLogLine[0] == 'ERROR' and self.level < 4:
                print colored(formattedLogLine[0], self.errorTxtColor, self.errorTxtHighlights, attrs=self.errorTxtAttributes) + "   " + " ".join(formattedLogLine[1:])

            elif formattedLogLine[0] == 'CRITICAL':
                print colored(formattedLogLine[0], self.criticalTxtColor, self.criticalTxtHighlights, attrs=self.criticalTxtAttributes) + "   " + " ".join(formattedLogLine[1:])

        logFile.close()



    def stopReadingLogs(self):
        """
        Used to stop the "on the fly" logs display
        """

        self.readLogs = False


    def run(self):
        """
        Thread's main loop
        """

        self.followAndDisplayLogs()





def main():
    logFormatter = LogFormatter("brain.log")
    logFormatter.start()

    for i in range(10):
        logFile = open("brain.log", 'a')
        logFile.write("ERROR  djklfhsldjf\n")
        logFile.close()
        time.sleep(0.5)

    for i in range(10):
        logFile = open("brain.log", 'a')
        logFile.write("WARNING  d54454jf\n")
        logFile.close()
        time.sleep(0.5)

    logFormatter.stopReadingLogs()
    logFormatter.join()



if __name__ == "__main__":
    main()
