# DSO-X 2000 scope python interface
This is a PyVISA-based interface to Keysight DSO-X 2000 scopes. Implements a subset of functionality relevant for QUANTOP. Uses binary data transfer, which is significantly faster than the ASCII-based approach. Tested with DSO-X 2024. 

## Installation
Clone this repo and change into its directory, e.g. by running
```
git clone https://github.com/quantop-dungeon/KeysightDSOX2000.git
cd keysightdsox2000
```

Then one can install this as a package:

```bash
pip install .
```

To install this package while being to able to edit its files, install it in development mode:

```bash
pip install -e .
```

## Basic usage
To acquire the current trace from channel 1, for example, use:

```python
from keysightdsox2000 import DSOX2000

scope = DSOX2000(address=u'TCPIP0::dx2024a.qopt.nbi.dk::INSTR')
ts, Vs = scope.get_trace(channel=1)

# ts and Vs are flat numpy arrays containing time values (in seconds)
# and voltages (in volts), with same shape
```
