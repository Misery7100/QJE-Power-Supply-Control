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
#! doesn't work
class ExitPopup(MDDialog): # TODO: move inside src 

    def __init__(self, **kwargs):
        super(ExitPopup, self).__init__(**kwargs)
        content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text="Are you sure?",
                          size_hint_y=None,
                          valign='top')
        content.bind(texture_size=content.setter('size'))
        self.dialog = MDDialog(title="Close Application",
                               content_cls=content,
                               size_hint=(.3, None),
                               height=dp(200))

        self.dialog.add_action_button("Close me!",
                                      action=lambda *x: self.dismiss_callback())
        self.dialog.open()

    def dismiss_callback(self):
        self.dialog.dismiss()
        App.get_running_app().close_app()

# ------------------------- #

class App(MDApp):

    in_class = ObjectProperty(None)

    # ......................... #

    def __init__(self, cols: int = 3, **kwargs):
        super().__init__(**kwargs)

        self.screen = MDScreen()
        self.grid = MDBoxLayout(orientation='vertical')
        self.grid.spacing = 3
        self.grid.md_bg_color = (35 / 255, 35 / 255, 35 / 255, 1)

        ports = parse_ports()
        psu_widgets = []

        for i in range(2):
            ctrl = PowerSupplyWidget(
                height=350,
                width=280, 
                size_hint=(None, None)
            )
            psu_widgets.append(ctrl)

        num_rows = 0
        
        for i in range(0, len(psu_widgets), cols):

            row = MDBoxLayout(orientation='horizontal')
            row.spacing = 3
            num_rows += 1
            
            for j in range(cols):
                if i + j < len(psu_widgets):
                    row.add_widget(psu_widgets[i + j])

            self.grid.add_widget(row)

        bnd = Backend(psu_widgets[0], port=ports[0])

        self.backends = [bnd]
        self.screen.add_widget(self.grid)

        Window.size = (280 * min(len(psu_widgets), cols), 350 * num_rows) #! hardcoded
    
    # ......................... #

    def build(self):
        #Window.bind(on_request_close=self.on_request_close)
        return self.screen
    
    # ......................... #

    # def on_request_close(self, *args):
    #     ExitPopup()

    # ......................... #

    def reset_backends(self, *args):
        list(map(lambda x: x.reset(), self.backends))

# ------------------------- #

if __name__ == '__main__':
    app = App()
    app.run()
    app.reset_backends()