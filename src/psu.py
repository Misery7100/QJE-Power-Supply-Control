import os
import time
import yaml

from pathlib import Path
from serial import Serial

from .thread import SerialHalfDuplexV2
from .utils import dotdict

# ------------------------- #

BASE_DIR = Path(__file__).resolve().parent

with open(os.path.join(BASE_DIR, 'yml/qje_protocol.yml'), 'r') as stream:
    qje = dotdict(yaml.load(stream, Loader=yaml.Loader))

with open(os.path.join(BASE_DIR, 'yml/threads.yml'), 'r') as stream:
    cfg = dotdict(yaml.load(stream, Loader=yaml.Loader))

# ------------------------- #

class PSU:

    max_voltage = 30.00
    max_current = 3.000

    # ......................... #

    def __init__(self, port: str) -> None:
        
        self.port = port
        self.serial = Serial(self.port, timeout=0.5)