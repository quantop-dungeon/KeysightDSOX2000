# -*- coding: utf-8 -*-
"""
REMOTE CONTROL OF THE KEYSIGHT INFIIVISION DSOX2024A Scope
Version 1.0 (2017/03/02)

Connection via LAN, Find VISA TCP/IP Connect String
in the browser interface

@author: Bones

Information:

quarpi.qopt.nbi.dk/other/membrane/Equipment/Commercial/Keysight DSOX2024A/2000_series_prog_guide.pdf
    
"""

import pyvisa as visa
import numpy as np
from time import sleep


class DSOX2024:
    def __init__(self, address=u'TCPIP0::dx2024a.qopt.nbi.dk::INSTR'):
        """ 
        Connect to scope.
        """
        rm = visa.ResourceManager()
        self.scope = rm.open_resource(address)

        # Ask for response and validate
        scope_id = self.scope.query('*IDN?')
        if not scope_id.startswith("AGILENT TECHNOLOGIES,DSO-X 2024A"):
            raise IOError(f"Incorrect IDN string of device: {scope_id}")

        # Set output format to ascii
        self.scope.write(':WAV:FORM ascii')

    def _preamb_to_ts(self, preamb):
        """
        Transform the waveform preamble string to a more
        human-readable dictionary and construct time axis. 
        Only via the waveform preamble can scope trace time
        base information be obtained.
        """
        # Clean the input
        if preamb[-1] == '\n':
            preamb = preamb[:-1]
        n = preamb.count(',')+1
        entries = [[]]*n
        ind1 = 0
        ind2 = preamb.find(',')
        for ii in range(n-1):
            entries[ii] = preamb[ind1:ind2]
            ind1 = ind2 + 1
            ind2 = ind1 + preamb[ind1:].find(',')
        entries[-1] = preamb[ind1:]
        # Define what the heck the codes mean (p. 966 of Manual)
        form = {'+0': 'BYTE', '+1': 'WORD', '+4': 'ASCii'}
        typ = {'+2': 'AVERage', '+0': 'NORMal', '+1': 'PEAK', '+3': 'HRES'}
        # Build dictionary
        dic = {}
        dic.update({'format': form[entries[0]]})
        dic.update({'acq. type': typ[entries[1]]})
        dic.update({'points': int(entries[2])})
        dic.update({'av. count': int(entries[3])})
        dic.update({'x inc': float(entries[4])})
        dic.update({'x origin': float(entries[5])})
        dic.update({'x origin index': int(entries[6])})
        dic.update({'y inc': float(entries[7])})
        dic.update({'y origin': float(entries[8])})
        dic.update({'y origin index': int(entries[9])})
        x0 = dic['x origin']
        x0_n = dic['x origin index']
        dx = dic['x inc']
        N = dic['points']
        return np.linspace(x0-dx*x0_n, x0-dx*x0_n+dx*N, N)

    def _ascii_to_np(self, data):
        """
        Convert an ascii data array from the scope to
        a numpy array.
        """
        # Remove weird header
        if data.find('#') != -1:
            count = data.find('#') + 1
            while data[count].isdigit():
                count += 1
            data = data[count:]
        # Remove final newline character
        if data[-1] == '\n':
            data = data[:-1]

        # Initialise output array
        N = data.count(',')
        npdata = np.zeros(N+1, dtype=np.float64)
        ind1 = 0
        ind2 = data.find(',')
        for ii in range(N):
            npdata[ii] = float(data[ind1:ind2])
            ind1 = ind2+1
            ind2 = data[ind1:].find(',')+ind1
        npdata[N] = float(data[ind1:])

        return npdata


    def get_trace(self, channel=1, points=None):
        """
        Get a single trace from channel.
        """
        if channel not in range(1, 4+1):
            raise ValueError("Incorrect channel setting")
        
        self.scope.write(":WAV:SOUR CHAN" + str(channel))
        
        if points is not None:
            self.scope.write(":WAV:POIN " + str(int(points)))

        # Stop aquisition
        self.scope.write(':STOP')
        # Get data and preamble
        data = self.scope.query(":WAVeform:DATA?")
        preamb = self.scope.query(':WAVeform:PREamble?')
        # Continue aquisition
        self.scope.write(':RUN')
        # Convert data
        xdata = self._preamb_to_ts(preamb)
        ydata = self._ascii_to_np(data)
        return xdata, ydata


    def change_time_mode(self, mode='MAIN'):
        '''
        Can choose between the following options (p. 581 in programming manual)

        MAIN — The normal time base mode is the main time base. It is the default time
        base mode after the *RST (Reset) command.

        WINDow — In the WINDow (zoomed or delayed) time base mode,
        measurements are made in the zoomed time base if possible; otherwise, the
        measurements are made in the main time base.

        XY — In the XY mode, the :TIMebase:RANGe, :TIMebase:POSition, and
        :TIMebase:REFerence commands are not available. No measurements are
        available in this mode.

        ROLL — In the ROLL mode, data moves continuously across the display from
        left to right. The oscilloscope runs continuously and is untriggered. The
        :TIMebase:REFerence selection changes to RIGHt.
        '''
        if mode not in ['MAIN', 'WINDow', 'XY', 'ROLL']:
            msg = 'Time mode not recognized. Choose between MAIN, WINDow, XY or ROLL.'
            raise ValueError(msg)
        
        currMode = self.scope.query(':TIMebase:MODE?').split('\n')[0]
        #print('[+] Changing from {} to {} mode.'.format(currMode, mode))


    def setTimePerDivision(self, timePerDiv=2.0):
        '''
        Set horizontal time scale per division in seconds.
        '''
        timescale = float(timePerDiv)
        print('[+] Changing to {:.1f}s per division time scale.'.format(timescale))
        self.scope.write(':TIMebase:SCALe {:.5f}'.format(timescale))


    def setTotalTime(self, totalTimescale=2.0):
        '''
        Set horizontal time in seconds (total time).
        '''
        timescale = float(totalTimescale)
        print('[+] Changing to a total time scale of {:.1f}s .'.format(timescale))
        self.scope.write(':TIMebase:RANGe {:.5f}'.format(timescale))


    def measureAverageVoltage(self, channel=1, interval='DISPlay'):
        '''
        Returns average voltage of a given channel in volts.
        See p. 370 in programming manual:
        The :MEASure:VAVerage? query returns the average value of an integral
        number of periods of the signal. If at least three edges are not present,
        the oscilloscope averages all data points.
        '''
        channel = int(channel)
        VAverage = self.scope.query(':MEAS:VAV? {},CHAN{:d}'.format(interval, channel))
        print('[+] Average voltage of channel {:d} is {:.3f}V'.format(channel, float(VAverage)))
        return float(VAverage)

    def close(self):
        self.scope.close()


if __name__ == '__main__':
    scope = DSOX2024()
    scope.changeTimeMode(mode='ROLL')
    scope.setTimePerDivision(timePerDiv=10.0)
    sleep(10)
    scope.measureAverageVoltage(channel=1)
    scope.close()
#    scope.changeTimeMode(mode='ROLL')
#    scope.setTimePerDivision(timePerDiv=2.0)
#    sleep(2)
#    xdata, ydata = scope.get_trace(channel=1, points=100)
#
#    scope.setTimePerDivision(timePerDiv=0.1)
#    scope.changeTimeMode(mode='MAIN')
#
#    scope.close()
#
#    import pylab as plt
#    plt.figure(figsize=(10, 7))
#    plt.plot(xdata, ydata)
#    plt.xlabel('Time (s)')
#    plt.ylabel('Voltage (V)')
#    plt.minorticks_on()
#    plt.tight_layout()
    