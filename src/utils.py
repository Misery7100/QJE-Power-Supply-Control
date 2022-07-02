import os
import yaml

from kivy.core.text import LabelBase
from pathlib import Path

# ------------------------- #

class dotdict(dict):
    """
    Dict with dot notation access to dictionary elements.
    """
    
    def __getattr__(*args):
        val = dict.get(*args)
        return dotdict(val) if type(val) is dict else val

    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent

# load configuration files

with open(os.path.join(BASE_DIR, 'yml/qje_protocol.yml'), 'r') as stream:
    qje = dotdict(yaml.load(stream, Loader=yaml.Loader))

with open(os.path.join(BASE_DIR, 'yml/threads.yml'), 'r') as stream:
    cfg = dotdict(yaml.load(stream, Loader=yaml.Loader))

with open(os.path.join(BASE_DIR, 'yml/style.yml'), 'r') as stream:
    style = dotdict(yaml.load(stream, Loader=yaml.Loader))

# register digital-like font for kivy

LabelBase.register(
    name='DS-Digi',
    fn_regular=os.path.join(BASE_DIR, 'fonts/DS-DIGI.TTF')
)
