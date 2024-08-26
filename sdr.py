import tkinter as tk
from rtlsdr import RtlSdr
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import datetime
from tkinter import filedialog
import os

def start_acquisition():
    global sdr, acquisition_flag, acquisition_thread, signal_samples
    freq = freq_entry.get().replace(",",".")
    rate = rate_entry.get().replace(",",".")
    try:
        freq = float(freq)
        rate = float(rate)
        if not (0.5 <= freq <= 999):
            raise ValueError("Please enter a frequency between 0.5 and 999.")
        if not (1 <= rate <= 3.2):
            raise ValueError("Please enter a sample rate between 1 and 3.2.")
    except Exception as e:
        tk.messagebox.showerror("Invalid input", str(e))
        return

    signal_samples = []
    start_button.config(state=tk.DISABLED)
    load_button.config(state=tk.DISABLED)
    data_label.config(text="")
    SNR_label.config(text="")
    try:
        sdr = RtlSdr()
        sdr.sample_rate = rate * 1e6       # širina prikaza
        sdr.center_freq = freq * 1e6     # centar prikaza
        sdr.freq_correction = 60
        sdr.gain = 10
    except Exception as e:
        print("Error occurred while initializing RTL-SDR device:", str(e))
        start_button.config(state=tk.NORMAL)
        load_button.config(state=tk.NORMAL)
        return
    
    acquisition_flag.set()
    acquisition_thread = threading.Thread(target=acquire_samples)
    acquisition_thread.start()

    update_thread = threading.Thread(target=update_plot)
    update_thread.start()

    stop_button.config(state=tk.NORMAL)
    status_label.config(text="Acquiring samples...")

def stop_acquisition():
    global sdr, signal_samples, acquisition_flag, acquisition_thread
    stop_button.config(state=tk.DISABLED)
    acquisition_flag.clear()
    acquisition_thread.join() # čeka da se završi acquisition_thread

    if sdr is not None:
        try:
            sdr.close()
        except Exception as e:
            print("Error occurred while closing RTL-SDR device:", str(e))

    save_samples(signal_samples)

    analyze_samples(sdr.center_freq, sdr.sample_rate, signal_samples)

    start_button.config(state=tk.NORMAL)
    load_button.config(state=tk.NORMAL)

def load_file():
    global signal_samples, center_freq, sample_rate
    start_button.config(state=tk.DISABLED)
    ax.clear()
    fig.canvas.draw()

    status_label.config(text="Load .npy file with signal samples.")
    data_label.config(text="")
    SNR_label.config(text="")

    filename = filedialog.askopenfilename(filetypes=(("Numpy files", "*.npy"), ("All files", "*.*")))

    if filename:
        signal_samples = np.load(filename)
        basename = os.path.basename(filename)
        center_freq = float(basename.split("_")[2]) * 1e6
        sample_rate = float(basename.split("_")[4]) * 1e6
        status_label.config(text=f"Loading file {basename}")
        print(f"Loading file {basename}")
        update_plot()
        plot_done.wait()
        analyze_samples(center_freq, sample_rate, signal_samples)
        start_button.config(state=tk.NORMAL)
        status_label.config(text=f"File {basename} loaded successfully.")
        
    else:
        start_button.config(state=tk.NORMAL)
        status_label.config(text="Enter center frequency, sample rate and press start or load .npy file with signal samples.")

def acquire_samples():
    global sdr, signal_samples
    while acquisition_flag.is_set():
        samples = sdr.read_samples(256 * 1024)
        signal_samples.extend(samples)

def update_plot():
    global sdr, acquisition_flag, signal_samples, center_freq, sample_rate
    if(acquisition_flag.is_set()):
        while acquisition_flag.is_set():
            samples = signal_samples[-256*1024:]

            ax.clear()  
            if len(samples) > 0:
                ax.psd(samples, NFFT=1024, Fs=sdr.sample_rate/1e6, Fc=sdr.center_freq/1e6)
                ax.set_xlabel('Frequency (MHz)')
                ax.set_ylabel('Relative power (dB)')
            fig.canvas.draw()
            time.sleep(0.05)
    else:
        parts = len(signal_samples) / (256*1024)
        i=0
        while(i<parts):
            if(i!=parts-1):
                samples = signal_samples[i*256*1024:(i+1)*256*1024]
            else:
                samples = signal_samples[-256*1024:]
            ax.clear()  
            if len(samples) > 0:
                ax.psd(samples, NFFT=1024, Fs=sample_rate/1e6, Fc=center_freq/1e6)
                ax.set_xlabel('Frequency (MHz)')
                ax.set_ylabel('Relative power (dB)')
            fig.canvas.draw()
            i+=1
            root.update_idletasks()           
            time.sleep(0.05)
        plot_done.set()

