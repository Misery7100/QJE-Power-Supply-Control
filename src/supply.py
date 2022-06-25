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

from .controllers_v2 import *
from .thread import SerialHalfDuplex

# ------------------------- #

class PowerSupplyWidget(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'

        self.ctrl_layout = MDBoxLayout(orientation='vertical')
        self.ctrl_layout.padding = 10
        self.ctrl_layout.spacing = 10
        self.ctrl_layout.md_bg_color = (69 / 255, 69 / 255, 69 / 255, 1) #! hardcoded shit

        #self.ctrl_layout.line_color = (135 / 255, 135 / 255, 135 / 255, 1) #! hardcoded shit
        #self.ctrl_layout.line_width = 5 #! hardcoded shit

        self.title = MDLabel(
                text='No PSU', 
                size_hint_y=0.1,
                halign='center',
                theme_text_color="Custom",
                text_color="#dcdcdc", #! hardcoded shit
            )
        self.title.disabled = True
        
        self.output_button = OutputButton()
        self.v_ctrl = VoltageCtrlWidget()
        self.c_ctrl = CurrentCtrlWidget()

        self.ctrl_layout.add_widget(self.title)
        self.ctrl_layout.add_widget(self.v_ctrl)
        self.ctrl_layout.add_widget(self.c_ctrl)
        self.ctrl_layout.add_widget(self.output_button)

        self.add_widget(self.ctrl_layout)

# ------------------------- #
# ------------------------- #
# ------------------------- #
# ------------------------- #

class PowerSupplyControl(MDBoxLayout):

    def __init__(self, port, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'

        self.ctrl_layout = MDBoxLayout(orientation='vertical')
        self.ctrl_layout.padding = 10
        self.ctrl_layout.spacing = 10
        self.ctrl_layout.md_bg_color = (0, 0, 0, 0.4) #! hardcoded shit

        self.port = port
        self.output_status = 0

        self.title = MDLabel(
                text=port, 
                size_hint_y=0.1,
                halign='center',
                theme_text_color="Custom",
                text_color="#dcdcdc",
            )

        self.output_button = OutputButton(instance=self)
        #self.v_ctrl = VoltageController(instance=self)
        #self.c_ctrl = CurrentController(instance=self)

        self.ctrl_layout.add_widget(self.title)
        self.ctrl_layout.add_widget(self.v_ctrl)
        self.ctrl_layout.add_widget(self.c_ctrl)
        self.ctrl_layout.add_widget(self.output_button)

        self.add_widget(self.ctrl_layout)

        self.initialize_connection()

        self.thread = SerialHalfDuplex(instance=self)

        self.reset()
        self.thread.update_constant_indicators()
        self.thread.start()
        
    # ......................... #

    def reset(self):
        self.output_button.set_output_while(0)
        time.sleep(0.1)
        self.v_ctrl.change('00.00')
        time.sleep(0.1)
        self.c_ctrl.change('0.000')
    
    # ......................... #
    
    def initialize_connection(self):
        self.serial = Serial(self.port)

# ------------------------- #