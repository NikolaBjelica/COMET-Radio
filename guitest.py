import tkinter as tk
from tkinter import messagebox
import serial
import time

# Set up the serial connection with the Arduino
ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1) 

# Initialize the main window
root = tk.Tk()
root.title("Welcome to C.O.M.E.T")

root.geometry("300x300")  

root.configure(bg="#001F3F") 
 
# Set up tracking variables
tracking_enabled = False
confirmed_to_set = False  # Track whether Arduino has confirmed "SET" readiness

# Callback to send 'SET' command and wait for confirmation
def send_set_command():
    global confirmed_to_set
    ser.write(b'2\n')  # Send 'SET' command (enum value is 2)
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

# Send position data for both motors
def set_positions():
    if not confirmed_to_set:
        messagebox.showerror("Error", "Please press 'Set Positions' first.")
        return
    
    try:
        x_angle = float(set_x_entry.get())
        y_angle = float(set_y_entry.get())
        
        # Send X and Y angles to Arduino
        ser.write(f"{x_angle}\n".encode())
        #time.sleep(0.2)
        ser.write(f"{y_angle}\n".encode())
        messagebox.showinfo("Success", f"Positions set to X: {x_angle}, Y: {y_angle}.")
        
    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid numbers for angles.")

# Send the 'TRACK' command to start tracking to the motor control system in Arduino
def start_tracking():
    global tracking_enabled
    ser.write(b'3\n')  # Send 'TRACK' command (enum value is 3 in Arduino code)
    tracking_enabled = True
    messagebox.showinfo("Tracking", "Tracking started.")


frame= tk.Frame(root, bg="#001F3F")
frame.pack(expand=True) #Centers everything 


tk.Label(frame, text="Set Motor Position:", bg="#001F3F", fg="white").grid(row=0, column=0, columnspan=2, pady=5)

# Set Positions button
set_positions_button = tk.Button(frame, text="Initialize System", command=send_set_command, bg="#000000", fg="white")
set_positions_button.grid(row=1, column=0, columnspan=2, pady=5)

# X Position input Motor 1 
tk.Label(frame, text="X Angle (Motor 1):", bg="#001F3F", fg="white").grid(row=2, column=0, pady=5, sticky='e')
set_x_entry = tk.Entry(frame, state='disabled')
set_x_entry.grid(row=2, column=1, pady=5)

# Y Position input Motor 2 
tk.Label(frame, text="Y Angle (Motor 2):", bg="#001F3F", fg="white").grid(row=3, column=0, pady=5, sticky='e')
set_y_entry = tk.Entry(frame, state='disabled')
set_y_entry.grid(row=3, column=1, pady=5)

# Button to set the angles to the position that the user has requested
apply_button = tk.Button(frame, text="Apply", command=set_positions, bg="#000000", fg="white")
apply_button.grid(row=4, column=0, columnspan=2, pady=5)

# Start Tracking button
start_tracking_button = tk.Button(frame, text="Start Tracking", command=start_tracking, state='disabled', bg="#000000", fg="white")
start_tracking_button.grid(row=5, column=0, columnspan=2, pady=10)

# Run the GUI event loop
root.mainloop()
