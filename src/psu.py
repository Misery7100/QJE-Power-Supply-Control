from serial import Serial

from src.utils import *

# ------------------------- #

class PSU:
    """
    QJE-like PSU control with serial. 
    """

    # default values for QJ3003P and QJ3005P
    max_voltage = 30.00
    max_current = 3.000

    # ......................... #

    def __init__(self, port: str, **kwargs) -> None:
        
        self.port = port
        self.serial = Serial(self.port, **kwargs)
    
    # ......................... #

    def write(self, query: str):
        """
        _summary_

        Args:
            query (str): as
        """

        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        self.serial.write(f'{query}{qje.end_sym}'.encode())
        self.serial.flush()
    
    # ......................... #

    def read(self):
        f = self.serial.readline().decode().strip()

        return f
