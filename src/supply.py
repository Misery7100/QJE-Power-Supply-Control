from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from src.controllers import *

# ------------------------- #

class PowerSupplyWidget(MDBoxLayout):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = 'vertical'

        self.ctrl_layout = MDBoxLayout(orientation='vertical')
        self.ctrl_layout.padding = 10
        self.ctrl_layout.spacing = 10
        self.ctrl_layout.md_bg_color = (69 / 255, 69 / 255, 69 / 255, 1) #! hardcoded shit

        self.title = MDLabel(
                text='No PSU', 
                size_hint_y=0.1,
                halign='center',
                theme_text_color="Custom",
                text_color=style.psu_widget.text_color
            )
        
        self.output_button = OutputButton()
        self.v_ctrl = VoltageCtrlWidget()
        self.c_ctrl = CurrentCtrlWidget()

        self.ctrl_layout.add_widget(self.title)
        self.ctrl_layout.add_widget(self.v_ctrl)
        self.ctrl_layout.add_widget(self.c_ctrl)
        self.ctrl_layout.add_widget(self.output_button)

        self.add_widget(self.ctrl_layout)

        self.v_ctrl.disable_digits()
        self.c_ctrl.disable_digits()
        self.output_button.set_disconnected()