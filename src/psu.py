from serial import Serial

from src.utils import *

# ------------------------- #

class PSU:
    """
    QJE-like PSU control via comport. 
    """

    # default values for QJ3003P and QJ3005P
    max_voltage = 30.00 # V
    max_current = 3.000 # A

    # ......................... #

    def __init__(self, port: str, **kwargs) -> None:
        
        self.port = port
        self.serial = Serial(self.port, **kwargs)
    
    # ......................... #

    def write(self, query: str):
        """
        Write to PSU's comport.

        Args:
            query (str): query to write
        """

        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()
        self.serial.write(f'{query}{qje.end_sym}'.encode())
        self.serial.flush()
    
    # ......................... #

    def read(self) -> str:
        """
        Read value from PSU's comport.

        Returns:
            str: read line from the assigned port
        """

        try:
            f = self.serial.readline().decode().strip()
            return f
        except:
            return ''
