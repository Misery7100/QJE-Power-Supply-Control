import os
os.environ['KIVY_IMAGE'] = 'pil'

# ------------------------- #

import serial.tools.list_ports as list_ports
import time

from kivy.properties import ObjectProperty
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.core.text import LabelBase
from kivy.core.window import Window
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

from src.supply import *
from src.serial import parse_ports
from src.backend import Backend

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent

LabelBase.register(
    name='DS-Digi',
    fn_regular=os.path.join(BASE_DIR, 'src/fonts/DS-DIGI.TTF')
)

# ------------------------- #

class App(MDApp):

    in_class = ObjectProperty(None)

    # ......................... #

    def __init__(self, cols: int = 3, **kwargs):
        super().__init__(**kwargs)

        self.screen = MDScreen()
        self.grid = MDBoxLayout(orientation='vertical')

        self.grid.md_bg_color = (69 / 255, 69 / 255, 69 / 255, 1)

        ports = parse_ports()
        psu_widgets = []

        for i in range(4):
            ctrl = PowerSupplyWidget(
                height=350,
                width=280, 
                size_hint=(None, None)
            )
            psu_widgets.append(ctrl)

        num_rows = 0
        
        for i in range(0, len(psu_widgets), cols):

            row = MDBoxLayout(orientation='horizontal')
            num_rows += 1
            
            for j in range(cols):
                if i + j < len(psu_widgets):
                    row.add_widget(psu_widgets[i + j])

            self.grid.add_widget(row)

        bnd = Backend(psu_widgets[0], port=ports[0])

        self.screen.add_widget(self.grid)

        Window.size = (280 * cols, 350 * num_rows) #! hardcoded
    
    # ......................... #

    def build(self):
        return self.screen

# ------------------------- #

if __name__ == '__main__':
    App().run()