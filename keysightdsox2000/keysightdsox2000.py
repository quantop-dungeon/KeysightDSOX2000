import pyvisa
import numpy as np

from typing import Union


class DSOX2000:
    """A class for communication with DSO-X 2000-series scopes.

    Attributes:
        comm: A visa communication resource.

    Args:
        address: 
            Visa resource name.
        read_termination, write_termination:
            Command terminations used when communicating with the instrument.
            It was observed that even scopes of the same model and the same 
            firmware version can expect different terminations, but the current 
            default seems to work for all of them. 
        rsc_kwargs: 
            Other keyword arguments passed to ResourceManager.open_resource()
            to configure the created resource. See the documentation of pyvisa
            module for their details.
    """
    comm = None

    def __init__(self, address: str = "TCPIP0::dx2024a.qopt.nbi.dk::INSTR",
                 read_termination: str = "\n",
                 write_termination: str = "\n",
                 **rsc_kwargs):

        rsc_kwargs['read_termination'] = read_termination
        rsc_kwargs['write_termination'] = write_termination

        # Connects to the device.
        rm = pyvisa.ResourceManager()
        self.comm = rm.open_resource(address, **rsc_kwargs)

        # Asks for an identifier and validates it.
        id = self.comm.query("*IDN?")
        if not "dso-x 20" in id.lower():
            raise IOError(f"The device returns an wrong IDN string: {id}")

        # Sets the waveform output format to: signed binary,
        # two bytes per data point, most significan bit byte first,
        # always request the maximum number of points in the trace.
        self.comm.write(":WAVeform:FORMat WORD;"
                        ":WAVeform:UNSigned OFF;"
                        ":WAVeform:BYTeorder MSBFirst;"
                        ":WAVeform:POINts:MODE MAXimum")

    def get_trace(self, channel: Union[int, str] = 1) -> dict:
        """Reads a single trace from the specified scope channel. Requests 
        the maximum number of samples.

        Args:
            channel: 
                Channel name or number. Can be an integer for input channels or 
                a string admissible by waveform:source, e.g. one of the
                ('chan<n>', 'func', 'math', 'wmem').  

        Returns:
            A dictionary with the x and y data (under the keys 'x' and 'y'), 
            and optionally metadata.
        """

        if type(channel) is not str:
            channel = "CHAN%i" % channel

        d = {"x": None, "y": None}  # Output dictionary

        # If the data is read from a regular input channel, adds the axis names
        # and the units. Otherwise (e.g. if is the data is FFT from the func
        # channel), the x and y values are still read out, but currently no
        # information about the axes labels is added.
        if channel.lower().startswith('chan'):
            d.update({"xlabel": "Time (s)", "ylabel": "Voltage (V)"})

        # Configures the waveform source.
        self.comm.write(f":WAVeform:SOURce {channel}")

        # Reads the y values. The data type is as configured in init:
        # short (two-byte integer), with the most significan byte first.
        y_raw = self.comm.query_binary_values(":WAVeform:DATA?",
                                              datatype="h",
                                              is_big_endian=True,
                                              container=np.ndarray)

        resp = self.comm.query(":WAVeform:XINCrement?;"
                               ":WAVeform:XORigin?;"
                               ":WAVeform:YINCrement?;"
                               ":WAVeform:YORigin?;"
                               ":ACQuire:TYPE?")
        rln = resp.split(sep=';')

        x_inc, x_0, y_inc, y_0, acq_type = *[float(s) for s in rln[:4]], rln[4]

        if acq_type.lower().startswith('peak'):
            # In the peak detection mode, there are two y points for one time 
            # stamp, for the min and max values.
            x_raw_ = np.arange(len(y_raw) // 2)
            x_raw = np.reshape(np.vstack([x_raw_, x_raw_]).T, (len(y_raw),))
        else:
            x_raw = np.arange(len(y_raw))

        # Calculates the x axis and scales the y data.
        d["x"] = x_0 + x_inc * x_raw
        d["y"] = y_0 + y_inc * y_raw

        return d

    def aquire_single(self):
        """Initiates the aquisition of a single trace (same as pressing 
        the SINGLE button).
        """
        self.comm.write(":SINGle")

    def acquire_continuous(self):
        """Initiates continuous data acquitions (same as pressing 
        the RUN button).
        """
        self.comm.write(":RUN")

    def stop_acquisition(self):
        """Stops data aquisition (same as pressing the STOP button)."""
        self.comm.write(":STOP")

    def set_time_per_division(self, t: Union[float, str]):
        """Set horizontal time scale per division in seconds."""
        self.comm.write(f":TIMebase:SCALe {t}")

    def set_total_time(self, t: Union[float, str]):
        """Sets horizontal time in seconds (total time)."""
        self.comm.write(f":TIMebase:RANGe {t}")

    def measure_average_voltage(self, channel: Union[int, str] = 1,
                                interval="display") -> float:
        """Reads the average voltage of a given channel in volts.

        See p. 370 in programming manual for more details:
        The :MEASure:VAVerage? query returns the average value of an integral
        number of periods of the signal. If at least three edges are not
        present, the oscilloscope averages all data points.
        """
        if type(channel) is not str:
            channel = "CHAN%i" % channel

        v_avg = self.comm.query(f":MEASure:VAVerage? {interval},{channel}")
        return float(v_avg)
