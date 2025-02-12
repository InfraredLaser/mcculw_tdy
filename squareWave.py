'''
    Output a bipolar square waveform onto target device.
'''

from mcculw import ul
from mcculw.device_info import DaqDeviceInfo
import time
try:
    from examples.console.console_examples_util import config_first_detected_device
except ImportError:
    from .examples.console.console_examples_util import config_first_detected_device

# Constants
DAC_CHANNEL = 0  # DAC Channel to output the waveform
V_HIGH = 5.0     # High Voltage (V)
V_LOW = -V_HIGH  # Low Voltage (V)
SAMPLE_RATE = 50.000  # Samples per second (for square wave frequency)
DURATION = 5  # Duration in seconds to output the waveform   

def squareWave():
    use_device_detection = True
    dev_id_list = []
    board_num = 0

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
        channel = 0

        print(f'Outputting {V_HIGH} / {V_LOW}, Volts to channel', channel)
        # Calculate how long the high and low parts of the square wave will last
        half_period = 1 / SAMPLE_RATE  # Half period of the square wave

        start_time = time.time()
        print(f"Half period of the waveform: {half_period} s.")
        while True: #time.time() - start_time < DURATION:
            # Output high voltage (V_HIGH)
            ul.v_out(board_num, DAC_CHANNEL, ao_range, V_HIGH)
            time.sleep(half_period)

            # Output low voltage (V_LOW)
            ul.v_out(board_num, DAC_CHANNEL, ao_range, V_LOW)
            time.sleep(half_period)

        print(f"Square wave output completed for {DURATION} seconds.")
    except Exception as e:
        print('\n', e)
    except KeyboardInterrupt:
        print('Aborted Program via Ctrl+C.')
        ul.v_out(board_num, DAC_CHANNEL, ao_range, 0)
    finally:
        if use_device_detection:
            ul.release_daq_device(board_num)

def main():
    squareWave()

if __name__ == "__main__":
    main()