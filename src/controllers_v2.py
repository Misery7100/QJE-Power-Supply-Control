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

from .utils import dotdict

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent

with open(os.path.join(BASE_DIR, 'yml/style.yml'), 'r') as stream:
    style = dotdict(yaml.load(stream, Loader=yaml.Loader))

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
                text_color=style.unit_indicator.text_color,
                pos_hint={"center_x": 0.6, "center_y": 0.3}
            )
        
        self.label.font_size = style.unit_indicator.font_size
        
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
        self.empty_box1 = MDBoxLayout(size_hint_y=0.25, orientation='vertical')
        self.empty_box2 = MDBoxLayout(size_hint_y=0.35, orientation='vertical')

        self.label = MDLabel(
                text=label,
                theme_text_color="Custom",
                text_color=style.const_indicator.text_color,
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            )

        self.indicator = MDIconButton(
                icon='checkbox-blank-circle',
                pos_hint={"center_x": 0.5, "center_y" : 0.5},
                theme_text_color="Custom",
                text_color=style.const_indicator.indicator_color_off,
                ripple_scale=0
            )

        self.label.font_size = style.const_indicator.font_size
        self.indicator.user_font_size = style.const_indicator.indicator_size
        self.indicator.line_color = style.const_indicator.indicator_color_off

        self.box.add_widget(self.label)
        self.box.add_widget(self.indicator)

        self.add_widget(self.empty_box1)
        self.add_widget(self.box)
        self.add_widget(self.empty_box2)
    
    # ......................... #
    
    def indicator_on(self):
        self.indicator.text_color = style.const_indicator.indicator_color_on
    
    # ......................... #

    def indicator_off(self):
        self.indicator.text_color = style.const_indicator.indicator_color_off

# ------------------------- #

class SingleBitCtrlWidget(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'
        self.spacing = 10
        self.padding = 5

        self.increment = MDIconButton(
                icon='chevron-up', 
                pos_hint={"center_x": 0.5},
                theme_text_color="Custom",
                text_color=style.inc_dec_btns.text_color,
                ripple_scale=0.8
            )
        self.decrement = MDIconButton(
                icon='chevron-down', 
                pos_hint={"center_x": 0.5},
                theme_text_color="Custom",
                text_color=style.inc_dec_btns.text_color,
                ripple_scale=0.8
            )
        self.bit_field = MDLabel(
                text='0',
                halign='center',
                pos_hint={"center_x": 0.5},
                theme_text_color="Custom",
                text_color=style.bit.text_color
            )

        self.bit_field.font_size = style.bit.font_size
        self.bit_field.font_name = style.bit.font_family

        self.add_widget(self.increment)
        self.add_widget(self.bit_field)
        self.add_widget(self.decrement)

# ------------------------- #

class UniversalCtrlWidget(MDBoxLayout):

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
        self.bits = []
        self.point_pos = point_pos

        self.md_bg_color = style.universal_ctrl.background
        self.line_color = style.universal_ctrl.line_color
        self.line_width = style.universal_ctrl.line_width

        self.const_indicator = ConstantIndicator(label=const_indicator_label, size_hint_x=0.8)
        self.unit_indicator = UnitIndicator(label=unit_indicator_label)

        self.add_widget(self.const_indicator)

        self.float_point = MDLabel(
            text='.', 
            pos_hint={"center_x": 0.5},
            halign='center',
            theme_text_color="Custom",
            text_color=style.bit.text_color,
            size_hint_x=0.1
        )

        self.float_point.font_size = style.bit.font_size
        self.float_point.font_name = style.bit.font_family

        for i in range(bits):
            if self.point_pos == i:
                self.add_widget(self.float_point)

            dbc = SingleBitCtrlWidget(pos_hint={"center_y": 0.5}, width=80)
            self.bits.append(dbc)
            self.add_widget(self.bits[i])
        
        self.add_widget(self.unit_indicator)
    
    # ......................... #

    def set_value(self, value: str):

        for i, sym in enumerate(value.replace('.', '')):
            self.bits[i].bit_field.text = sym
    
    # ......................... #

    def disable_digits(self):
        for bit in self.bits:
            bit.bit_field.disabled = True
            bit.increment.text_color = "#000000"
            bit.decrement.text_color = "#000000"
        
        self.float_point.disabled = True
        
    # ......................... #

    def enable_digits(self):
        for bit in self.bits:
            bit.bit_field.disabled = False
            bit.increment.text_color = style.inc_dec_btns.text_color
            bit.decrement.text_color = style.inc_dec_btns.text_color
        
        self.float_point.disabled = False

# ------------------------- #

class CurrentCtrlWidget(UniversalCtrlWidget):

    def __init__(self, **kwargs):
        kwargs.update(dict(
            point_pos=1,
            const_indicator_label="C.C", 
            unit_indicator_label="A"
        ))
        super().__init__(**kwargs)

# ------------------------- #

class VoltageCtrlWidget(UniversalCtrlWidget):

    def __init__(self, **kwargs):
        kwargs.update(dict(
            point_pos=2,
            const_indicator_label="C.V", 
            unit_indicator_label="V"
        ))
        super().__init__(**kwargs)

# ------------------------- #

class OutputButton(MDFillRoundFlatButton):

    def __init__(self, **kwargs):
        kwargs.update(dict(
            text='OUTPUT', 
            size_hint_y=0.1,
            theme_text_color="Custom",
            text_color=style.output_btn.text_color,
            ripple_scale=0
        ))
        super().__init__(**kwargs)

        self.md_bg_color = style.output_btn.background_off
        self.value = 0

        self.bind(on_press=self.toggle_output_color)

    # ......................... #

    def toggle_output_color(self, *args):
        colors = [style.output_btn.background_off, style.output_btn.background_on]
        self.value = (self.value + 1) % 2
        self.md_bg_color = colors[self.value]

# ------------------------- #