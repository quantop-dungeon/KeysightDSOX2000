# -*- coding: utf-8 -*-

import pyvisa as visa
import numpy as np

class DSOX2000:
    def __init__(self, address="TCPIP0::dx2024a.qopt.nbi.dk::INSTR"):
        """Connect to scope."""
        rm = visa.ResourceManager()
        self.scope = rm.open_resource(address)

        self.scope.read_termination = '\n'
        self.scope.write_termination = '\n'

        # Ask for response and validate
        scope_id = self.scope.query("*IDN?")
        if not scope_id.startswith("AGILENT TECHNOLOGIES,DSO-X 2024A"):
            raise IOError(f"Incorrect IDN string of device: {scope_id}")

        # Set output format to signed binary (way faster)
        self.scope.write(":WAV:FORM BYTE")
        self.scope.write(":WAV:UNS OFF")
        self.scope.write(":WAV:points:mode max")

    def get_trace(self, channel=1):
        """Get a single trace from channel. Automatically gets the maximum number
        of samples
        """
        if channel not in range(1, 4 + 1):
            raise ValueError("Incorrect channel number")

        self.scope.write(":WAV:SOUR CHAN" + str(channel))

        # Stop aquisition
        self.scope.write(":STOP")

        # Get data, plus x and y scales
        data = self.scope.query_binary_values(":WAVeform:DATA?", datatype="b")

        x_inc = float(self.scope.query(":wav:xinc?"))
        x_0 = float(self.scope.query(":wav:xorigin?"))

        y_inc = float(self.scope.query(":wav:yinc?"))
        y_0 = float(self.scope.query(":wav:yorigin?"))

        # Total number of points, used later to generate the t axis
        n = len(data)

        # Convert data to NumPy, following the Programming Manual. It states
        # that xorigin and yorigin correspond to the first datapoint
        xdata = x_0 + x_inc * np.arange(n)
        ydata = y_0 + y_inc * (np.array(data))

        # Continue acquisition
        self.scope.write(":RUN")

        return xdata, ydata

    def change_time_mode(self, mode="MAIN"):
        """
        Can choose between the following options (p. 581 in programming manual)

        MAIN — The normal time base mode is the main time base. It is the
        default time base mode after the *RST (Reset) command.

        WINDow — In the WINDow (zoomed or delayed) time base mode,
        measurements are made in the zoomed time base if possible; otherwise,
        the measurements are made in the main time base.

        XY — In the XY mode, the :TIMebase:RANGe, :TIMebase:POSition, and
        :TIMebase:REFerence commands are not available. No measurements are
        available in this mode.

        ROLL — In the ROLL mode, data moves continuously across the display
        from left to right. The oscilloscope runs continuously and is
        untriggered.
        The :TIMebase:REFerence selection changes to RIGHt.
        """
        if mode not in ["MAIN", "WINDow", "XY", "ROLL"]:
            msg = (
                "Time mode not recognized. Choose between"
                " MAIN, WINDow, XY or ROLL."
            )
            raise ValueError(msg)

    def setTimePerDivision(self, timePerDiv=2.0):
        """
        Set horizontal time scale per division in seconds.
        """
        timescale = float(timePerDiv)
        print(
            "[+] Changing to {:.1f}s per division time scale.".format(
                timescale
            )
        )
        self.scope.write(":TIMebase:SCALe {:.5f}".format(timescale))

    def setTotalTime(self, totalTimescale=2.0):
        """
        Set horizontal time in seconds (total time).
        """
        timescale = float(totalTimescale)
        print(
            "[+] Changing to a total time scale of {:.1f}s .".format(timescale)
        )
        self.scope.write(":TIMebase:RANGe {:.5f}".format(timescale))

    def measureAverageVoltage(self, channel=1, interval="DISPlay"):
        """
        Returns average voltage of a given channel in volts.
        See p. 370 in programming manual:
        The :MEASure:VAVerage? query returns the average value of an integral
        number of periods of the signal. If at least three edges are not
        present, the oscilloscope averages all data points.
        """
        channel = int(channel)
        VAverage = self.scope.query(
            ":MEAS:VAV? {},CHAN{:d}".format(interval, channel)
        )
        print(
            "[+] Average voltage of channel {:d} is {:.3f}V".format(
                channel, float(VAverage)
            )
        )
        return float(VAverage)
