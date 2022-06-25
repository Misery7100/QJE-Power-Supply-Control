import time

from serial import Serial
from threading import Thread

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
        self.instance.serial.write('STATUS?\\n'.encode())
        self.instance.serial.flush()
        f = self.instance.serial.read(1)
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
            time.sleep(0.05)

            if self.instance.serial and not self.disconnected:
                try:
                    self.instance.serial.inWaiting()
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