import os
import time
import yaml

from pathlib import Path
from serial import Serial

from src.utils import dotdict

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

    def __init__(self, port: str, **kwargs) -> None:
        
        self.port = port
        self.serial = Serial(self.port, **kwargs)
    
    # ......................... #

    def write(self, query):
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        self.serial.write(f'{query}{qje.end_sym}'.encode())
        self.serial.flush()
    
    # ......................... #

    def read(self):
        f = self.serial.readline().decode().strip()

        return f
