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
from threading import Thread

from src.controllers import UniversalController

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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.screen = MDScreen()
        self.layout = MDBoxLayout(orientation='vertical')

        ctrl1 = UniversalController(point_pos=1, height=160, width=250, size_hint=(None, None))
        ctrl2 = UniversalController(point_pos=2, height=160, width=250, size_hint=(None, None))

        self.layout.add_widget(ctrl1)
        self.layout.add_widget(ctrl2)
        self.screen.add_widget(self.layout)
    
    # ......................... #

    def build(self):
        return self.screen

# ------------------------- #

if __name__ == '__main__':
    App().run()