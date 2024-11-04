import tkinter as tk                  # Import the Tkinter library for GUI development
from tkinter import messagebox         # Import messagebox from Tkinter for dialog boxes
import serial                          # Import serial library to handle serial communication with Arduino
import time                            # Import time library for delays

# Set up the serial connection with the Arduino
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)  # Open serial connection on specified port with a baud rate of 9600

# Initialize the main window
root = tk.Tk()                         # Create the main application window
root.title("Welcome to C.O.M.E.T")     # Set the title of the window

root.geometry("400x400")               # Set window size
root.configure(bg="#001F3F")           # Set background color for the window

# Set up tracking variables
tracking_enabled = False               # Boolean to track if tracking is active
confirmed_to_set = False               # Boolean to track if Arduino is ready to set positions

# Callback function to send 'SET' command and wait for confirmation from Arduino
def send_set_command():
    global confirmed_to_set             # Access the global variable to update its value
    ser.write(b'2\n')                   # Send 'SET' command (represented by enum value 2) to Arduino
    time.sleep(0.5)                     # Wait briefly to allow Arduino to process the command
    
    # Wait for Arduino's confirmation that it's ready to set positions
    response = ser.readline().decode('utf-8').strip()  # Read and decode the response from Arduino
    if response == "READY_TO_SET":                     # Check if the response is as expected
        confirmed_to_set = True                        # Set the flag to true if Arduino is ready
        messagebox.showinfo("Confirmation", "Arduino is ready to set positions.")  # Show confirmation message
        set_x_entry.config(state='normal')             # Enable the entry for initial X position
        set_y_entry.config(state='normal')             # Enable the entry for initial Y position
        end_x_entry.config(state='normal')             # Enable the entry for end X position
        end_y_entry.config(state='normal')             # Enable the entry for end Y position
        time_entry.config(state='normal')              # Enable the entry for time duration
        start_tracking_button.config(state='normal')   # Enable the Start Tracking button
    else:
        messagebox.showerror("Error", "Arduino failed to confirm readiness.")  # Show error if no confirmation

# Function to send position data for initial and end positions of both motors
def set_positions():
    if not confirmed_to_set:                           # Check if Arduino has confirmed readiness
        messagebox.showerror("Error", "Please press 'Initialize System' first.")  # Show error if not ready
        return
    
    try:
        # Read initial and end positions and time duration from the entries
        x_angle = float(set_x_entry.get())             # Get initial X position from user input
        y_angle = float(set_y_entry.get())             # Get initial Y position from user input
        x_end = float(end_x_entry.get())               # Get end X position from user input
        y_end = float(end_y_entry.get())               # Get end Y position from user input
        duration = float(time_entry.get())             # Get time duration from user input
        
        # Send X and Y angles, end positions, and time to Arduino
        ser.write(f"{x_angle}\n".encode())             # Send initial X angle
        ser.write(f"{y_angle}\n".encode())             # Send initial Y angle
        ser.write(f"{x_end}\n".encode())               # Send end X angle
        ser.write(f"{y_end}\n".encode())               # Send end Y angle
        ser.write(f"{duration}\n".encode())            # Send time duration

        # Show success message with values entered
        messagebox.showinfo("Success", f"Positions set to Initial (X: {x_angle}, Y: {y_angle}), "
                                       f"End (X: {x_end}, Y: {y_end}), Time: {duration}s.")
        
    except ValueError:                                 # Handle errors in user input
        messagebox.showerror("Input Error", "Please enter valid numbers for angles and time.")  # Show error message

# Function to send 'TRACK' command to Arduino and start tracking
def start_tracking():
    global tracking_enabled                            # Access the global tracking flag
    ser.write(b'3\n')                                  # Send 'TRACK' command (enum value 3) to Arduino
    tracking_enabled = True                            # Set tracking flag to true
    messagebox.showinfo("Tracking", "Tracking started.")  # Show tracking started message


# Set up GUI elements in a frame
frame = tk.Frame(root, bg="#001F3F")                   # Create a frame with specified background color
frame.pack(expand=True)                                # Center the frame in the window

# Label for motor position setting section
tk.Label(frame, text="Set Motor Position:", bg="#001F3F", fg="white").grid(row=0, column=0, columnspan=2, pady=5)

# Button to initialize the system (send 'SET' command)
set_positions_button = tk.Button(frame, text="Initialize System", command=send_set_command, bg="#000000", fg="white")
set_positions_button.grid(row=1, column=0, columnspan=2, pady=5)

# Initial X Position input (Motor 1)
tk.Label(frame, text="Initial X Angle (Motor 1):", bg="#001F3F", fg="white").grid(row=2, column=0, pady=5, sticky='e')
set_x_entry = tk.Entry(frame, state='disabled')       # Disable until Arduino is ready
set_x_entry.grid(row=2, column=1, pady=5)

# Initial Y Position input (Motor 2)
tk.Label(frame, text="Initial Y Angle (Motor 2):", bg="#001F3F", fg="white").grid(row=3, column=0, pady=5, sticky='e')
set_y_entry = tk.Entry(frame, state='disabled')       # Disable until Arduino is ready
set_y_entry.grid(row=3, column=1, pady=5)

# End X Position input (Motor 1)
tk.Label(frame, text="End X Angle (Motor 1):", bg="#001F3F", fg="white").grid(row=4, column=0, pady=5, sticky='e')
end_x_entry = tk.Entry(frame, state='disabled')       # Disable until Arduino is ready
end_x_entry.grid(row=4, column=1, pady=5)

# End Y Position input (Motor 2)
tk.Label(frame, text="End Y Angle (Motor 2):", bg="#001F3F", fg="white").grid(row=5, column=0, pady=5, sticky='e')
end_y_entry = tk.Entry(frame, state='disabled')       # Disable until Arduino is ready
end_y_entry.grid(row=5, column=1, pady=5)

# Time Duration input
tk.Label(frame, text="Time Duration (s):", bg="#001F3F", fg="white").grid(row=6, column=0, pady=5, sticky='e')
time_entry = tk.Entry(frame, state='disabled')        # Disable until Arduino is ready
time_entry.grid(row=6, column=1, pady=5)

# Button to set positions (send motor positions and duration to Arduino)
apply_button = tk.Button(frame, text="Apply", command=set_positions, bg="#000000", fg="white")
apply_button.grid(row=7, column=0, columnspan=2, pady=5)

# Button to start tracking (send 'TRACK' command to Arduino)
start_tracking_button = tk.Button(frame, text="Start Tracking", command=start_tracking, state='disabled', bg="#000000", fg="white")
start_tracking_button.grid(row=8, column=0, columnspan=2, pady=10)

# Run the GUI event loop
root.mainloop()                                       # Start the Tkinter main loop to run the application
