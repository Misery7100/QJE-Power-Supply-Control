import time

from serial import Serial
from threading import Thread

from serial import Serial

from src.utils import *
from src.serial import parse_ports

# ------------------------- #

class SerialHalfDuplexV2(Thread):
    """
    Instance daemon thread to make communication with UI and PSU.
    """

    def __init__(self, backend: object, **kwargs) -> None:

        super().__init__(daemon=True, **kwargs)

        self.disconnected = False
        self.paused = False

        self.backend = backend

    # ......................... #

    def resume(self):
        """
        Resume the thread artificially.
        """

        self.paused = False
        
    # ......................... #

    def pause(self):
        """
        Pause the thread artificially.
        """

        self.paused = True
    
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
        """
        Main thread loop.
        """
        
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
                        
                        # loop delay x1
                        time.sleep(cfg.timeouts.in_step)

                    # update current
                    if not self.paused and self.output_enabled:
                        try:
                            current = self.backend.current
                        
                        except:
                            pass
                        
                        # loop delay x2
                        time.sleep(cfg.timeouts.in_step)

                    # update indicators
                    if not self.paused and self.output_enabled:
                        try:
                            self.backend.update_constant_indicators()
                        except:
                            pass
                        
                        # loop delay x3
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
    """
    App monitoring daemon thread.
    """

    def __init__(self, backend: object, **kwargs) -> None:

        super().__init__(daemon=True, **kwargs)

        self.backend = backend
    
    # ......................... #
    
    def stop(self):
        """
        Stop instance polling.
        """

        self._stop_event.set()
    
    # ......................... #

    def check_ports(self):
        """
        Update available ports set with pre-reset.
        """

        self.available = set()
        ports = parse_ports()

        for port in ports:
            if port not in self.available:
                self.available.add(port)
    
    # ......................... #

    def run(self):
        """
        Main thread loop.
        """

        while True:

            # check and update ports
            self.check_ports()
            disconnected = self.working.difference(self.available)
            new = self.available.difference(self.working)

            # remove disconnected instances
            for p in disconnected:
                self.working.remove(p)
            
            # add new instances (not work because on-fly connection isn't implemented)
            for p in new:
                self.working.add(p)

            # update app screen according to the working ports set
            self.backend.update_app_screen()

            # loop delay
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