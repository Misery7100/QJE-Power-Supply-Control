# QJE Power Supply Control

Cross-platform app for control QJ300xP power supplies by QJE

Normal case             |  Disconnected case
:-------------------------:|:-------------------------:
<img src="https://imgur.com/VShvCgV.png" width="220" />  |  <img src="https://imgur.com/A3bu1XU.png" width="220" />

## Usage

For debug and test cases or some home usage you can install requirements and run the app as python scipt.
For end users better to build the app using [PyInstaller](https://pyinstaller.org/en/stable/).

You should connect all PSUs you need before the app run, because connection on the fly isn't implemented due PSU.

## Features

- Control multiple PSUs at the same time;
- Disconnection handling;
- Reset connected PSUs on close and on startup;
- UI similar to real PSU appearance.

## Bugs

- Digit controls overshoot due PSU UART hardware implementation;
- Output button overshoot.

## Protocol

| Query       | Description |
|---------------|--------------|
| VOUT1?        | Get output voltage |
| IOUT1?        | Get output current |
| VSET1:xx.xx | Set voltage on PSU to `xx.xx` |
| ISET1:x.xxx | Set current on PSU to `x.xxx` |
| VSET1? | Get set voltage |
| ISET1? | Get set current |
| STATUS? | Get current status in format `xxx` where  `0xx` corresponds to constant current,  `1xx` - constant voltage, `x0x` - enabled output,  `x1x` - disabled output, `x ∈ {0, 1}` |
| OUTPUTx | `x = 1` - enable, `x = 0` - disable PSU output |
| \n | End symbol for any query  |