def save_samples(signal_samples):
    global sdr
    freq = sdr.center_freq / 1e6
    rate = round(sdr.sample_rate / 1e6, 2) 
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"signal_samples_{freq}_MHz_{rate}_{timestamp}.npy"
    try:
        np.save(filename, signal_samples)    
        print("Signal samples saved successfully.")
        status_label.config(text="Signal samples saved successfully.")
    except Exception as e:
        print("Error occurred while saving signal samples:", str(e))
        status_label.config(text="Error occurred while saving signal samples.")

def analyze_samples(signal_freq, sample_rate, signal_samples):
    power = perform_fft(signal_samples)

    noise_band = 50e3
    signal_band = 150e3

    power_db = 10 * np.log10(power)

    signal_start_freq = signal_freq - 10e3
    signal_end_freq = signal_freq + 10e3
    signal_start_index = int(((signal_start_freq - signal_freq) / sample_rate + 0.5) * len(power_db))
    signal_end_index = int(((signal_end_freq - signal_freq) / sample_rate + 0.5) * len(power_db))
    signal_power = np.mean(power_db[signal_start_index:signal_end_index])

    noise_start_freq_1 = signal_freq - signal_band - noise_band
    noise_end_freq_1 = signal_freq - signal_band
    noise_start_freq_2 = signal_freq + signal_band
    noise_end_freq_2 = signal_freq + signal_band + noise_band

    noise_start_index_1 = int(((noise_start_freq_1 - signal_freq) / sample_rate + 0.5) * len(power_db))
    noise_end_index_1 = int(((noise_end_freq_1 - signal_freq) / sample_rate + 0.5) * len(power_db))
    noise_start_index_2 = int(((noise_start_freq_2 - signal_freq) / sample_rate + 0.5) * len(power_db))
    noise_end_index_2 = int(((noise_end_freq_2 - signal_freq) / sample_rate + 0.5) * len(power_db))

    noise_power_1 = np.mean(power_db[noise_start_index_1:noise_end_index_1])
    noise_power_2 = np.mean(power_db[noise_start_index_2:noise_end_index_2])
    noise_power = (noise_power_1 + noise_power_2) / 2

    SNR = signal_power - noise_power

    data_label.config(text="Signal Power: {:.5f} dB  Noise Power: {:.5f} dB".format(signal_power, noise_power))
    SNR_label.config(text="Signal-to-noise ratio: {:.5f} dB".format(SNR))

    print("Signal Power: {:.5f} dB  Noise Power: {:.5f} dB".format(signal_power, noise_power))
    print("Signal-to-noise ratio: {:.5f} dB".format(SNR))

def perform_fft(samples):
    fft_results = np.fft.fftshift(np.fft.fft(samples))
    power = np.abs(fft_results)**2 / len(fft_results)
    return power

sdr = None
center_freq = 0
sample_rate = 0
root = tk.Tk()
root.geometry("670x750")
root.title("Programmable Radio Receiver")

font_label = ("Calibri", 12)
font_button = ("Calibri", 12, "bold")

title_label = tk.Label(root, text="Programmable Radio Receiver", font=("Arial", 16, "bold"))
title_label.grid(row=0, column=0, padx=10, pady=10, columnspan=4)

freq_label = tk.Label(root, text="Frequency center (MHz):", font=font_label)
freq_label.grid(row=1, column=0, pady=2, sticky="e")

freq_entry = tk.Entry(root, font=font_label)
freq_entry.grid(row=1, column=1, pady=2, sticky="w")

rate_label = tk.Label(root, text="Sample rate (MS/s):", font=font_label)
rate_label.grid(row=2, column=0, pady=2, sticky="e")

rate_entry = tk.Entry(root, font=font_label)
rate_entry.grid(row=2, column=1, pady=2, sticky="w")

status_label = tk.Label(root, text="Enter center frequency, sample rate and press start or load .npy file with signal samples", font=font_label)
status_label.grid(row=5, column=0, pady=5, columnspan=4)

fig = plt.Figure()
ax = fig.add_subplot(111)

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(row=4, column=0, padx=10, pady=10, columnspan=4)

signal_samples = []
acquisition_flag = threading.Event()
acquisition_thread = None
plot_done = threading.Event()

load_button = tk.Button(root, text="Load file", command=load_file, font=font_button, padx=1, pady=5)
load_button.grid(row=3, column=3)

start_button = tk.Button(root, text="Start", command=start_acquisition, font=font_button, padx=1, pady=5)
start_button.grid(row=3, column=0)

stop_button = tk.Button(root, text="Stop", command=stop_acquisition, state=tk.DISABLED, font=font_button, padx=1, pady=5)
stop_button.grid(row=3, column=1)

data_label = tk.Label(root, text="", font=font_label, padx=10, pady=3)
data_label.grid(row=6, column=0, columnspan=4)

SNR_label = tk.Label(root, text="", font=font_button, padx=10, pady=3)
SNR_label.grid(row=7, column=0, columnspan=4)

root.mainloop()
