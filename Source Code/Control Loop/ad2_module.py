from ctypes import *
from dwfconstants import *
import sys
import time
import matplotlib.pyplot as plt
import numpy

buffer_size = 512
samples1 = (c_double * buffer_size)()  # Buffer for samples
samples2 = (c_double * buffer_size)()

def ad2_setup():
    if sys.platform.startswith("win"):
        dwf = cdll.dwf
    elif sys.platform.startswith("darwin"):
        dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
    else:
        dwf = cdll.LoadLibrary("libdwf.so")

    version = create_string_buffer(16)
    dwf.FDwfGetVersion(version)
    print("DWF Version: "+str(version.value))

    hdwf = c_int()
    #open device
    print("Opening first device...")
    dwf.FDwfDeviceOpen(c_int(-1), byref(hdwf))

    if hdwf.value == hdwfNone.value:
        szerr = create_string_buffer(512)
        dwf.FDwfGetLastErrorMsg(szerr)
        print(str(szerr.value))
        print("failed to open device")
        quit()

    dwf.FDwfAnalogInBufferSizeSet(hdwf, c_int(buffer_size))    # setting buffer size used by buffer read
    
    # power supplies
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(False)) 
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(1), c_double(5))
    dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))
    
    # wavegen 2
    channel = 1
    dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(channel), AnalogOutNodeCarrier, funcSquare)
    dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(channel), AnalogOutNodeCarrier, c_double(1e3))
    dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(channel), AnalogOutNodeCarrier, c_double(2.5))
    dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, c_int(channel), AnalogOutNodeCarrier, c_double(100))
    dwf.FDwfAnalogOutNodeOffsetSet(hdwf, c_int(channel), AnalogOutNodeCarrier, c_double(2.5))
    dwf.FDwfAnalogOutConfigure(hdwf, c_int(channel), c_int(3))
    
    # # the device will only be configured when FDwf###Configure is called
    dwf.FDwfDeviceAutoConfigureSet(hdwf, c_int(0))  

    print("Preparing to read sample...")
    # Enable scope channels 1 and 2
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(0), c_int(1)) 
    dwf.FDwfAnalogInChannelEnableSet(hdwf, c_int(1), c_int(1)) 
    dwf.FDwfAnalogInFrequencySet(hdwf, c_double(10e6))
    dwf.FDwfAnalogInChannelOffsetSet(hdwf, c_int(-1), c_double(0)) # set offset of enabled channels to 0
    dwf.FDwfAnalogInChannelRangeSet(hdwf, c_int(-1), c_double(10)) # set range of channels
    
    # dwf.FDwfAnalogInConfigure(hdwf, c_int(0), c_int(0)) # single sample mode
    dwf.FDwfAnalogInConfigure(hdwf, c_int(1), c_int(1)) # buffer mode
    
    dwf.FDwfAnalogOutNodeEnableSet(hdwf, c_int(1), AnalogOutNodeCarrier, c_int(1))
    dwf.FDwfAnalogOutConfigure(hdwf, c_int(1), c_int(1))
    
    time.sleep(2)
    
    return dwf, hdwf

def buffer_average(dwf, hdwf):
    dwf.FDwfAnalogInStatus(hdwf, c_int(True), None)  # Get latest data
    dwf.FDwfAnalogInStatusData(hdwf, c_int(0), samples1, buffer_size)  # Read buffer
    v1 = sum(samples1) / len(samples1)
    # v2 = sum(samples2) / len(samples2)
    
    dwf.FDwfAnalogInStatus(hdwf, c_int(True), None)  # Get latest data
    dwf.FDwfAnalogInStatusData(hdwf, c_int(1), samples2, buffer_size)  # Read buffer
    v2 = sum(samples2) / len(samples2)
    
    return v1, v2

def pwm(dwf, hdwf, duty_cycle):
    dwf.FDwfAnalogOutNodeFunctionSet(hdwf, c_int(0), AnalogOutNodeCarrier, funcSquare)
    dwf.FDwfAnalogOutNodeFrequencySet(hdwf, c_int(0), AnalogOutNodeCarrier, c_double(100e3))
    dwf.FDwfAnalogOutNodeAmplitudeSet(hdwf, c_int(0), AnalogOutNodeCarrier, c_double(5))
    dwf.FDwfAnalogOutNodeSymmetrySet(hdwf, c_int(0), AnalogOutNodeCarrier, c_double(duty_cycle))
    dwf.FDwfAnalogOutNodeOffsetSet(hdwf, c_int(0), AnalogOutNodeCarrier, c_double(3))
    dwf.FDwfAnalogOutConfigure(hdwf, c_int(0), c_int(3))
    
def toggle_power(dwf, hdwf, op):
    dwf.FDwfAnalogIOChannelNodeSet(hdwf, c_int(0), c_int(0), c_double(op)) 
    dwf.FDwfAnalogIOEnableSet(hdwf, c_int(True))
    dwf.FDwfAnalogIOConfigure(hdwf)

def ad2_close(dwf, hdwf):
    dwf.FDwfDeviceCloseAll()