# -*- coding: utf-8 -*-
"""
Created on Wed Feb 28 12:13:03 2024

@author: Johann Hemmer
"""

import clr

import sys
import os

# Import System.IO for saving and opening files
from System.IO import *

# Import C compatible List and String
from System import String
from System.Collections.Generic import List

# Add needed dll references
sys.path.append(os.environ['LIGHTFIELD_ROOT'])
sys.path.append(os.environ['LIGHTFIELD_ROOT']+"\\AddInViews")
clr.AddReference('PrincetonInstruments.LightFieldViewV5')
clr.AddReference('PrincetonInstruments.LightField.AutomationV5')
clr.AddReference('PrincetonInstruments.LightFieldAddInSupportServices')

# PI imports
from PrincetonInstruments.LightField.Automation import Automation
from PrincetonInstruments.LightField.AddIns import ExperimentSettings
from PrincetonInstruments.LightField.AddIns import CameraSettings
from PrincetonInstruments.LightField.AddIns import DeviceType

class Spectrometer():
    def __init_(self):
        pass

    def connect(self):
        # Open a LightField instance with an empty method
        self.auto = Automation(True, List[String]())

        self.experiment = self.auto.LightFieldApplication.Experiment
        
        print(f'Loaded {self.experiment.Name}.')

    def set(self, setting, value):
        if self.experiment.Exists(setting):
            self.experiment.SetValue(setting, value)
    
    def get(self, setting):
        if self.experiment.Exists(setting):
            return self.experiment.GetValue(setting)

    def acquire(self):
        if not self.busy:
            self.experiment.Acquire()
        else:
            print('Spectrometer busy.')

    @property
    def exposure_time(self) -> int:
        # Returns the exposure time, in s
        value = self.get(CameraSettings.ShutterTimingExposureTime)
        return value

    @exposure_time.setter
    def exposure_time(self, value: float):
        # Sets the exposure time, in s
        self.set(CameraSettings.ShutterTimingExposureTime, value)

    @property
    def total_frames(self) -> int:
        # Returns the total number of frames to acquire
        value = self.get(ExperimentSettings.AcquisitionFramesToStore)
        return value

    @total_frames.setter
    def total_frames(self, value: int):
        # Sets the total number of frames to acquire
        value = float(value) # convert to float, but only acept int
        self.set(ExperimentSettings.AcquisitionFramesToStore, value)

    @property
    def file_name(self) -> int:
        # Returns the file name
        value = self.get(ExperimentSettings.FileNameGenerationBaseFileName)
        return value

    @file_name.setter
    def file_name(self, value: float):
        # Sets the file name
        self.set(ExperimentSettings.FileNameGenerationBaseFileName, Path.GetFileName(value))
    
    @property
    def busy(self):
        return self.experiment.IsRunning
    
if __name__ == '__main__':
    s = Spectrometer()
    
    s.connect()