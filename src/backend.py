import os
import time
import yaml

from functools import partial
from pathlib import Path
from serial import Serial

from .thread import SerialHalfDuplexV2
from .utils import dotdict

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent

with open(os.path.join(BASE_DIR, 'yml/qje_protocol.yml'), 'r') as stream:
    qje = dotdict(yaml.load(stream, Loader=yaml.Loader))

with open(os.path.join(BASE_DIR, 'yml/threads.yml'), 'r') as stream:
    cfg = dotdict(yaml.load(stream, Loader=yaml.Loader))

with open(os.path.join(BASE_DIR, 'yml/style.yml'), 'r') as stream:
    style = dotdict(yaml.load(stream, Loader=yaml.Loader))

# ------------------------- #

class Backend: # TODO: fix shit with disabled instances, fix thread (lost connection etc)

    max_voltage = 30.00
    max_current = 3.000

    # ......................... #

    def __init__(self, app: object, port: str, **kwargs):
        self.register(app, port)
        self.bind()
    
    # ......................... #

    def register(self, app: object, port: str):

        self.output_enabled = 0
        self._voltage = None
        self._current = None

        self.app = app
        self.output_button = self.app.output_button
        self.voltage_control = self.app.v_ctrl
        self.current_control = self.app.c_ctrl
        self.port = port
        self.serial = Serial(self.port, timeout=0.2)
        self.thread = SerialHalfDuplexV2(backend=self)

        self.app.title.text = self.port
        self.app.title.disabled = False

        self.voltage_control.enable_digits()
        self.current_control.enable_digits()
        self.output_button.md_bg_color = style.output_btn.background_off

        self.reset() # reset output, current and voltage
        self.update_constant_indicators() # update cinds on init
        self.thread.start()
    
    # ......................... #

    def reset(self):
        self.set_output_while(0)
        time.sleep(cfg.timeouts.in_step)
        self.voltage = 0
        time.sleep(cfg.timeouts.in_step)
        self.current = 0
        time.sleep(cfg.timeouts.in_step)
    
    # ......................... #

    def bind(self):

        self.output_button.bind(on_press=self.toggle_output)

        for i, bit in enumerate(self.voltage_control.bits):

            delta = 10 ** (self.voltage_control.point_pos - i - 1)
            bit.increment.bind(on_press=partial(self.update_voltage, delta))
            bit.decrement.bind(on_press=partial(self.update_voltage, -delta))
        
        for i, bit in enumerate(self.current_control.bits):

            delta = 10 ** (self.current_control.point_pos - i - 1)
            bit.increment.bind(on_press=partial(self.update_current, delta))
            bit.decrement.bind(on_press=partial(self.update_current, -delta))

    # ......................... #

    def get_status(self, *args):

        self.thread.pause() # reset buffer is here

        self.serial.write(f'{qje.get_status}{qje.end_sym}'.encode())
        self.serial.flush()

        f = self.serial.readline().decode().strip()
        self.thread.resume()

        return f
    
    # ......................... #

    def get_name(self, *args):
        self.thread.pause() # reset buffer is here

        self.serial.write(f'{qje.get_name}{qje.end_sym}'.encode())
        self.serial.flush()

        f = self.serial.readline().decode().strip()
        self.thread.resume()

        return f
    
    # ......................... #

    def update_constant_indicators(self, *args):

        f = self.get_status()

        if f[0] == '0':
            self.voltage_control.const_indicator.indicator_off()
            self.current_control.const_indicator.indicator_on()
        
        else:
            self.voltage_control.const_indicator.indicator_on()
            self.current_control.const_indicator.indicator_off()
    
    # ......................... #

    def set_output_while(self, value, *args):

        #! sometimes value missed

        self.thread.pause()

        self.serial.write(f'{qje.set_output}{value}{qje.end_sym}'.encode())
        self.serial.flush()
        time.sleep(cfg.timeouts.output_while)

        # status = self.get_status() # reset buffer is here

        # while status[1] != str(value):

        #     self.serial.write(f'{qje.set_output}{value}{qje.end_sym}'.encode())
        #     self.serial.flush()
        #     time.sleep(cfg.timeouts.output_while)
        #     status = self.get_status()
        #     time.sleep(cfg.timeouts.output_while)
        
        self.thread.resume()
    
    # ......................... #

    def toggle_output(self, *args):

        self.output_enabled = (self.output_enabled + 1) % 2
        self.set_output_while(self.output_enabled)

        if not self.output_enabled:
            self.voltage_control.set_value(self._voltage)
            self.current_control.set_value(self._current)
    
    # ......................... #

    def update_voltage(self, delta, *args):
        self.voltage = float(self._voltage) + delta
    
    # ......................... #

    def update_current(self, delta, *args):
        self.current = float(self._current) + delta

    # ......................... #

    def voltage_float_to_str(self, value):
        text = f'{value:.2f}'
        text = f'{str(0) * (5 - len(text))}' + text

        return text
    
    # ......................... #

    def current_float_to_str(self, value):
        text = f'{value:.3f}'
        text = f'{str(0) * (5 - len(text))}' + text

        return text

    # ......................... #

    @property
    def voltage(self):
        return self._voltage
    
    @voltage.setter
    def voltage(self, value):

        value = float(value)
        value = min(max(0, value), self.max_voltage)
        value = self.voltage_float_to_str(value)

        if not self.output_enabled:
            self.voltage_control.set_value(value)

        self._voltage = value

        self.thread.pause() # reset buffer is here

        self.serial.write(f'{qje.voltage_set}{value}{qje.end_sym}'.encode())
        self.serial.flush()
        time.sleep(cfg.timeouts.global_thread)

        self.thread.resume()
    
    @voltage.getter
    def voltage(self):

        self.serial.reset_output_buffer()
        self.serial.reset_input_buffer()
        self.serial.write(f'{qje.voltage_get}{qje.end_sym}'.encode())
        self.serial.flush()

        #sym = self.serial.read().decode()

        # while sym == "\\n":
        #     sym = self.serial.read().decode()
        #     self.serial.flush()
        #     print(sym)

        f = self.serial.readline().decode().strip()

        #self.serial.flush()

        #self._voltage = f

        if self.output_enabled:
            self.voltage_control.set_value(f)

        return self._voltage
    
    # ......................... #

    @property
    def current(self):
        return self._current
    
    @current.setter
    def current(self, value):

        value = float(value)
        value = min(max(0, value), self.max_current)
        value = self.current_float_to_str(value)

        if not self.output_enabled:
            self.current_control.set_value(value)

        self._current = value

        self.thread.pause() # reset buffer is here

        self.serial.write(f'{qje.current_set}{value}{qje.end_sym}'.encode())
        self.serial.flush()
        time.sleep(cfg.timeouts.global_thread)

        self.thread.resume()
    
    @current.getter
    def current(self):

        self.serial.reset_input_buffer() # ?
        self.serial.reset_output_buffer() # ?

        self.serial.write(f'{qje.current_get}{qje.end_sym}'.encode())
        self.serial.flush()

        f = self.serial.readline().decode().strip()

        #self._current = f

        if self.output_enabled:
            self.current_control.set_value(f)

        return self._current
    
    # ......................... #

