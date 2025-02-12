'''
    File contians utilities when handling DAQ Devices.
'''

from mcculw import ul
from mcculw.enums import InterfaceType
import numpy as np
from typing import Dict, List


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
def sineWave(
        board_num:int,
        buffer, 
        ao_range, 
        amplitude, 
        frequency,
        num_samples
        ):
    t = np.linspace(0, 1, num_samples, endpoint=True)
    sine_wave = amplitude * np.sin(2*np.pi * frequency * t)
    for i, point in enumerate(sine_wave):
        raw_value = ul.from_eng_units(board_num, ao_range, point)
        buffer[i] = raw_value

def squareWave(
        board_num:int,
        buffer, 
        ao_range, 
        amplitude, 
        frequency,
        num_samples
        ):
    t = np.linspace(0, 1, num_samples, endpoint=True)
    sine_wave = amplitude * np.sign(np.sin(2*np.pi * frequency * t))
    for i, point in enumerate(sine_wave):
        raw_value = ul.from_eng_units(board_num, ao_range, point)
        buffer[i] = raw_value
# configure_devices()