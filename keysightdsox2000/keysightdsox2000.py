import pyvisa as visa
import numpy as np

from typing import Union, Tuple
from numpy import ndarray


class DSOX2000:
    """A class for communication with DSO-X 2000-series scopes.

    Attributes:
        comm: A communication resource.

    Args:
        address: Visa resource name.
    """
    comm = None

    def __init__(self, address: str = "TCPIP0::dx2024a.qopt.nbi.dk::INSTR"):
        # Connects to the device.
        rm = visa.ResourceManager()
        self.comm = rm.open_resource(address)

        self.comm.read_termination = "\n"
        self.comm.write_termination = "\n"

        # Asks for an identifier and validates it.
        id = self.comm.query("*IDN?")
        if not "dso-x 20" in id.lower():
            raise IOError(f"Incorrect IDN string of device: {id}")

        # Sets the waveform output format to signed binary.
        self.comm.write(":WAV:FORM BYTE")
        self.comm.write(":WAV:UNS OFF")
        self.comm.write(":WAV:points:mode max")

    def get_trace(self, channel: Union[int, str] = 1) -> Tuple[ndarray, ndarray,
                                                               dict]:
        """Reads a single trace from a scope channel. Requests the maximum
        number of samples.

        Args:
            channel: Channel name or number.

        Returns:
            A tuple (x, y, mdt).
        """

        self.comm.write(":WAV:SOUR CHAN" + str(channel))

        # Get data, plus x and y scales
        data = self.comm.query_binary_values(":WAVeform:DATA?", datatype="b")

        x_inc = float(self.comm.query(":wav:xinc?"))
        x_0 = float(self.comm.query(":wav:xorigin?"))

        y_inc = float(self.comm.query(":wav:yinc?"))
        y_0 = float(self.comm.query(":wav:yorigin?"))

        # Total number of points, used later to generate the x axis.
        n = len(data)

        # Convert data to NumPy, following the Programming Manual. It states
        # that xorigin and yorigin correspond to the first datapoint
        xdata = x_0 + x_inc * np.arange(n)
        ydata = y_0 + y_inc * (np.array(data))

        # Continue acquisition
        self.comm.write(":RUN")

        return (xdata, ydata, mdt)

    def aquire_single(self):
        """Initiates the aquisition of a single trace (same as pressing 
        the SINGLE button).
        """
        self.comm.write(':SINGle')

    def acquire_continuous(self):
        """Initiates continuous data acquitions (same as pressing 
        the RUN button).
        """
        self.comm.write(':RUN')

    def stop_acquisition(self):
        """Stops data aquisition (same as pressing the STOP button)."""
        self.comm.write(":STOP")

    def set_time_per_div(self, t):
        """
        Set horizontal time scale per division in seconds.
        """
        timescale = float(t)
        print(
            "[+] Changing to {:.1f}s per division time scale.".format(
                timescale
            )
        )
        self.comm.write(":TIMebase:SCALe {:.5f}".format(timescale))

    def set_total_time(self, t):
        """Sets horizontal time in seconds (total time).
        """
        timescale = float(t)
        print(
            "[+] Changing to a total time scale of {:.1f}s .".format(timescale)
        )
        self.comm.write(":TIMebase:RANGe {:.5f}".format(timescale))

    def meas_avg_voltage(self, channel=1, interval="DISPlay"):
        """Reads the average voltage of a given channel in volts.
        
        See p. 370 in programming manual for more details:
        The :MEASure:VAVerage? query returns the average value of an integral
        number of periods of the signal. If at least three edges are not
        present, the oscilloscope averages all data points.
        """
        channel = int(channel)
        v_avg = self.comm.query(
            ":MEAS:VAV? {},CHAN{:d}".format(interval, channel)
        )
        print(
            "[+] Average voltage of channel {:d} is {:.3f}V".format(
                channel, float(v_avg)
            )
        )
        return float(v_avg)
