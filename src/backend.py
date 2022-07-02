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
    """
    Backend for single PSU controller.
    """

    # ......................... #

    def __init__(self, app: PowerSupplyWidget, port: str):

        super().__init__(port=port)

        self.register(app)
        self.bind()
    
    # ......................... #

    def register(self, app: PowerSupplyWidget):
        """
        Setup initial backend values, duplex thread and connect
        widget elements.

        Args:
            app (PowerSupplyWidget): instance widget
        """

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
        """
        Artificially disable UI widget.
        """
        
        self.app.title.text = 'Disconnected'
        self.app.title.text_color = style.psu_widget.text_color_disabled
        self.voltage_control.disable_digits()
        self.current_control.disable_digits()
        self.output_button.set_disconnected()

    # ......................... #

    def enable_ui(self):
        """
        Artificially enable UI widget.
        """
        
        self.app.title.text = self.port
        self.app.title.text_color = style.psu_widget.text_color
        self.voltage_control.enable_digits()
        self.current_control.enable_digits()
        self.output_button.set_connected()

    # ......................... #

    def reset(self):
        """
        Reset PSU voltage and current to zero, disable output.
        """

        self.set_output_while(0)
        time.sleep(cfg.timeouts.in_step)
        self.voltage = 0
        time.sleep(cfg.timeouts.in_step)
        self.current = 0
        time.sleep(cfg.timeouts.in_step)
    
    # ......................... #

    def bind(self):
        """
        Bing UI elements with backend methods.
        """

        self.output_button.bind(on_press=self.toggle_output)

        # setup value change according to decimal bit position
        for i, bit in enumerate(self.voltage_control.bits):

            delta = 10 ** (self.voltage_control.point_pos - i - 1)
            bit.increment.bind(on_press=partial(self.update_voltage, delta))
            bit.decrement.bind(on_press=partial(self.update_voltage, -delta))
        
        # setup value change according to decimal bit position
        for i, bit in enumerate(self.current_control.bits):

            delta = 10 ** (self.current_control.point_pos - i - 1)
            bit.increment.bind(on_press=partial(self.update_current, delta))
            bit.decrement.bind(on_press=partial(self.update_current, -delta))

    # ......................... #

    def get_status(self, *args) -> str:
        """
        Get information about output status and constant indicators
        on real PSU.

        Returns:
            str: status bits in string representation
        """

        if self.serial:

            self.thread.pause()

            self.write(qje.get_status)
            f = self.read()

            self.thread.resume()

        return f
    
    # ......................... #

    def get_name(self, *args) -> str:
        """
        Get PSU vendor name. Doesn't work for QJ3005P.

        Returns:
            str: PSU vendor name
        """

        if self.serial:
            self.thread.pause()

            self.serial.write(qje.get_name)
            f = self.read()

            self.thread.resume()

        return f
    
    # ......................... #

    def update_constant_indicators(self, *args) -> None:
        """
        Update UI constant indicators according to current PSU status.
        """

        if self.serial:

            f = self.get_status()

            if not f:
                return

            # obtain "C.C"
            if f[0] == '0':
                self.voltage_control.const_indicator.indicator_off()
                self.current_control.const_indicator.indicator_on()
            
            # obtain "C.V"
            else:
                self.voltage_control.const_indicator.indicator_on()
                self.current_control.const_indicator.indicator_off()
    
    # ......................... #

    def set_output_while(self, value: int, *args):
        """
        Disable or enable PSU output.

        Args:
            value (int): output enabled (1) or disabled (0)
        """

        #! sometimes value is missed

        if self.serial:
            self.thread.pause()

            self.write(f'{qje.set_output}{value}')
            time.sleep(cfg.timeouts.output_while)
            
            self.thread.resume()
    
    # ......................... #

    def toggle_output(self, *args):
        """
        Toggle output position.
        """

        if not self.output_button.disconnect and self.serial:

            self.output_enabled = (self.output_enabled + 1) % 2
            self.set_output_while(self.output_enabled)

            if not self.output_enabled:
                self.voltage_control.set_value(self._voltage)
                self.current_control.set_value(self._current)
    
    # ......................... #

    def update_voltage(self, delta: float, *args):
        """
        Update voltage with delta.

        Args:
            delta (float): delta to add.
        """

        if self.serial:
            self.voltage = float(self._voltage) + delta
    
    # ......................... #

    def update_current(self, delta: float, *args):
        """
        Update current with delta.

        Args:
            delta (float): delta to add.
        """

        if self.serial:
            self.current = float(self._current) + delta

    # ......................... #

    def voltage_float_to_str(self, value: float) -> str:
        """
        Convert float value for voltage to string according to
        right floating point position (xx.xx).

        Args:
            value (float): float representation of a value

        Returns:
            str: string representation of a value
        """

        text = f'{value:.2f}'
        text = f'{str(0) * (5 - len(text))}' + text

        return text
    
    # ......................... #

    def current_float_to_str(self, value: float) -> str:
        """
        Convert float value for current to string according to
        right floating point position (x.xxx).

        Args:
            value (float): float representation of a value

        Returns:
            str: string representation of a value
        """

        text = f'{value:.3f}'
        text = f'{str(0) * (5 - len(text))}' + text

        return text

    # ......................... #

    @property
    def voltage(self):
        return self._voltage
    
    @voltage.setter
    def voltage(self, value: str):
        """
        Voltage setter.

        Args:
            value (str): voltage to set
        """

        if self.serial:

            # get string value representation after limits checking
            value = float(value)
            value = min(max(0, value), self.max_voltage)
            value = self.voltage_float_to_str(value)

            # if output disabled - update UI value
            # elsewise it'll be done from the thread
            if not self.output_enabled:
                self.voltage_control.set_value(value)

            self._voltage = value

            self.thread.pause()

            # write corresponding value to the PSU
            self.write(f'{qje.voltage_set}{value}')
            time.sleep(cfg.timeouts.global_thread)

            self.thread.resume()
    
    @voltage.getter
    def voltage(self) -> str:
        """
        Voltage getter.

        Returns:
            str: voltage value
        """

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
    def current(self, value: str):
        """
        Current setter.

        Args:
            value (str): current to set
        """

        if self.serial:
            
            # get string value representation after limits checking
            value = float(value)
            value = min(max(0, value), self.max_current)
            value = self.current_float_to_str(value)

            # if output disabled - update UI value
            # elsewise it'll be done from the thread
            if not self.output_enabled:
                self.current_control.set_value(value)

            self._current = value

            self.thread.pause()

            self.write(f'{qje.current_set}{value}')
            time.sleep(cfg.timeouts.global_thread)

            self.thread.resume()
    
    @current.getter
    def current(self) -> str:
        """
        Current getter.

        Returns:
            str: current value
        """

        if self.serial:

            self.write(qje.current_get)
            f = self.read()

            if self.output_enabled:
                self.current_control.set_value(f)

            return self._current

