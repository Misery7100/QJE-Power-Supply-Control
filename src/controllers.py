import os
from re import L
import serial.tools.list_ports as list_ports
import time
import yaml

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
from pathlib import Path
from serial import Serial

from .utils import dotdict

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent

with open(os.path.join(BASE_DIR, 'yml/props.yml'), 'r') as stream:
    global_props = dotdict(yaml.safe_load(stream))

# ------------------------- #

class UnitIndicator(MDBoxLayout):

    def __init__(self, label='A', **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 5

        self.box = MDBoxLayout(size_hint_y=0.4, orientation='vertical')
        self.empty_box1 = MDBoxLayout(size_hint_y=0.2, orientation='vertical')
        self.empty_box2 = MDBoxLayout(size_hint_y=0.4, orientation='vertical')

        self.label = MDLabel(
                text=label,
                theme_text_color="Custom",
                text_color=global_props.const_indicator.text_color,
                pos_hint={"center_x": 0.6, "center_y": 0.3}
            )
        
        self.box.add_widget(self.label)
        self.add_widget(self.empty_box1)
        self.add_widget(self.box)
        self.add_widget(self.empty_box2)

# ------------------------- #

class ConstantIndicator(MDBoxLayout):

    def __init__(self, label='C.#', **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 5

        self.box = MDBoxLayout(size_hint_y=0.4, orientation='vertical')
        self.empty_box1 = MDBoxLayout(size_hint_y=0.2, orientation='vertical')
        self.empty_box2 = MDBoxLayout(size_hint_y=0.4, orientation='vertical')

        self.label = MDLabel(
                text=label,
                theme_text_color="Custom",
                text_color=global_props.const_indicator.text_color,
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                #size_hint=(1, 0.4)
            )

        self.indicator = MDIconButton(
                icon='checkbox-blank-circle',
                pos_hint={"center_x": 0.5, "center_y" : 0.5},
                theme_text_color="Custom",
                text_color=global_props.const_indicator.indicator_color,
                #size_hint=(1, 1.5)
            )

        self.indicator_with_effects = EffectWidget()
        self.indicator_with_effects.add_widget(self.indicator)
        self.indicator_with_effects.effects = [
                # HorizontalBlurEffect(size=3.5), 
                # VerticalBlurEffect(size=3.5),
                # FXAAEffect()
            ]
        
        #self.indicator.disabled = True
        self.label.font_size = global_props.const_indicator.font_size
        self.indicator.user_font_size = global_props.const_indicator.indicator_size

        self.box.add_widget(self.label)
        self.box.add_widget(self.indicator_with_effects)
        self.add_widget(self.empty_box1)
        self.add_widget(self.box)
        self.add_widget(self.empty_box2)

# ------------------------- #

class SingleBitController(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 5

        self.increment = MDIconButton(
                icon='chevron-up', 
                pos_hint={"center_x": 0.5},
                theme_text_color="Custom",
                text_color=global_props.inc_dec_btns.text_color
            )
        self.decrement = MDIconButton(
                icon='chevron-down', 
                pos_hint={"center_x": 0.5},
                theme_text_color="Custom",
                text_color=global_props.inc_dec_btns.text_color
            )
        self.bit_field = MDLabel(
                text='0',
                halign='center',
                pos_hint={"center_x": 0.5},
                theme_text_color="Custom",
                text_color=global_props.bit.text_color
            )

        self.bit_field.font_size = global_props.bit.font_size
        self.bit_field.font_name = global_props.bit.font_family

        self.increment.bind(on_press=self.incrementation) # ? use partial further ? #
        self.decrement.bind(on_press=self.decrementation) # ? use partial further ? #

        self.add_widget(self.increment)
        self.add_widget(self.bit_field)
        self.add_widget(self.decrement)
    
    # ......................... #

    def incrementation(self, *args, **kwargs):
        pass

    # ......................... #

    def decrementation(self, *args, **kwargs):
        pass

# ------------------------- #

class UniversalController(MDBoxLayout):

    bits = list()

    # ......................... #

    def __init__(
            self, 
            bits: int = 4, 
            point_pos: int = None,
            const_indicator_label: str = "C. #", 
            unit_indicator_label: str = "A",
            **kwargs
        ):

        super().__init__(**kwargs)

        self.orientation = 'horizontal'
        self.md_bg_color = (0, 0, 0, 0.9)

        self.const_indicator = ConstantIndicator(label=const_indicator_label)
        self.unit_indicator = UnitIndicator(label=unit_indicator_label)

        self.add_widget(self.const_indicator)

        self.float_point = MDLabel(
            text='.', 
            pos_hint={"center_x": 0.5},
            halign='center',
            theme_text_color="Custom",
            text_color=global_props.bit.text_color,
            size_hint_x=0.1
        )

        self.float_point.font_size = global_props.bit.font_size
        self.float_point.font_name = global_props.bit.font_family

        for i in range(bits):
            if point_pos == i:
                self.add_widget(self.float_point)

            dbc = SingleBitController(pos_hint={"center_y": 0.5}, width=80)
            self.bits.append(dbc)
            self.add_widget(dbc)
        
        self.add_widget(self.unit_indicator)
    
    # ......................... #



# ------------------------- #

class CurrentController(UniversalController):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# ------------------------- #

class VoltageController(UniversalController):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

# ------------------------- #