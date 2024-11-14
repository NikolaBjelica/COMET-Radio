import tkinter as tk  # Import the Tkinter library for GUI development
from tkinter import messagebox  # Import messagebox from Tkinter for dialog boxes
import serial  # Import serial library to handle serial communication with Arduino
import time  # Import time library for delays
import subprocess # to run the GNUradio script
import numpy as np
import matplotlib.pyplot as plt 


# Set up the serial connection with the Arduino
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Open serial connection on specified port with a baud rate of 9600

# Initialize the main window
root = tk.Tk()  # Create the main application window
root.title("Welcome to C.O.M.E.T")  # Set the title of the window

root.geometry("400x700")  # Increased window size to accommodate the widgets
root.configure(bg="#001F3F")  # Set background color for the window

# Set up tracking variables
tracking_enabled = False  # Boolean to track if tracking is active
confirmed_to_set = False  # Boolean to track if Arduino is ready to set positions
confirmed_to_end = False  # Boolean to track if Arduino is ready to set end positions
confirmed_to_time = False # Boolean to track if Arduino is ready to set time duration

output_filename = 'output.bin' 

def send_stop_command():    
    ser.write(b'0')
    time.sleep(0.5)
    response = ser.readline().decode('utf-8').strip()
    messagebox.showinfo(response)
    
def send_reset_command (): 
    ser.write(b'1')
    time.sleep(0.5)
    response = ser.readline().decode('utf-8').strip()
    messagebox.showinfo(response)
    
# Callback function to send 'SET' command and wait for confirmation from Arduino
def send_set_command():
    global confirmed_to_set
    ser.write(b'2')                   # Send 'SET' command (enum value 2) to Arduino
    time.sleep(0.5)
    
    # Wait for Arduino's confirmation that it's ready to set positions
    response = ser.readline().decode('utf-8').strip()
    if response == "READY_TO_SET":
        confirmed_to_set = True
        messagebox.showinfo("Confirmation", "Arduino is ready to set positions.")
        
        set_x_entry.config(state='normal')
        set_y_entry.config(state='normal')
        start_tracking_button.config(state='normal')
    else:
        messagebox.showerror("Error", "Arduino failed to confirm readiness.")

def start_data_collection():
    try:
        frequency = int(freq_entry.get())
        sample_rate = int(rate_entry.get())
        
        #Run the GNURadio script with values input
        subprocess.Popen(['python3', 'sdr_collect.py', str(frequency), str(sample_rate), output_filename])
        messagebox.showinfo("Data Collection", "SDR data collection started.") 
    except ValueError:
        messagebox.showerror("Input Error", "Enter valid numbers for freqeuncy and sample rate.")
        
def load_binary_file (filename, start_frame=0, num_frame=10240000):
    with open(filename, 'rb') as f: 
        f.seek(start_frame * 2) 
        signal = np.fromfile(f, dtype=np.int16, count=num_frames) 
    return signal
 
 #output_path will be used to save a copy of the heatmap -- later feature 
def plot_heatmap(file_name, sample_rate, output_path=None):
    signal = load_binary_file(filename)
    plt.figure(figsize=(10,6))
    plt.specgram(signal, NFFT=512, Fs=sample_rate, noverlaps=256, cmap='inferno')
    time = np.arange(len(signal)) / sample_rate
    plt.xlim([0, len(signal) / sample_rate])
    plt.title('Heatmap of FM Signal')
    plt.xlabel('Time (seconds)') 
    plt.ylabel('Frequency')
    plt.colorbar(label='Intensity (dB)')
    
    if output_path:
        plt.savefig(output_path)
    plt.show()

# Function to send initial X and Y angles after 'SET' command
def send_initial_angles(x_angle, y_angle):
    if confirmed_to_set:
        string = f"{x_angle},{y_angle}\n"
        ser.write(string.encode()) #Send initial X and Y in comma-seperated format 
        time.sleep(0.5)
        response = ser.readline().decode('utf-8').strip()
        print(response)

    else:
        messagebox.showerror("Error", "Please press 'Initialize System' first.")

