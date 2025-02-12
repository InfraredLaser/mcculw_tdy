
'''
    Imports to aid in Device Handeling.
'''
from mcculw import ul
from mcculw.device_info import DaqDeviceInfo
from mcculw.enums import ScanOptions, FunctionType, Status, ULRange
from typing import List
import numpy as np
from time import sleep
from ctypes import cast, POINTER, c_ushort
try:
    from tdy_utils.utils_daq import configure_devices, squareWave
except ImportError:
    from .tdy_utils.utils_daq import configure_devices

def main():
    
    devices = configure_devices()
    print(devices)

    usb_202 = DaqDeviceInfo(devices['USB-202'])
    usb_3101fs = DaqDeviceInfo(devices['USB-3101FS'])
    usb_3101fs_ao_info = usb_3101fs.get_ao_info()

    points_per_chan = 10_000
    num_chanels = 1
    memhandle = ul.win_buf_alloc(points_per_chan * num_chanels)
    ao_buffer = cast(memhandle, POINTER(c_ushort))
    print(f"supported ranges: {usb_3101fs_ao_info.supported_ranges}")
    squareWave(board_num=devices['USB-3101FS'], 
               buffer=ao_buffer, 
               ao_range=usb_3101fs_ao_info.supported_ranges[0],
               amplitude=1,
               frequency=1000,
               num_samples=points_per_chan)
    
    # Start the scan
    scan_options = (ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS)

    try:
        ul.a_out_scan(board_num=devices['USB-3101FS'], 
                        low_chan=0, 
                        high_chan=0, 
                        num_points= points_per_chan * num_chanels, 
                        rate=100,#ULRange.NOTUSED, 
                        ul_range=usb_3101fs_ao_info.supported_ranges[0], 
                        memhandle=memhandle, 
                        options=scan_options
                    )
        status = Status.RUNNING
        while status != Status.IDLE:
            print('.', end='')

            # Slow down the status check so as not to flood the CPU
            sleep(0.5)

            status, _, _ = ul.get_status(devices['USB-3101FS'], FunctionType.AOFUNCTION)

        print('')

        print('Scan completed successfully')
    except KeyboardInterrupt:
        ul.v_out(devices['USB-3101FS'], 0, usb_3101fs_ao_info.supported_ranges[0], 0)
    finally:
        if memhandle:
            ul.win_buf_free(memhandle)
        
        print("Releasing DAQ Devices")
        for board_num, device in enumerate(devices):
            ul.release_daq_device(board_num)

if __name__ == "__main__":
    main()
