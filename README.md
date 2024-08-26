# RTL-SDR-Signal-Analyzer
Application for analysis of signal strength on software-defined radio receiver

This is a programmable radio receiver application using RTL-SDR and Tkinter. The application allows you to capture and analyze radio signals, visualize power spectral density, and calculate the signal-to-noise ratio.

## Installation

First, ensure you have Python 3 installed. Then, install the necessary libraries:

```bash
pip install matplotlib numpy pyrtlsdr tkinter

Additionally, for the pyrtlsdr library to work correctly, it is necessary to download the .zip file from the following link: https://ftp.osmocom.org/binaries/windows/rtl-sdr/. The version used during the development of the software solution for this project was "rtl-sdr-64bit-20230430.zip".
Connect the RTL-SDR receiver to your computer. To use the RTL-SDR receiver on a Windows operating system, you need to install the appropriate drivers. Zadig is a free tool for installing USB drivers, which is essential for working with RTL-SDR. To download Zadig, visit the Zadig tool's website: http://zadig.akeo.ie/downloads/. After downloading Zadig, launch it. It is recommended to select the "Options -> List All Devices" option in the Zadig interface. Choose "Bulk-In, Interface (Interface 0)" from the dropdown list. Double-check that the USB ID shows "0BDA 2838 00," as this indicates that the receiver is selected. We need to install the WinUSB driver, so make sure WinUSB is selected in the box to the right of the green arrow. The box to the left of the green arrow is not important and may display (NONE) or (RTL...). The box on the left indicates the currently installed driver, while the box on the right shows the driver that will be installed after you click "Replace/Install Driver."
To verify that these steps were successful, you can open Command Prompt and type "rtl_test." If everything is correct, you should see information about your RTL-SDR device. You can use the software solution from this project or any software compatible with RTL-SDR.


## Usage

Launch the application by double-clicking on the Python script or from the command line using the command python3 sdr.py. When the application opens, you will see an interface with various options. First, enter the center frequency (in MHz) and the sampling rate (in MS/s) in the appropriate fields at the top of the application. The frequency should be between 0.5 and 999 MHz, and the sampling rate between 1 and 3.2 MS/s.

After entering the required parameters, you can click on "Start" to begin receiving and displaying signals in real-time. When you select this option, the RTL-SDR device will start collecting radio spectrum data at the specified frequency and sampling rate. You can stop this process by clicking the "Stop" button. The data will be automatically saved in a file with the .npy extension. The file name will include information about the frequency, sampling rate, and the time the data was collected.

Another option is to load previously saved data by clicking on "Load file." This will open a file selection dialog where you can choose a .npy file that contains previously collected data.

While the data is being collected or loaded, the screen will display a graphical representation of the relative signal strength versus frequency. The application will then analyze the data and display the average signal strength, average noise strength, and the difference in strength between the signal and the noise.



