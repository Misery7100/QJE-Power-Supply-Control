from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel

from src.components import *

# ------------------------- #

class PowerSupplyWidget(MDBoxLayout):
    """
    Power supply controling layout constructed using main controller components.
    """

    def __init__(self, **kwargs):
        
        super().__init__(**kwargs)

        self.orientation = 'vertical'

        # define main container layout
        self.ctrl_layout = MDBoxLayout(orientation='vertical')

        # load parameters from the configuration file
        self.ctrl_layout.padding = style.psu_widget.padding
        self.ctrl_layout.spacing = style.psu_widget.spacing
        self.ctrl_layout.md_bg_color = style.psu_widget.background

        # setup title
        self.title = MDLabel(
                text='No PSU', 
                size_hint_y=0.1,
                halign='center',
                theme_text_color="Custom",
                text_color=style.psu_widget.text_color
            )
        
        # add controllers
        self.output_button = OutputButton()
        self.v_ctrl = VoltageCtrlWidget()
        self.c_ctrl = CurrentCtrlWidget()

        # build layout
        self.ctrl_layout.add_widget(self.title)
        self.ctrl_layout.add_widget(self.v_ctrl)
        self.ctrl_layout.add_widget(self.c_ctrl)
        self.ctrl_layout.add_widget(self.output_button)
        self.add_widget(self.ctrl_layout)