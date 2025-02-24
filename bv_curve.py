
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
    from tdy_utils.utils_daq import configure_devices, waveform
except ImportError:
    from .tdy_utils.utils_daq import configure_devices

def main():
    
    devices = configure_devices()
    print(devices)

    # usb_202 = DaqDeviceInfo(devices['USB-202'])
    usb_3101fs = DaqDeviceInfo(devices['USB-3101FS'])
    usb_3101fs_ao_info = usb_3101fs.get_ao_info()
    usb_3101fs_range = usb_3101fs_ao_info.supported_ranges[0]

    
    ### Device 3101fs parameters ###
    LOW_CHAN = 0
    HIG_CHAN = 0 #min(3, ao_info.num_chans - 1)
    NUM_CHAN = HIG_CHAN - LOW_CHAN + 1

    AMPL = 1.0 # Voltage output is ratio of total analog output voltage
    print(f"Voltage: {AMPL} V")
    FREQ = 5_000 #Sample rate 100,000 -> FREQ = 10,000 gives 1 kHz somehow...
    SAMPLE_RATE = 100_000
    DURATION = 1
    NUM_SAMPLES = SAMPLE_RATE * DURATION
    #################################

    memhandle = ul.win_buf_alloc(NUM_SAMPLES)
    ao_buffer = cast(memhandle, POINTER(c_ushort))
    
    waveform(board_num=devices['USB-3101FS'], 
               buffer=ao_buffer, 
               ao_range=usb_3101fs_range,
               amplitude=0.,
               duration=DURATION,
               frequency=FREQ,
               num_samples=NUM_SAMPLES)
    
    # Start the scan
    scan_options = (ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS)

    try:
        ul.a_out_scan(board_num=devices['USB-3101FS'], 
                        low_chan=LOW_CHAN, 
                        high_chan=HIG_CHAN, 
                        num_points= NUM_SAMPLES, 
                        rate=FREQ,#ULRange.NOTUSED, 
                        ul_range=usb_3101fs_range, 
                        memhandle=memhandle, 
                        options=scan_options
                    )
        
        bv_curve_voltage_steps = np.arange(0, 2.65, 0.025, dtype=float)
        SLEEP_STEP = 1 # sec
        print(f"\nStart: {bv_curve_voltage_steps[0]:.2f} V | Stop: {bv_curve_voltage_steps[-1]:.2f} V")

        status = Status.RUNNING
        while status != Status.IDLE:
            for v_amplitude in bv_curve_voltage_steps:
                print(f"Voltage: {v_amplitude:.4} V")
                waveform(
                    board_num=devices['USB-3101FS'], 
                    buffer=ao_buffer, 
                    ao_range=usb_3101fs_range,
                    amplitude=v_amplitude,
                    duration=DURATION,
                    frequency=FREQ,
                    num_samples=NUM_SAMPLES
                )
                sleep(SLEEP_STEP)

            status, _, _ = ul.get_status(devices['USB-3101FS'], FunctionType.AOFUNCTION)
            waveform(devices['USB-3101FS'], ao_buffer, usb_3101fs_range, amplitude=0., duration=DURATION, frequency=FREQ, num_samples=NUM_SAMPLES)
            sleep(SLEEP_STEP)
            status = Status.IDLE

        print('')

        print('Scan completed successfully')
    except KeyboardInterrupt:
        waveform(devices['USB-3101FS'], ao_buffer, usb_3101fs_range, amplitude=0, duration=DURATION, frequency=FREQ, num_samples=NUM_SAMPLES)
    finally:
        if memhandle:
            waveform(devices['USB-3101FS'], ao_buffer, usb_3101fs_range, amplitude=0, duration=DURATION, frequency=FREQ, num_samples=NUM_SAMPLES)
            sleep(0.1)
            ul.win_buf_free(memhandle)
        
        print("Releasing DAQ Devices")
        for board_num, device in enumerate(devices):
            ul.release_daq_device(board_num)

if __name__ == "__main__":
    main()
