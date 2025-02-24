"""
File:                       a_out_scan.py

Library Call Demonstrated:  mcculw.ul.a_out_scan()

Purpose:                    Writes to a range of D/A Output Channels.

Demonstration:              Sends a digital output to the D/A channels

Other Library Calls:        mcculw.ul.win_buf_alloc()
                            mcculw.ul.win_buf_free()
                            mcculw.ul.get_status()
                            mcculw.ul.release_daq_device()

Special Requirements:       Device must have D/A converter(s).
                            This function is designed for boards that
                            support timed analog output.  It can be used
                            for polled output boards but only for values
                            of NumPoints up to the number of channels
                            that the board supports (i.e., NumPoints =
                            6 maximum for the six channel CIO-DDA06).
"""
from __future__ import absolute_import, division, print_function
from builtins import *  # @UnusedWildImport

from ctypes import cast, POINTER, c_ushort
from math import pi, sin
from time import sleep
import numpy as np

from mcculw import ul
from mcculw.enums import ScanOptions, FunctionType, Status, ULRange
from mcculw.device_info import DaqDeviceInfo

try:
    from examples.console.console_examples_util import config_first_detected_device
except ImportError:
    from .examples.console.console_examples_util import config_first_detected_device


def run_example():
    # By default, the example detects and displays all available devices and
    # selects the first device listed. Use the dev_id_list variable to filter
    # detected devices by device ID (see UL documentation for device IDs).
    # If use_device_detection is set to False, the board_num variable needs to
    # match the desired board number configured with Instacal.
    use_device_detection = True
    dev_id_list = []
    board_num = 0
    memhandle = None

    try:
        if use_device_detection:
            config_first_detected_device(board_num, dev_id_list)

        daq_dev_info = DaqDeviceInfo(board_num)
        if not daq_dev_info.supports_analog_output:
            raise Exception('Error: The DAQ device does not support '
                            'analog output')

        print('\nActive DAQ device: ', daq_dev_info.product_name, ' (',
              daq_dev_info.unique_id, ')\n', sep='')

        ao_info = daq_dev_info.get_ao_info()
        ao_range = ao_info.supported_ranges[0]

        LOW_CHAN = 0
        HIG_CHAN = 0 #min(3, ao_info.num_chans - 1)
        NUM_CHAN = HIG_CHAN - LOW_CHAN + 1

        AMPL = 1.0 # Voltage output is ratio of total analog output voltage
        print(f"Voltage: {AMPL} V")
        FREQ = 5_000 #Sample rate 100,000 -> FREQ = 10,000 gives 1 kHz somehow...
        SAMPLE_RATE = 100_000
        DURATION = 1
        NUM_SAMPLES = SAMPLE_RATE * DURATION

        # Allocate a buffer for the scan
        memhandle = ul.win_buf_alloc(NUM_SAMPLES)
        # Convert the memhandle to a ctypes array
        # Note: the ctypes array will no longer be valid after win_buf_free
        # is called.
        # A copy of the buffer can be created using win_buf_to_array
        # before the memory is freed. The copy can be used at any time.
        ctypes_array = cast(memhandle, POINTER(c_ushort))

        # Check if the buffer was successfully allocated
        if not memhandle:
            raise Exception('Error: Failed to allocate memory')

        # Start the scan
        scan_options = (ScanOptions.BACKGROUND | ScanOptions.CONTINUOUS)
        squareWave(board_num, ctypes_array, ao_range, amplitude=AMPL, duration=DURATION, frequency=FREQ, num_samples=NUM_SAMPLES)
        ul.a_out_scan(board_num, LOW_CHAN, HIG_CHAN, NUM_SAMPLES, FREQ, ao_range, memhandle, scan_options)
        

        # Wait for the scan to complete
        print('Waiting for output scan to complete...', end='')
        status = Status.RUNNING

        bv_curve_example = np.arange(0, 2.65, 0.05, dtype=float)
        SLEEP_STEP = 1 # sec
        print(f"\nStart: {bv_curve_example[0]:.2f} V | Stop: {bv_curve_example[-1]:.2f} V")
        while status != Status.IDLE:
            # print('.', end='')
            # sleep(1)
            # squareWave(board_num, ctypes_array, ao_range, amplitude=0.05, duration=DURATION, frequency=FREQ, num_samples=NUM_SAMPLES)
            # # Slow down the status check so as not to flood the CPU
            # sleep(5)
            # squareWave(board_num, ctypes_array, ao_range, amplitude=0.5, duration=DURATION, frequency=FREQ, num_samples=NUM_SAMPLES)

            for v_amplitude in bv_curve_example:
                print(f"Voltage: {v_amplitude:.4} V")
                squareWave(board_num, ctypes_array, ao_range, amplitude=float(v_amplitude), duration=DURATION, frequency=FREQ, num_samples=NUM_SAMPLES)
                sleep(SLEEP_STEP)

            status, _, _ = ul.get_status(board_num, FunctionType.AOFUNCTION)
            squareWave(board_num, ctypes_array, ao_range, amplitude=0., duration=DURATION, frequency=FREQ, num_samples=NUM_SAMPLES)
            sleep(SLEEP_STEP)
            break

        print('')

        print('Scan completed successfully')
    except Exception as e:
        print('\n', e)
    finally:
        if memhandle:
            # Free the buffer in a finally block to prevent a memory leak.
            squareWave(board_num, ctypes_array, ao_range, amplitude=0, duration=DURATION, frequency=FREQ, num_samples=NUM_SAMPLES)
            sleep(0.1)
            ul.win_buf_free(memhandle)
        if use_device_detection:
            ul.release_daq_device(board_num)

def sineWave(
        board_num,
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
        board_num,
        buffer, 
        ao_range, 
        amplitude, 
        frequency,
        duration,
        num_samples
        ):
    t = np.linspace(0, duration, int(duration*num_samples), endpoint=True)
    sine_wave = amplitude * np.sign(np.sin(2*np.pi * frequency * t))
    for i, point in enumerate(sine_wave):
        raw_value = ul.from_eng_units(board_num, ao_range, point)
        buffer[i] = raw_value

def add_example_data(board_num, data_array, ao_range, num_chans, rate,
                     points_per_channel):
    # Calculate frequencies that will work well with the size of the array
    frequencies = []
    for channel_num in range(num_chans):
        frequencies.append(
            (channel_num + 1) / (points_per_channel / rate) * 10)

    # Calculate an amplitude and y-offset for the signal
    # to fill the analog output range
    amplitude = (ao_range.range_max - ao_range.range_min) / 2
    y_offset = (amplitude + ao_range.range_min) / 2

    # Fill the array with sine wave data at the calculated frequencies.
    # Note that since we are using the SCALEDATA option, the values
    # added to data_array are the actual voltage values that the device
    # will output
    data_index = 0
    for point_num in range(points_per_channel):
        for channel_num in range(num_chans):
            freq = frequencies[channel_num]
            value = amplitude * sin(2 * pi * freq * point_num / rate) + y_offset
            raw_value = ul.from_eng_units(board_num, ao_range, value)
            data_array[data_index] = raw_value
            data_index += 1

    return frequencies


if __name__ == '__main__':
    run_example()
