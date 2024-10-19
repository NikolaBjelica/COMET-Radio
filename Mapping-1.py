import numpy as np
import matplotlib as plt 

def load_binary_file(filename, start_frame=0, num_frame=1024):
    
    with open(filename, 'rb') as f:
        f.seek(start_frame * 2)
        signal = np.fromfile(f, dtype=np.int16, count=num_frame)
    return signal

def plot_heatmap(signal, sample_rate):
    plt.figure(figsize=(10,6))

    plt.spacegram(signal, NFFT=512, Fs=sample_rate, roverlap=256, cmap='inferno')
    time = np.arrange(len(signal)) / sample_rate
    plt.xlim([0, len(signal)/sample_rate])
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency')

    plt.colorbar(label = 'Intensity (dB)')

    plt.show()


if __name__ == "__main__":
    filename = "C:\\Users\\Nikola Bjelica\\OneDrive\\Desktop\\output.dat"
    sample_rate = 1024000
    start_frame = 0
    num_frame = 10240

    signal = load_binary_file(filename, start_frame, num_frame)
    plot_heatmap(signal, sample_rate)
