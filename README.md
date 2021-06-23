# DSO-X 2024 Python scope interface
This is a PyVISA-based interface to the Keysight DSO-X 2024 scope. Implements a subset of functionality relevant for QUANTOP. Uses binary data transfer, which is significantly faster than the previous ASCII-based approach

## Installation
Clone this repo and change into its directory, e.g. by running
```
git clone https://github.com/quantop-dungeon/DSOX2024.git
cd dsox2024
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
The basic use of this module is very easy. To acquire the current trace from channel 1, for example, use:

```python
from dsox2024 import DSOX2024

scope = DSOX2024(address=u'TCPIP0::dx2024a.qopt.nbi.dk::INSTR')
ts, Vs = scope.get_trace(channel=1)

# ts and Vs are flat numpy arrays containing time values (in seconds)
# and voltages (in volts), with same shape
```
