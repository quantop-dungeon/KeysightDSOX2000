# -*- coding: utf-8 -*-

import pyvisa as visa
import numpy as np

from typing import Union, Tuple
from numpy import ndarray


class DSOX2000:
    """Class for communication with DSO-X 2000-series scopes.

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

        self.comm.read_termination = '\n'
        self.comm.write_termination = '\n'

        # Asks for an identifier and validates it.
        id = self.comm.query("*IDN?")
        if not id.startswith("AGILENT TECHNOLOGIES,DSO-X 2024A"):
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

        # Stop aquisition
        self.comm.write(":STOP")

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

    def set_time_per_div(self, timePerDiv=2.0):
        """
        Set horizontal time scale per division in seconds.
        """
        timescale = float(timePerDiv)
        print(
            "[+] Changing to {:.1f}s per division time scale.".format(
                timescale
            )
        )
        self.comm.write(":TIMebase:SCALe {:.5f}".format(timescale))

    def set_total_time(self, totalTimescale=2.0):
        """
        Set horizontal time in seconds (total time).
        """
        timescale = float(totalTimescale)
        print(
            "[+] Changing to a total time scale of {:.1f}s .".format(timescale)
        )
        self.comm.write(":TIMebase:RANGe {:.5f}".format(timescale))

    def meas_avg_volt(self, channel=1, interval="DISPlay"):
        """
        Returns average voltage of a given channel in volts.
        See p. 370 in programming manual:
        The :MEASure:VAVerage? query returns the average value of an integral
        number of periods of the signal. If at least three edges are not
        present, the oscilloscope averages all data points.
        """
        channel = int(channel)
        VAverage = self.comm.query(
            ":MEAS:VAV? {},CHAN{:d}".format(interval, channel)
        )
        print(
            "[+] Average voltage of channel {:d} is {:.3f}V".format(
                channel, float(VAverage)
            )
        )
        return float(VAverage)