# ------------------------- #

class AppBackend:
    """
    Main app backend to operate with connected instance
    and handle disconnection cases.
    """
    
    def __init__(self, app: object) -> None:

        self.available = set()
        self.working = set()
        
        self.app = app
        self.thread = SerialMonitor(backend=self)
    
    # ......................... #

    def start(self):
        """
        Start thread with backend start.
        """

        self.thread.start()
    
    # ......................... #

    def check_initial_connection(self) -> bool:
        """
        Check avilable port set is not empty, check
        ports in the set for living (handle power off case for PSU).

        Returns:
            bool: is there available PSU instances
        """


        self.thread.check_ports()
        bad_ports = set()

        # check ports in the set if non-empty
        for port in self.available:

            psu = PSU(port=port, timeout=0.5)
            psu.write(qje.get_status)
            f = psu.read()
            
            if not f:
                bad_ports.add(port)
                psu.serial.close()

        # exclude ports impossible to reach (psu power off case)
        self.available = self.available.difference(bad_ports)
        
        return self.available != set()
    
    # ......................... #

    def build_app_screen(self, num_cols: int = 3):
        """
        Init build of the app screen.

        Args:
            num_cols (int, optional): number of columns at the app screen. Defaults to 3.
        """

        available = list(self.available)

        # add instance for each available port and connect with separate backend
        for port in available:
            ctrl = PowerSupplyWidget(
                    height=350,
                    width=280,
                    size_hint=(None, None)
                )
            self.psu_instances[port] = ctrl
            bnd = InstanceBackend(self.psu_instances[port], port=port)
            self.psu_backends[port] = bnd

        num_rows = 0
        
        # place instance according to its count
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
        """
        Update app screen according to changes in working ports set.
        """

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