import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

if __name__ == "__main__":
    f=10
    a=2
    dur=1
    sample_rate = 100
    samples = np.linspace(0, dur, int(sample_rate * dur))
    square_wave = a * np.sign(np.sin(2*np.pi*f*samples))
    
    FILE_NUM = 6
    n = 200
    data = pd.read_csv(f'scan_data_{FILE_NUM}.csv')
    data_avg = data['Channel 0'].rolling(window=n).mean().dropna()

    plt.figure(figsize=(10, 4))
    plt.plot(data_avg, marker='o')
    plt.title('BV Curve')
    plt.xlabel(f'Index Every {n} steps')
    plt.ylabel('Intensity')
    plt.grid(True)
    plt.show()
    plt.xticks()