# Function to gather initial position inputs and send them
def set_initial_positions():
    if not confirmed_to_set:
        messagebox.showerror("Error", "Please press 'Initialize System' first.")
        return
    
    try:
        # Read values from input fields
        x_angle = float(set_x_entry.get())
        y_angle = float(set_y_entry.get())
        
        # Send initial angles
        send_initial_angles(x_angle, y_angle)
        
        # Show success message
        messagebox.showinfo("Success", f"Positions set to Initial (X: {x_angle}, Y: {y_angle})")
                            
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for angles and time.")


# Function to send 'END' command and enable end position fields
def send_end_command():
    global confirmed_to_end
    ser.write(b'4')  # Send 'END' command (enum value 4)
    time.sleep(0.5)
    response = ser.readline().decode('utf-8').strip()  # Wait for confirmation from Arduino
    if response == "READY_TO_END":
        confirmed_to_end = True
        messagebox.showinfo("Confirmation", "Arduino is ready to set end positions.")
        end_x_entry.config(state='normal')
        end_y_entry.config(state='normal')
    else:
        messagebox.showerror("Error", "Arduino failed to confirm readiness for end positions.")

# Function to send end angles in comma-separated format
def send_end_angles(finalAzimuth, finalElevation):
    if confirmed_to_end:
        string = f"{finalAzimuth},{finalElevation}\n"
        ser.write(string.encode())  # Send end angles in comma-separated format
        time.sleep(0.5)
        response = ser.readline().decode('utf-8').strip()
        print(response)
    else:
        messagebox.showerror("Error", "Arduino not ready to receive end angles.")

# Function to send only the end angles
def set_end_positions():
    try:
        # Read values from input fields
        x_end = float(end_x_entry.get())
        y_end = float(end_y_entry.get())
        
        # Set end angles
        send_end_angles(x_end, y_end)
        
        messagebox.showinfo("Success", f"End positions set to (X: {x_end}, Y: {y_end})")
        
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for end angles.")

# Function to send 'TIME' command and duration
def send_duration_command():
    global confirmed_to_time
    ser.write(b'5')  # Send 'TIME' command (enum value 5)
    time.sleep(0.5)
    response = ser.readline().decode('utf-8').strip()  # wait for confirmation from Arduino
    if response == "READY_TO_TIME":
        confirmed_to_time = True
        time_entry.config(state='normal')
        messagebox.showinfo("Confirmation", "Arduino is ready to set time duration.")
    else:
        messagebox.showerror("Error", "Arduino failed to confirm readiness for time duration.")
        
def send_time_duration(timeDuration):
    if confirmed_to_time:
        string = f"{timeDuration}\n"
        ser.write(string.encode())  # Send end angles in comma-separated format
        time.sleep(0.5)
        response = ser.readline().decode('utf-8').strip()
        print(response)
    else:
        messagebox.showerror("Error", "Arduino not ready to receive time duration.")
        
# Function to send only the time duration
def set_time_position():
    try:
        # Read time from input field
        duration = float(time_entry.get())
        
        # Set time
        send_time_duration(duration)
        
        messagebox.showinfo("Success", f"Time duration set to {duration} seconds.")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for duration.")

# Function to send 'TRACK' command to Arduino and start tracking
def start_tracking():
    global tracking_enabled  # Access the global tracking flag
    ser.write(b'3')  # Send 'TRACK' command (enum value 3) to Arduino
    tracking_enabled = True  # Set tracking flag to true
    messagebox.showinfo("Tracking", "Tracking started.")  # Show tracking started message

# Set up GUI elements in a frame
frame = tk.Frame(root, bg="#001F3F")  # Create a frame with specified background color
frame.pack(expand=True, fill='both')  # Fill the window with the frame

tk.Label(frame, text="Frequency (Hz):", bg="#001F3F", fg= "white").grid(row=0, column=0,  pady=5, sticky='e') 
freq_entry = tk.Entry(frame)
freq_entry.grid(row=0, column=1, pady=5) 

tk.Label(frame, text="Sample Rate:", bg="#001F3F", fg= "white").grid(row=1, column=0,  pady=5, sticky='e') 
rate_entry = tk.Entry(frame)
rate_entry.grid(row=1, column=1, pady=5) 

