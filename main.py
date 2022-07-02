import os
os.environ['KIVY_IMAGE'] = 'pil'

# ------------------------- #

from kivy.config import Config
Config.set('graphics', 'resizable', False)

from kivy.properties import ObjectProperty
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFillRoundFlatButton
from pathlib import Path

from src.supply import *
from src.backend import AppBackend

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

        self.theme_cls.primary_palette = "Green"

        self.screen = MDScreen()
        self.grid = MDBoxLayout(orientation='vertical')
        self.grid.spacing = 3 #! hardcoded shit
        self.grid.md_bg_color = (35 / 255, 35 / 255, 35 / 255, 1) #! hardcoded shit

        self.app_backend = AppBackend(app=self)
        self.psu_widgets = dict()
        self.backends = dict()
        self.dialog = None

        connected = self.app_backend.check_initial_connection()

        if not connected:
            Window.size = (280, 350)
            self.show_alert_dialog()

        else:
            self.app_backend.build_app_screen() 
            self.app_backend.start()
    
    # ......................... #

    def build(self):
        return self.screen
    
    # ......................... #

    def reset_backends(self, *args):

        # reset only available psus
        available_backends = list(filter(lambda x: x.port in self.app_backend.working, self.backends.values()))
        list(map(lambda x: x.reset(), available_backends))

    # ......................... #

    def show_alert_dialog(self):
        self.dialog = MDDialog(
            text="No PSUs found",
            buttons=[
                MDFillRoundFlatButton(
                    text="Close",
                    on_release=self.dialog_close
                    #theme_text_color="Custom",
                    #text_color=self.theme_cls.primary_color,
                ),
            ]
        )
        self.dialog.open()
    
    # ......................... #

    def dialog_close(self, *args):
        self.dialog.dismiss(force=True)
        self.stop()

# ------------------------- #

if __name__ == '__main__':
    app = App()
    app.run()
    app.reset_backends()