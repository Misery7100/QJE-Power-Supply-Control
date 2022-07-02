import time

from functools import partial
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout

from src.supply import *
from src.utils import *
from src.psu import PSU
from src.thread import SerialHalfDuplexV2, SerialMonitor

# ------------------------- #

class InstanceBackend(PSU):

    # ......................... #

    def __init__(self, app: object, port: str):

        super().__init__(port=port)

        self.register(app)
        self.bind()
    
    # ......................... #

    def register(self, app: object):

        self.output_enabled = 0
        self._voltage = None
        self._current = None

        self.app = app
        self.output_button = self.app.output_button
        self.voltage_control = self.app.v_ctrl
        self.current_control = self.app.c_ctrl
        self.thread = SerialHalfDuplexV2(backend=self)

        self.enable_ui()
        self.reset() # reset output, current and voltage
        self.update_constant_indicators() # update cinds on init
        self.thread.start()
    
    # ......................... #

    def disable_ui(self):
        
        self.app.title.text = 'Disconnected'
        self.app.title.text_color = style.psu_widget.text_color_disabled
        self.voltage_control.disable_digits()
        self.current_control.disable_digits()
        self.output_button.set_disconnected()

    # ......................... #

    def enable_ui(self):
        
        self.app.title.text = self.port
        self.app.title.text_color = style.psu_widget.text_color
        self.voltage_control.enable_digits()
        self.current_control.enable_digits()
        self.output_button.set_connected()

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

        if self.serial:

            self.thread.pause()

            self.write(qje.get_status)
            f = self.read()

            self.thread.resume()

        return f
    
    # ......................... #

    def get_name(self, *args):

        if self.serial:
            self.thread.pause()

            self.serial.write(qje.get_name)
            f = self.read()

            self.thread.resume()

        return f
    
    # ......................... #

    def update_constant_indicators(self, *args):

        if self.serial:

            f = self.get_status()

            if f[0] == '0':
                self.voltage_control.const_indicator.indicator_off()
                self.current_control.const_indicator.indicator_on()
            
            else:
                self.voltage_control.const_indicator.indicator_on()
                self.current_control.const_indicator.indicator_off()
    
    # ......................... #

    def set_output_while(self, value, *args):

        #! sometimes value is missed

        if self.serial:
            self.thread.pause()

            self.write(f'{qje.set_output}{value}')
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

        if not self.output_button.disconnect and self.serial:

            self.output_enabled = (self.output_enabled + 1) % 2
            self.set_output_while(self.output_enabled)

            if not self.output_enabled:
                self.voltage_control.set_value(self._voltage)
                self.current_control.set_value(self._current)
    
    # ......................... #

    def update_voltage(self, delta, *args):
        if self.serial:
            self.voltage = float(self._voltage) + delta
    
    # ......................... #

    def update_current(self, delta, *args):
        if self.serial:
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

        if self.serial:

            value = float(value)
            value = min(max(0, value), self.max_voltage)
            value = self.voltage_float_to_str(value)

            if not self.output_enabled:
                self.voltage_control.set_value(value)

            self._voltage = value

            self.thread.pause() # reset buffer is here

            self.write(f'{qje.voltage_set}{value}')
            time.sleep(cfg.timeouts.global_thread)

            self.thread.resume()
    
    @voltage.getter
    def voltage(self):

        if self.serial:

            self.write(qje.voltage_get)
            f = self.read()

            if self.output_enabled:
                self.voltage_control.set_value(f)

            return self._voltage
    
    # ......................... #

    @property
    def current(self):
        return self._current
    
    @current.setter
    def current(self, value):

        if self.serial:

            value = float(value)
            value = min(max(0, value), self.max_current)
            value = self.current_float_to_str(value)

            if not self.output_enabled:
                self.current_control.set_value(value)

            self._current = value

            self.thread.pause()

            self.write(f'{qje.current_set}{value}')
            time.sleep(cfg.timeouts.global_thread)

            self.thread.resume()
    
    @current.getter
    def current(self):

        if self.serial:

            self.write(qje.current_get)
            f = self.read()

            if self.output_enabled:
                self.current_control.set_value(f)

            return self._current

# ------------------------- #

class AppBackend:
    
    def __init__(self, app) -> None:

        self.available = set()
        self.working = set()
        
        self.app = app
        self.thread = SerialMonitor(backend=self)
    
    # ......................... #

    def start(self):
        self.thread.start()
    
    # ......................... #

    def check_initial_connection(self):

        self.thread.check_ports()
        bad_ports = set()

        if self.available:
            for port in self.available:

                psu = PSU(port=port, timeout=0.5)
                psu.write(qje.get_status)
                f = psu.read()
                
                if not f:
                    bad_ports.add(port)
                    psu.serial.close()
        
        self.available = self.available.difference(bad_ports)
        
        if self.available: 
            return True

        else:
             return False
            
    
    # ......................... #

    def build_app_screen(self, num_cols: int = 3):

        available = list(self.available)

        for port in available:
            ctrl = PowerSupplyWidget(
                    height=350, #! hardcoded
                    width=280,  #! hardcoded
                    size_hint=(None, None)
                )
            self.psu_instances[port] = ctrl
            bnd = InstanceBackend(self.psu_instances[port], port=port)
            self.psu_backends[port] = bnd

        num_rows = 0
        
        for i in range(0, len(self.psu_instances), num_cols):

            row = MDBoxLayout(orientation='horizontal')
            row.spacing = 3
            num_rows += 1

            for j in range(num_cols):
                if i + j < len(self.psu_instances):
                    row.add_widget(self.psu_instances[available[i + j]])

            self.app.grid.add_widget(row)
        
        self.app.screen.add_widget(self.app.grid)
        Window.size = (280 * min(len(self.psu_instances.keys()), num_cols), 350 * num_rows)

    # ......................... #

    def update_app_screen(self):

        for port in self.psu_instances.keys():
            if port not in self.working:
                self.psu_backends[port].disable_ui()
            else:
                self.psu_backends[port].enable_ui()
                self.psu_backends[port].update_constant_indicators()
    
    # ......................... #

    @property
    def psu_instances(self):
        return self.app.psu_widgets
    
    @property
    def psu_backends(self):
        return self.app.backends