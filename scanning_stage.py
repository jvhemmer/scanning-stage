# -*- coding: utf-8 -*-
"""
Created on Mon Oct 9 2023

@author: Johann Hemmer
"""

from ctypes import WinDLL, create_string_buffer
from typing import Tuple

import os, time

class Controller():
    def __init__(self) -> None:      
        # Load PriorScientificSDK library
        self.SDKPrior = WinDLL(r"C:\Users\Lab 146\Desktop\Scripts\PriorScientificSDK.dll")

        # Create a buffer to pass data to C functions, with size 1000 (just a large number)
        self.rx = create_string_buffer(1000)

        # Initialize API
        print('Initializing API...')
        _ret = self.SDKPrior.PriorScientificSDK_Initialise()

        if _ret:
            print(f'API initialization error. Return code: {_ret}.')
        else:
            print('API OK.')

        # Get version
        _ret = self.SDKPrior.PriorScientificSDK_Version(self.rx)
        print(f'DLL version {self.rx.value.decode()}')

        # Create session ID
        self.session_id = self.SDKPrior.PriorScientificSDK_OpenNewSession()
        if self.session_id < 0:
            print(f'Error getting session ID. Return code: {self.session_id}.')
            
        else:
            print(f'Session ID = {self.session_id}.')
        
        # I have no ideia what this does. Probably an API test
        _ret = self.SDKPrior.PriorScientificSDK_cmd(
            self.session_id,
            create_string_buffer(b"dll.apitest 33 goodresponse"),
            self.rx
        )
        print(f'API response: {_ret}, rx = {self.rx.value.decode()}.')

        # Probably another API test
        _ret = self.SDKPrior.PriorScientificSDK_cmd(
            self.session_id,
            create_string_buffer(b"dll.apitest -300 stillgoodresponse"),
            self.rx
        )
        print(f'API response: {_ret}, rx = {self.rx.value.decode()}.')

