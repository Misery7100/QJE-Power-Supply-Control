import time

from serial import Serial
from threading import Thread

from serial import Serial

from src.utils import *
from src.serial import parse_ports

# ------------------------- #

class SerialHalfDuplexV2(Thread):

    def __init__(self, backend, **kwargs) -> None:

        super().__init__(daemon=True, **kwargs)

        self.disconnected = False
        self.paused = False

        self.backend = backend

    # ......................... #

    def resume(self):
        self.paused = False
        
    # ......................... #

    def pause(self):
        self.paused = True
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
    
    # ......................... #

    @property
    def serial(self):
        return self.backend.serial
    
    @serial.getter
    def serial(self):
        return self.backend.serial
    
    @serial.setter
    def serial(self, value: object):
        self.backend.serial = value
    
    # ......................... #

    @property
    def output_enabled(self):
        return self.backend.output_enabled

    @output_enabled.getter
    def output_enabled(self):
        return self.backend.output_enabled
    
    @output_enabled.setter
    def output_enabled(self, value: int):
        self.backend.output_enabled = value

    # ......................... #

    def run(self):
        while True:
            time.sleep(cfg.timeouts.global_thread)

            if self.serial and not self.disconnected:
                try:
                    self.serial.inWaiting()

                    # update voltage
                    if not self.paused and self.output_enabled:
                        try:
                            voltage = self.backend.voltage

                        except:
                            pass
                            
                        time.sleep(cfg.timeouts.in_step)

                    # update current
                    if not self.paused and self.output_enabled:
                        try:
                            current = self.backend.current
                        
                        except:
                            pass
                            
                        time.sleep(cfg.timeouts.in_step)


                    if not self.paused and self.output_enabled:
                        try:
                            self.backend.update_constant_indicators()
                        
                        except:
                            pass
                            
                        time.sleep(cfg.timeouts.in_step)

                except:
                    self.disconnected = True
                    self.serial = None
            
            else:
                pass
                try:
                    self.serial = Serial(self.backend.port)
                    self.disconnected = False

                except:
                    pass

# ------------------------- #

class SerialMonitor(Thread):

    def __init__(self, backend, **kwargs) -> None:
        super().__init__(daemon=True, **kwargs)

        self.backend = backend
    
    # ......................... #
    
    def stop(self):
        self._stop_event.set()
    
    # ......................... #

    def check_ports(self):
        self.available = set()
        ports = parse_ports()

        for port in ports:
            if port not in self.available:
                self.available.add(port)
    
    # ......................... #

    def run(self):
        while True:
            self.check_ports()
            disconnected = self.working.difference(self.available)
            new = self.available.difference(self.working)

            for p in disconnected:
                self.working.remove(p)
            
            for p in new:
                self.working.add(p)

            self.backend.update_app_screen()

            time.sleep(cfg.timeouts.psu_capture)
    
    # ......................... #

    @property
    def available(self):
        return self.backend.available
    
    @available.setter
    def available(self ,value):
        self.backend.available = value
    
    @property
    def working(self):
        return self.backend.working
    
    @working.setter
    def working(self ,value):
        self.backend.working = value