'''
    File contians utilities when handling DAQ Devices.
'''

from mcculw import ul
from mcculw.enums import InterfaceType
from mcculw.device_info import DaqDeviceInfo
import numpy as np
from typing import Dict, List
from ctypes import POINTER


def configure_devices() -> Dict:
    '''
        Assign DAQ's to device nubers.

        MCCLW Python interface (ul) assigns connected devices to board numbers.
        ex/ USB-3101FS (2128658) - Device ID = 224 -> referenced with board num 0.

        DAQ Devices can then be commanded with board number as reference.

        Return:
            list of device names to keep track of assigned board num as index in list.
    '''
    ul.ignore_instacal()
    devices:List[ul.DaqDeviceDescriptor] = ul.get_daq_device_inventory(InterfaceType.USB)

    if not devices:
        raise Exception("ERROR: No USB DAQ devices connected")

    connected_devices = {}
    print(f"\nConfiguring {len(devices)} USB DAQs. ")
    for board_num, device in enumerate(devices):
        print(f"Board Number: {board_num} | {device.product_name}")
        connected_devices[device.product_name] = board_num
        ul.create_daq_device(board_num, device)
    print()

    return connected_devices

""" Building waveforms for DAQs with analog output. """
def waveform(
        waveform_type:str,
        daq:DaqDeviceInfo,
        buffer:POINTER,
        duration:int,
        num_samples:int,
        amplitude:float,
        frequency:int):
    '''
        Adjust waveform in memory. Currently parameter waveform_type only supports 'sine' and 'square'.
    '''
    if not daq.supports_analog_output:
        raise f"[ERROR] Daq does not support Analog Output: {daq.product_name}"
    
    t = np.linspace(0, duration, num_samples, endpoint=True)
    if waveform_type == "sine":
        wave = amplitude * np.sin(2*np.pi * frequency * t)
    elif waveform_type == "square":
        wave = amplitude * np.sign(np.sin(2*np.pi * frequency * t))
    else:
        raise "[ERROR] Waveform only supports string 'sine' and 'square'. \n"

    for i, sample in enumerate(wave):
        raw_value = ul.from_eng_units(daq.board_num, daq.get_ai_info().supported_ranges[0], sample)
        buffer[i] = raw_value

# configure_devices()