class Stage():
    def __init__(self, controller: Controller) -> None:
        self.controller = controller
        
        # Initialize properties
        self._trim = (0, 0)

    def __del__(self):
        self.disconnect()

    def command(self, cmd, verbose = False) -> Tuple[int, str]:
        if verbose: print(f"Sending command: '{cmd}'...")
        _ret = self.controller.SDKPrior.PriorScientificSDK_cmd(
            self.controller.session_id,
            create_string_buffer(cmd.encode()),
            self.controller.rx
        )
        
        if _ret:
            if verbose: print(f'API error. Return code: {_ret}.')
            # sys.exit()
        else:
            if verbose: print('OK.')

        return _ret, self.controller.rx.value.decode()


    def disconnect(self):
        if self.busy:
            print('Stage busy (code {self.busy}). Ignoring.')
        else:
            self.command("controller.disconnect", True)


    def connect(self, com_port):
        # Assign com_port value
        self.com_port = com_port

        print(f'Connecting to COM {self.com_port}...')
        (_ret, _rx) = self.command(f'controller.connect {self.com_port}')
        if _ret:
            print(f'Connection failed on COM Port {self.com_port}',
                    'Make sure instrument is on and cables are properly ',
                    'connected. Also, the COM Port depends on the USB port ',
                    'the instrument was connected to the computer.',
                    sep = os.linesep)
        else:
            print('Connection successful.')
            print(f"Model: {self.name}.")
            print(f'Position: {self.pos} um.')
            print(f'Step size: {self.step_size} 1/um.')
            print(f'Speed: {self.speed} um/s.')
            print(f'Acceleration: {self.accel} um/s^2.')
            print(f'Jerk time: {self.jerk} ms.')
            
    def stop(self, smooth=True):
        print('Stopping...')
        
        if smooth:
            self.command("controller.stop.smoothly")
        else:
            self.command("controller.stop.abruptly")


    def monitor(self, rate: float = 0.01):      
        while self.busy:
            pos = self.pos
            print('\033[K' + 'Current position, in um: ' + str(pos), end = '\r')
            time.sleep(rate)

    def goto(self, new_pos: Tuple[float, float]):
        # Goes to the specified position
        x = new_pos[0] / (self.step_size / self.steps_per_micron)
        y = new_pos[1] / (self.step_size / self.steps_per_micron)
        
        (ret, _) = self.command(f"controller.stage.goto-position {x} {y}")

    def set_home(self):
        # Sets the current position as (0, 0)
        self.command('controller.stage.position.set {0} {0}')
    

    def move(self, amount: Tuple[float, float]):
        # Displaces the current position by a set amount (`amount`) only along the y-axis
        x, y = amount
        
        x = x / (self.step_size / self.steps_per_micron)
        y = y / (self.step_size / self.steps_per_micron)
        
        self.command(f'controller.stage.move-relative {x} {y}')

    @property
    def busy(self) -> int:
        # 0 = idle, 1 = x moving, 2 = y moving, 3 = x and y moving
        (ret, rx) = self.command("controller.stage.busy.get")
        self._busy = int(rx)
        return self._busy

    @property
    def name(self) -> str:
        # Returns stage model name
        (ret, rx) = self.command("controller.stage.name.get")
        self._name = rx
        return self._name

    @property
    def steps_per_micron(self) -> int:
        # Returns current steps per micrometer
        (ret, rx) = self.command("controller.stage.steps-per-micron.get")
        self._steps_per_micron = int(rx)
        return self._steps_per_micron

    @property
    def step_size(self) -> int:
        # Returns current unit step size in 1/um (known as 'ss' in docs)
        (ret, rx) = self.command("controller.stage.ss.get")
        self._step_size = int(rx)
        return self._step_size

    @step_size.setter
    def step_size(self, value: int):
        if self.busy:
            print(f'Stage busy (code {self.busy}). Ignoring.')
        else:
            (ret, _) = self.command(f"controller.stage.ss.set {value}")
            
            if ret:
                print(f'Something went wrong. Error code: {ret}.')

    @property
    def trim(self) -> Tuple[float, float]:
        # Returns the trim in µm
        return self._trim

    @trim.setter
    def trim(self, value: Tuple[float, float]):
        self._trim = value

    @property
    def pos(self) -> Tuple[float, float]:
        # Returns current stage position as (X, Y)
        (ret, rx) = self.command("controller.stage.position.get")
        if ret < 0:
            if ret == -10004:
                print('Controller and stage are not connected.')
        else:
            _pos_split = rx.split(',')
    
            self._x = round(float(_pos_split[0]) * (self.step_size / self.steps_per_micron), 2)
            self._y = round(float(_pos_split[1]) * (self.step_size / self.steps_per_micron), 2)
    
            self._pos = (self._x, self._y)
            return self._pos


    @property
    def speed(self) -> float:
        (ret, rx) = self.command("controller.stage.speed.get")
        self._speed = float(rx)
        return self._speed

    @speed.setter
    def speed(self, value: float):
        value = value
        if self.busy:
            print(f'Stage busy (code {self.busy}). Ignoring.')
        else:
            (ret, _) = self.command(f"controller.stage.speed.set {value}")
            
            if ret:
                print(f'Something went wrong. Error code: {ret}.')

    @property
    def accel(self) -> float:
        # Returns acceleration during stage movement
        (ret, rx) = self.command("controller.stage.acc.get")
        self._accel = float(rx)
        return self._accel        

    @accel.setter
    def accel(self, value: float):
        value = value
        if self.busy:
            print(f'Stage busy (code {self.busy}). Ignoring.')
        else:
            (ret, _) = self.command(f"controller.stage.acc.set {value}")
            
            if ret:
                print(f'Something went wrong. Error code: {ret}.')

    @property
    def jerk(self) -> float:
        # Returns jerk time (time in ms untill full acceleration)
        (ret, rx) = self.command("controller.stage.jerk.get")
        self._jerk = float(rx)
        return self._jerk  

    @jerk.setter
    def jerk(self, value: float):
        if self.busy:
            print(f'Stage busy (code {self.busy}). Ignoring.')
        else:
            (ret, _) = self.command(f"controller.stage.jerk.set {value}")
            
            if ret:
                print(f'Something went wrong. Error code: {ret}.')
