'''
    Output a bipolar square waveform onto target device.

    NOTE: This script does not properly output a sine wave for the following:
        - The code will gradually iterate though voltage levels created in sin wave
        - The output DAQ voltage adjusts for each point.
        - The DAQ cannot output the voltaes fast enough to maintian a target output freq.
        - SOLUTION: USE ao_scan
'''

from mcculw import ul
from mcculw.device_info import DaqDeviceInfo
import time
import numpy as np
import matplotlib.pyplot as plt

try:
    from examples.console.console_examples_util import config_first_detected_device
except ImportError:
    from .examples.console.console_examples_util import config_first_detected_device

# Constants
DAC_CHANNEL = 0  # DAC Channel to output the waveform
V_HIGH = 5.0     # High Voltage (V)
V_LOW = -V_HIGH  # Low Voltage (V)
SAMPLE_RATE = 10_000  # Samples per second (for square wave frequency)
AMPLITUDE = 5
FREQUENCY = 10
DURATION = 1
NUM_SAMPLES = SAMPLE_RATE * DURATION
OFFSET = 0
def plotWaveform(x:np.ndarray, y:np.ndarray):
    ''' Plot waveform via matplotlib'''
    plt.plot(x, y)

    # Add labels and title
    plt.title('Sine Wave')
    plt.xlabel('time')
    plt.ylabel('sin(x)')

    # Show the plot
    plt.grid(False)
    plt.show()

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
        # Generate sine wave
        time_values = np.linspace(0, DURATION, NUM_SAMPLES, endpoint=True)
        sine_wave = AMPLITUDE * np.sin(2*np.pi*time_values*FREQUENCY)
        plotWaveform(np.arange(0, NUM_SAMPLES), time_values)

        print(f'Outputting {V_HIGH} / {V_LOW}, Volts to channel', DAC_CHANNEL)
        print(f"Number of samples: {NUM_SAMPLES} | Frequency: {FREQUENCY} Hz")
        # Calculate how long the high and low parts of the square wave will last
        start_time = time.time()
        
        while True:#time.time() - start_time < DURATION:
            # Output high voltage (V_HIGH)
            for value in sine_wave:
                # Convert sine wave value to DAC output value
                #dac_value = int(value * 65535 / 5)  # Assuming 16-bit resolution, and 5V max output
                ul.v_out(board_num, DAC_CHANNEL, ao_range, value)
                ul.a_out_scan()
                #time.sleep(1/SAMPLE_RATE)

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