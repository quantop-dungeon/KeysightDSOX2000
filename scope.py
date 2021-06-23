# -*- coding: utf-8 -*-
"""
REMOTE CONTROL OF THE KEYSIGHT INFIIVISION DSOX2024A Scope
Version 1.0 (2017/03/02)

Connection via LAN, Find VISA TCP/IP Connect String
in the browser interface

@author: Andi

Information:
\\quarpi\other\membrane\Equipment\Commercial\Keysight DSOX2024A\
2000_series_prog_guide.pdf
    
"""

import visa
import numpy as np

class connect:
    def __init__(self, address=u'TCPIP0::dx2024a::INSTR'):
        """ 
        Connect to scope.
        """
        rm = visa.ResourceManager()
        self.scope = rm.get_instrument(address)
        # Ask for response
        print(self.scope.ask('*IDN?'))
        # Set output format to ascii
        self.scope.write(':WAV:FORM ascii')

    def get_time(self,preamb):
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

    def read_ascii_data(self,data):
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
        npdata = np.zeros(N+1)
        ind1 = 0
        ind2 = data.find(',')
        for ii in range(N):
            npdata[ii] = float(data[ind1:ind2])
            ind1 = ind2+1
            ind2 = data[ind1:].find(',')+ind1
        npdata[N] = float(data[ind1:])
        return npdata
    

    def get_trace(self,channel=1,points=None):
        """
        Get a single trace from channel.
        """
        self.scope.write(":WAV:SOUR CHAN" + str(channel))
        if points != None:
            self.scope.write(":WAV:POIN " + str(int(points)))
        # Stop aquisition
        self.scope.write(':STOP')
        # Get data and preamble
        data = self.scope.ask(":WAVeform:DATA?")
        preamb = self.scope.ask(':WAVeform:PREamble?')
        # Continue aquisition
        self.scope.write(':RUN')
        # Convert data
        xdata = self.get_time(preamb)
        ydata = self.read_ascii_data(data)
        return xdata, ydata


    def close(self):
        self.scope.close()
		

if __name__ == '__main__':
    scope = connect()
    xdata, ydata = scope.get_trace(channel=4, points=1000)
    scope.close()
    import pylab as plt
    plt.plot(xdata,ydata)
    plt.show()