# GUI layout with input fields and buttons
tk.Label(frame, text="Set Motor Position:", bg="#001F3F", fg="white").grid(row=2, column=0, columnspan=2, pady=5)

set_positions_button = tk.Button(frame, text="Initialize System", command=send_set_command, bg="#000000", fg="white")
set_positions_button.grid(row=3, column=0, columnspan=2, pady=5)

# Initial X Position input
tk.Label(frame, text="Initial X Angle (Motor 1):", bg="#001F3F", fg="white").grid(row=4, column=0, pady=5, sticky='e')
set_x_entry = tk.Entry(frame, state='disabled')
set_x_entry.grid(row=4, column=1, pady=5)

# Initial Y Position input
tk.Label(frame, text="Initial Y Angle (Motor 2):", bg="#001F3F", fg="white").grid(row=5, column=0, pady=5, sticky='e')
set_y_entry = tk.Entry(frame, state='disabled')
set_y_entry.grid(row=5, column=1, pady=5)

# Button to apply initial angles
apply_button = tk.Button(frame, text="Apply", command=set_initial_positions, bg="#000000", fg="white")
apply_button.grid(row=6, column=0, columnspan=2, pady=5)

# Button to set end position
set_end_button_1 = tk.Button(frame, text="Initialize End Positions", command=send_end_command, bg="#000000", fg="white")
set_end_button_1.grid(row=7, column=0, columnspan=2, pady=5)

# End X Position input
tk.Label(frame, text="End X Angle (Motor 1):", bg="#001F3F", fg="white").grid(row=8, column=0, pady=5, sticky='e')
end_x_entry = tk.Entry(frame, state='disabled')
end_x_entry.grid(row=8, column=1, pady=5)

# End Y Position input
tk.Label(frame, text="End Y Angle (Motor 2):", bg="#001F3F", fg="white").grid(row=9, column=0, pady=5, sticky='e')
end_y_entry = tk.Entry(frame, state='disabled')
end_y_entry.grid(row=9, column=1, pady=5)

# Button to set end position
set_end_button_2 = tk.Button(frame, text="Set End Position", command=set_end_positions, bg="#000000", fg="white")
set_end_button_2.grid(row=10, column=0, columnspan=2, pady=5)

# Button to set time position
set_time_button_2 = tk.Button(frame, text="Initialize Time Duration", command=send_duration_command, bg="#000000", fg="white")
set_time_button_2.grid(row=11, column=0, columnspan=2, pady=5)

# Time Duration input
tk.Label(frame, text="Time Duration (s):", bg="#001F3F", fg="white").grid(row=12, column=0, pady=5, sticky='e')
time_entry = tk.Entry(frame, state='disabled')
time_entry.grid(row=12, column=1, pady=5)

# Button to set time duration
set_time_button = tk.Button(frame, text="Set Time Duration", command=set_time_position, bg="#000000", fg="white")
set_time_button.grid(row=13, column=0, columnspan=2, pady=5)

#Buttons to start data collection 
start_data_collection_button = tk.Button(frame, text="Start Data Collection", command=start_data_collection, bg="#000000", fg="white")
start_data_collection_button.grid(row=14, column=0, columnspan=2, pady=5)
#Button to plot heatmap 
plot_heatmap_button= tk.Button(frame, text="Plot Heatmap", command=lambda: plot_heatmap(output_filename, int(rate_entry.get())), bg="#000000", fg="white")
plot_heatmap_button.grid(row=15, column=0, columnspan=2, pady=5)

# Button to start tracking
start_tracking_button= tk.Button(frame, text="Start Tracking", command=start_tracking, bg="#000000", fg="white", state='disabled')
start_tracking_button.grid(row=16, column=0, columnspan=2, pady=5)

#Button to Stop 
stop_motors_button = tk.Button(frame, text="Stop Motors", command=send_stop_command, bg="#000000", fg="white")
stop_motors_button.grid(row=17, column=0, pady=0)

#Button to Reset 
reset_motors_button = tk.Button(frame, text="Reset Motors", command=send_reset_command, bg="#000000", fg="white") 
reset_motors_button.grid(row=17, column=1) 

# Start the Tkinter main loop
root.mainloop()
