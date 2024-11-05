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
confirmed_to_end = False               # Boolean to track if Arduino is ready to set end positions

def send_stop_command():    
    ser.write(b'0\n')
    time.sleep(0.5)
    response = ser.readline().decode('utf-8').strip()
    messagebox.showinfo(response)
    
# Callback function to send 'SET' command and wait for confirmation from Arduino
def send_set_command():
    global confirmed_to_set
    ser.write(b'2\n')                   # Send 'SET' command (enum value 2) to Arduino
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

# Function to send initial X and Y angles after 'SET' command
def send_initial_angles(x_angle, y_angle):
    if confirmed_to_set:
        ser.write(f"{x_angle},{y_angle}\n".encode()) #Send initial X and Y in comma-seperated format 
        time.sleep(0.5)
        response = ser.readline().decode('utf-8').strip()
        print(response)

    else:
        messagebox.showerror("Error", "Please press 'Initialize System' first.")

# Function to send 'END' command and enable end position fields
def send_end_command():
    global confirmed_to_end
    ser.write(b'4\n')                   # Send 'END' command (enum value 4)
    time.sleep(0.5)
    response = ser.readline().decode('utf-8').strip() # Wait for confirmation from Arduino
    if response == "READY_TO_END":
        confirmed_to_end = True
        end_x_entry.config(state='normal')
        end_y_entry.config(state='normal')
        time_entry.config(state='normal')
        messagebox.showinfo("Confirmation", "Arduino is ready to set end positions.")
    else:
        messagebox.showerror("Error", "Arduino failed to confirm readiness for end positions.")

# Function to send end angles in comma-separated format
def send_end_angles(x_end, y_end):
    if confirmed_to_end:
        angles = f"{x_end},{y_end}\n".encode()
        ser.write(angles)  # Send end angles in comma-separated format
    else: 
        messagebox.showerror("Error", "Arduino not ready to receive end angles.")

# Function to send 'TIME' command and duration
def send_duration(duration):
    ser.write(b'5\n')                   # Send 'TIME' command (enum value 5)
    ser.write(f"{duration}\n".encode()) # Send time duration

# Function to gather initial position inputs and send them
def set_positions():
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

# Function to send only the end angles
def set_end_positions():
    try:
        #Read values from input fields
        x_end = float(end_x_entry.get())
        y_end = float(end_y_entry.get())
        
        #Set end angles
        send_end_angles(x_end, y_end)
        
        messagebox.showinfo("Success", f"End positions set to (X: {x_end}, Y: {y_end})")
        
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for end angles.")

# Function to send only the time duration
def send_time_position():
    try:  
        #Read time from input field 
        duration = float(time_entry.get())
        
        #Set time 
        send_duration(duration)
        
        messagebox.showinfo("Success", f"Time duration set to {duration} seconds.")
    except ValueError:
        messagebox.showerror("Input Error", "Please enter a valid number for duration.")

# Function to send 'TRACK' command to Arduino and start tracking
def start_tracking():
    global tracking_enabled                            # Access the global tracking flag
    ser.write(b'3\n')                                  # Send 'TRACK' command (enum value 3) to Arduino
    tracking_enabled = True                            # Set tracking flag to true
    messagebox.showinfo("Tracking", "Tracking started.")  # Show tracking started message

# Set up GUI elements in a frame
frame = tk.Frame(root, bg="#001F3F")                   # Create a frame with specified background color
frame.pack(expand=True)                                # Center the frame in the window

# GUI layout with input fields and buttons
tk.Label(frame, text="Set Motor Position:", bg="#001F3F", fg="white").grid(row=0, column=0, columnspan=2, pady=5)
set_positions_button = tk.Button(frame, text="Initialize System", command=send_set_command, bg="#000000", fg="white")
set_positions_button.grid(row=1, column=0, columnspan=2, pady=5)

# Initial X Position input
tk.Label(frame, text="Initial X Angle (Motor 1):", bg="#001F3F", fg="white").grid(row=2, column=0, pady=5, sticky='e')
set_x_entry = tk.Entry(frame, state='disabled')
set_x_entry.grid(row=2, column=1, pady=5)

# Initial Y Position input
tk.Label(frame, text="Initial Y Angle (Motor 2):", bg="#001F3F", fg="white").grid(row=3, column=0, pady=5, sticky='e')
set_y_entry = tk.Entry(frame, state='disabled')
set_y_entry.grid(row=3, column=1, pady=5)

# Button to apply initial angles
apply_button = tk.Button(frame, text="Apply", command=set_positions, bg="#000000", fg="white")
apply_button.grid(row=4, column=0, columnspan=2, pady=5)

# End X Position input
tk.Label(frame, text="End X Angle (Motor 1):", bg="#001F3F", fg="white").grid(row=5, column=0, pady=5, sticky='e')
end_x_entry = tk.Entry(frame, state='disabled')
end_x_entry.grid(row=5, column=1, pady=5)

# End Y Position input
tk.Label(frame, text="End Y Angle (Motor 2):", bg="#001F3F", fg="white").grid(row=6, column=0, pady=5, sticky='e')
end_y_entry = tk.Entry(frame, state='disabled')
end_y_entry.grid(row=6, column=1, pady=5)

# Button to set end position
set_end_button = tk.Button(frame, text="Set End Position", command=send_end_angles, bg="#000000", fg="white")
set_end_button.grid(row=7, column=0, columnspan=2, pady=5)

# Time Duration input
tk.Label(frame, text="Time Duration (s):", bg="#001F3F", fg="white").grid(row=8, column=0, pady=5, sticky='e')
time_entry = tk.Entry(frame, state='disabled')
time_entry.grid(row=8, column=1, pady=5)

# Button to set time duration
set_time_button = tk.Button(frame, text="Set Time Duration", command=send_time_position, bg="#000000", fg="white")
set_time_button.grid(row=9, column=0, columnspan=2, pady=5)

# Button to start tracking
start_tracking_button = tk.Button(frame, text="Start Tracking", command=start_tracking, bg="#000000", fg="white", state='disabled')
start_tracking_button.grid(row=10, column=0, columnspan=2, pady=5)

# Start the Tkinter main loop
root.mainloop()
