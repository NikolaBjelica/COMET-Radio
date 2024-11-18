import numpy as np
import matplotlib.pyplot as plt 

def load_binary_file(filename, start_frame=0, num_frame=1024):
    with open(filename, 'rb') as f:
        f.seek(start_frame * 2)
        signal = np.fromfile(f, dtype=np.int16, count=num_frame)
    return signal

def plot_heatmap(signal, sample_rate, output_path=None):
    plt.figure(figsize=(10, 6))
    plt.specgram(signal, NFFT=512, Fs=sample_rate, noverlap=256, cmap='inferno')
    time = np.arange(len(signal)) / sample_rate
    plt.xlim([0, len(signal) / sample_rate])
    plt.xlabel('Time (seconds)')
    plt.ylabel('Frequency')
    plt.colorbar(label='Intensity (dB)')

    # Save the plot if an output path is provided
    if output_path:
        plt.savefig(output_path)  # Save the plot to the specified path
        print(f"Plot saved to {output_path}")

    plt.show()

if __name__ == "__main__":
    filename = '/mnt/c/Users/Nikola Bjelica/OneDrive/Desktop/output.bin'
    sample_rate = 1024000
    start_frame = 0
    num_frame = 1024000000

    signal = load_binary_file(filename, start_frame, num_frame)

    # Specify the path where you want to save the plot
    output_path = '/mnt/c/Users/Nikola Bjelica/OneDrive/Desktop/heatmap_plot.png'
    
    plot_heatmap(signal, sample_rate, output_path)
