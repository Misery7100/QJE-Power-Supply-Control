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

        self.title = MDLabel(
                text=port, 
                size_hint_y=0.1,
                halign='center',
                theme_text_color="Custom",
                text_color="#dcdcdc",
            )

        self.v_ctrl = VoltageController(instance=self)
        self.c_ctrl = CurrentController(instance=self)

        self.ctrl_layout.add_widget(self.title)
        self.ctrl_layout.add_widget(self.v_ctrl)
        self.ctrl_layout.add_widget(self.c_ctrl)

        self.add_widget(self.ctrl_layout)

        self.initialize_connection()
        self.thread = SerialHalfDuplex(instance=self)
        self.thread.start()
    
    # ......................... #
    
    def initialize_connection(self):
        self.serial = Serial(self.port)
        self.serial.write('STATUS?\\n'.encode())
        self.serial.flush()
        f = self.serial.read(1)
        self.serial.flush()
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

        return f.decode()
    
    # ......................... #

# ------------------------- #