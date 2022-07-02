# QJE Power Supply Control

Cross-platform app for control QJ300xP power supplies by QJE

<p float="left">
  <img src="https://imgur.com/VShvCgV.png" width="220" />
  <img src="https://imgur.com/A3bu1XU.png" width="220" />
</p>

## Features

## Protocol

| Command       | Description                                                                                                                                                                            |
|---------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| VOUT1?        | Get output voltage                                                                                                                                                                     |
| IOUT1?        | Get output current                                                                                                                                                                     |
| VSET1:xx.xx | Set voltage on PSU to `xx.xx`                                                                                                                                                          |
| ISET1:x.xxx | Set current on PSU to `x.xxx`                                                                                                                                                          |
| VSET1?        | Get set voltage                                                                                                                                                                        |
| ISET1?        | Get set current                                                                                                                                                                        |
| STATUS?       | Get current status in format `xxx` where  `0xx` corresponds to constant current,  `1xx` --- constant voltage, `x0x` --- enabled output,  `x1x` --- disabled output (`x` means `0` or `1`) |
| OUTPUTx     | `x = 1` --- enable, `x = 0` --- disabled PSU output output                                                                                                                                           |
| \n            | End symbol for any command                                                                                                                                                             |