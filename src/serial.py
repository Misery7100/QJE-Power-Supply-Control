import re

from typing import List

import serial.tools.list_ports as list_ports

# ------------------------- #

def parse_ports() -> List[str]:
    """
    Check available comports and filter it with matches.

    Returns:
        List[str]: list of available serial ports
    """

    match1 = 'Silicon Labs'
    match2 = 'USB to UART Bridge'

    available = []

    for port, desc, _ in sorted(list_ports.comports()):
        if re.search(match1, desc) or re.search(match2, desc):
            available.append(port)
    
    return available

# ------------------------- #