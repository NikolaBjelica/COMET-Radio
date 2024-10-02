import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time

# Function to plot heatmap
def plot_heatmap(data):
    # Assuming data contains RA, Dec, and Intensity columns
    ra = data['RA'].values
    dec = data['Dec'].values
    intensity = data['Intensity'].values

    # Create a 2D histogram (heatmap) based on RA and Dec
    plt.figure(figsize=(10, 6))
    plt.hist2d(ra, dec, weights=intensity, bins=50, cmap='hot')
    plt.colorbar(label='Signal Intensity')
    plt.xlabel('Right Ascension (RA)')
    plt.ylabel('Declination (Dec)')
    plt.title('Heatmap of Celestial Signals')
    plt.show()

# Main loop to continuously read data
csv_file = 'filtered_signals.csv'  # Path to your output CSV file

while True:
    try:
        # Read the latest data from the CSV file
        data = pd.read_csv(csv_file)

        # Check if data is not empty
        if not data.empty:
            # Plot the heatmap
            plot_heatmap(data)

        # Sleep for a short duration before checking for new data
        time.sleep(5)  # Adjust time as needed

    except Exception as e:
        print(f"Error reading the file: {e}")
        break


#Implementing Real Time Updates & Intensity thresholds for mapping colors

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time

def get_color(intensity):
    if intensity >= 100:
        return 'red'
    elif intensity >= 50:
        return 'orange'
    elif intensity >= 10:
        return 'blue'
    else:
        return 'gray'

# Initialize lists to hold RA, Dec, and colors
ra_list = []
dec_list = []
colors = []

# Create a figure for plotting
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots(figsize=(10, 6))
sc = ax.scatter(ra_list, dec_list, c=colors, s=100)
plt.title('Celestial Objects Heatmap')
plt.xlabel('Right Ascension (RA)')
plt.ylabel('Declination (Dec)')
plt.grid(True)

# Loop to continuously read from the CSV
while True:
    try:
        # Load the data from the CSV file
        data = pd.read_csv('data.csv')
        
        # Clear previous lists
        ra_list.clear()
        dec_list.clear()
        colors.clear()

        # Process the new data
        for index, row in data.iterrows():
            ra = row['RA']
            dec = row['Dec']
            intensity = row['Intensity']

            # Append new values to lists
            ra_list.append(ra)
            dec_list.append(dec)
            color = get_color(intensity)
            colors.append(color)

        # Update scatter plot
        sc.remove()  # Remove old scatter
        sc = ax.scatter(ra_list, dec_list, c=colors, s=100)
        plt.draw()
        plt.pause(0.1)  # Pause for a brief moment to allow the plot to update
        
        time.sleep(1)  # Adjust the sleep time as necessary for your update frequency

    except KeyboardInterrupt:
        print("Exiting...")
        break
