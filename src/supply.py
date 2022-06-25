from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.effectwidget import EffectWidget, HorizontalBlurEffect, VerticalBlurEffect, FXAAEffect
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFillRoundFlatButton, MDRoundFlatButton, MDIconButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDFillRoundFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.behaviors.magic_behavior import MagicBehavior
from kivymd.uix.screen import MDScreen

from serial import Serial

from .controllers import *
from .thread import SerialHalfDuplex

# ------------------------- #

class PowerSupplyControl(MDBoxLayout):

    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'

        self.ctrl_layout = MDBoxLayout(orientation='vertical')
        self.ctrl_layout.padding = 10
        self.ctrl_layout.spacing = 10
        self.ctrl_layout.md_bg_color = (0, 0, 0, 0.4)

        self.port = port
        self.output_status = 0

        self.title = MDLabel(
                text=port, 
                size_hint_y=0.1,
                halign='center',
                theme_text_color="Custom",
                text_color="#dcdcdc",
            )

        self.output_button = MDFillRoundFlatButton(
                text='OUTPUT', 
                size_hint_y=0.1,
                theme_text_color="Custom",
                text_color="#111111",
                ripple_scale=0
            )
        
        self.output_button.md_bg_color = "#787878" #! hardcoded shit
        self.output_button.line_color = "#434343" #! hardcoded shit
        self.output_button.line_width = 3
        self.output_button.bind(on_press=self.toggle_output)

        self.v_ctrl = VoltageController(instance=self)
        self.c_ctrl = CurrentController(instance=self)

        self.ctrl_layout.add_widget(self.title)
        self.ctrl_layout.add_widget(self.v_ctrl)
        self.ctrl_layout.add_widget(self.c_ctrl)
        self.ctrl_layout.add_widget(self.output_button)

        self.add_widget(self.ctrl_layout)

        self.initialize_connection()
        self.thread = SerialHalfDuplex(instance=self)
        self.thread.start()
    
    # ......................... #

    def toggle_output(self, *args): # TODO: move into separate class named OutputButton mb

        self.thread.paused = True
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

        self.output_status = (self.output_status + 1) % 2

        status = self.thread.get_status()

        while status[-1] != str(self.output_status):

            time.sleep(0.08) # TODO: move to threads params
            self.serial.write(f'{qje.set_output}{self.output_status}{qje.end_sym}'.encode())
            self.serial.flush()
            self.serial.reset_input_buffer()
            self.serial.reset_output_buffer()
            time.sleep(0.08)
            status = self.thread.get_status()

        self.toggle_output_color()
        self.thread.paused = False

    # ......................... #

    # ......................... #

    def toggle_output_color(self, *args): # TODO: move into separate class named OutputButton mb
        colors = ["#787878", "#ff8400"]
        self.output_button.md_bg_color = colors[self.output_status]
    
    # ......................... #
    
    def initialize_connection(self):
        self.serial = Serial(self.port)

# ------------------------- #