# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 19:30:30 2017

@author: qmpl/Fock
"""

###############################################################################
# Import python repository from QMPL

import os
import sys
if os.name == 'nt':  # This should correspond to windows
    pyrep = r'\\quarpi\other\membrane\Programs\Python'
    prefix = '\\\\'
else:
    if sys.platform == 'linux2':
        pyrep = '/quarpi/other/membrane/Programs/Python'  # for Linux
        prefix = '/'
    else:
        pyrep = '/Volumes/other/membrane/Programs/Python'  # for Mac
        prefix = '/'
if not(pyrep in sys.path):
    sys.path.append(pyrep)
    
###############################################################################
# Package imports  

import numpy as np
import wx
import matplotlib as mpl
import matplotlib.pyplot as plt

###############################################################################

# Open file dialog
app = wx.App()
frame = wx.Frame(None, -1, 'win.py')
fexts = "CSV files (*.csv)|*.csv|" \
         "All files (*.*)|*.*"
dlg = wx.FileDialog(frame, "Open", "", "", 
                wildcard = fexts,
                style = wx.FD_OPEN | wx.FD_MULTIPLE | wx.FD_FILE_MUST_EXIST)
dlg.ShowModal()
fpaths = dlg.GetPaths()
dlg.Destroy()

if fpaths == []:
    sys.exit()

# Loop through files
for ii in xrange(len(fpaths)):    
    # Load file
    data = np.genfromtxt(fpaths[ii], delimiter=',')
    t = data[:,0]
    t = t-np.nanmin(t)
    
    # Plot
    fig = plt.figure(ii)
    fname = os.path.splitext(os.path.basename(str(fpaths[ii])))[0]
    fig.canvas.set_window_title(fname)
    plt.plot(t,data[:,1:],lw=1)
    plt.xlabel('Time (s)')
    plt.ylabel('Voltage (V)')
    plt.title(fname)
    plt.ticklabel_format(axis='both', style='sci', scilimits=(-2,2))
    mpl.rcParams["savefig.directory"] = os.path.dirname(fpaths[ii])

plt.show()
