import os
os.environ['KIVY_IMAGE'] = 'pil'

from kivy.config import Config
Config.set('graphics', 'resizable', False)

# ------------------------- #

from kivy.properties import ObjectProperty
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFillRoundFlatButton

from src.supply import *
from src.utils import *
from src.backend import AppBackend

# ------------------------- #

class App(MDApp):
    """
    Cross-platform app for control QJ300xP power supplies by QJE.
    """

    # ......................... #

    def __init__(self, cols: int = 3, **kwargs):

        super().__init__(**kwargs)

        self.psu_widgets = dict()
        self.backends = dict()
        self.dialog = None

        # set main color palette
        self.theme_cls.primary_palette = style.main_app.color_palette

        # init screen and grid
        self.screen = MDScreen()
        self.grid = MDBoxLayout(orientation='vertical')
        self.grid.spacing = style.main_app.grid_spacing
        self.grid.md_bg_color = style.main_app.grid_background

        # init app backend and check are there connected PSUs
        self.app_backend = AppBackend(app=self)
        connected = self.app_backend.check_initial_connection()

        # show alert if no PSUs found
        if not connected:
            Window.size = (280, 350)
            self.show_alert_dialog()

        # build app screen according to number of found PSUs
        else:
            self.app_backend.build_app_screen(num_cols=cols) 
            self.app_backend.start()
    
    # ......................... #

    def build(self):
        return self.screen
    
    # ......................... #

    def reset_backends(self, *args):
        """
        Reset voltage, current to zero and disable output
        for all available PSUs, before exit.
        """

        available_backends = list(filter(
            lambda x: x.port in self.app_backend.working, 
            self.backends.values()
        ))
        list(map(lambda x: x.reset(), available_backends))

    # ......................... #

    def show_alert_dialog(self):
        """
        Show alert dialog if no PSUs found.
        """

        self.dialog = MDDialog(
            text="No PSUs found",
            buttons=[
                MDFillRoundFlatButton(
                    text="Close",
                    on_release=self.dialog_close
                )
            ]
        )
        self.dialog.open()
    
    # ......................... #

    def dialog_close(self, *args):
        """
        Stop app on alert dialog dismiss.
        """
        
        self.dialog.dismiss(force=True)
        self.stop()

# ------------------------- #

if __name__ == '__main__':
    app = App()
    app.run()
    app.reset_backends()