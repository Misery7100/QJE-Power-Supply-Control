import os
import time
import yaml

from serial import Serial
from threading import Thread

from pathlib import Path
from serial import Serial

from .utils import dotdict

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent

with open(os.path.join(BASE_DIR, 'yml/qje_protocol.yml'), 'r') as stream:
    qje = dotdict(yaml.load(stream, Loader=yaml.Loader))

with open(os.path.join(BASE_DIR, 'yml/threads.yml'), 'r') as stream:
    cfg = dotdict(yaml.load(stream, Loader=yaml.Loader))

# ------------------------- #

class SerialHalfDuplexV2(Thread): # TODO: fix shit with disabled instances, fix thread (lost connection etc)

    def __init__(self, backend, **kwargs) -> None:

        super().__init__(**kwargs)

        self.daemon = True
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

    def update_voltage(self):
        pass

    # ......................... #

    def update_current(self):
        pass

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
                    self.backend.app.disabled = True
            
            else:
                try:
                    self.serial = Serial(self.backend.port)
                    self.disconnected = False
                    self.backend.app.disabled = False

                except:
                    pass

# ------------------------- #
# ------------------------- #
# ------------------------- #
# ------------------------- #
# ------------------------- #

class SerialHalfDuplex(Thread):

    def __init__(self, instance, **kwargs) -> None:

        super().__init__(**kwargs)

        self.daemon = True
        self.disconnected = False
        self.paused = False

        self.instance = instance
    
    # ......................... #

    def get_status(self):
        self.instance.serial.reset_input_buffer()
        self.instance.serial.reset_output_buffer()
        self.instance.serial.write(f'{qje.get_status}{qje.end_sym}'.encode())
        self.instance.serial.flush()
        f = self.instance.serial.read(2)
        self.instance.serial.flush()
        self.instance.serial.reset_input_buffer()
        self.instance.serial.reset_output_buffer()
        f = f.decode()

        return f

    # ......................... #

    def update_voltage(self):
        pass

    # ......................... #

    def update_current(self):
        pass

    # ......................... #

    def update_constant_indicators(self):

        f = self.get_status()

        if f[0] == '0':
            self.instance.v_ctrl.const_indicator.indicator_off()
            self.instance.c_ctrl.const_indicator.indicator_on()
        
        else:
            self.instance.v_ctrl.const_indicator.indicator_on()
            self.instance.c_ctrl.const_indicator.indicator_off()

    # ......................... #

    def run(self):
        while 1:
            time.sleep(0.05) # TODO: move to threads params

            if self.instance.serial and not self.disconnected:
                try:
                    self.instance.serial.inWaiting()

                    # update voltage
                    if not self.paused and self.instance.output_status:
                        print('I`m here')
                        try:
                            _value = self.instance.v_ctrl.get()
                            print('I`m here 2')
                            value = _value[:-1].decode()
                            print(f'{value=}')

                        except:
                            pass

                        time.sleep(0.1)

                    if not self.paused and self.instance.output_status:
                        self.update_constant_indicators()

                except:
                    self.disconnected = True
                    self.instance.disabled = True
            
            else:
                try:
                    self.instance.serial = Serial(self.instance.port)
                    self.disconnected = False
                    self.instance.disabled = False

                except:
                    pass

# ------------------------- #
