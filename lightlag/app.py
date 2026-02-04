import ephem
import datetime
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import numpy as np

# Constants
AU_to_km = 149597870.7  # AU to kilometers
speed_of_light_km_per_s = 299792  # km/s

# Function to compute distances and delays
def compute_planet_distances(current_time):
    result = []
    positions = []  # Store positions for plotting
    earth = ephem.Earth()
    earth.compute(current_time)
    for planet_name, planet in planets.items():
        planet.compute(current_time)

        # Use Earth-relative distance (AU) for light-travel time
        distance_AU = planet.earth_distance
        distance_km = distance_AU * AU_to_km  # Convert AU to kilometers
        distance_million_km = distance_km / 1_000_000  # Convert km to millions of km

        # Use geocentric ecliptic longitude for plotting Earth-centered positions
        ecl = ephem.Ecliptic(planet)
        longitude_rad = float(ecl.lon)

        # Convert to Cartesian coordinates for plotting (Earth at origin)
        r = distance_AU  # Radial distance (AU)
        x = r * np.cos(longitude_rad)
        y = r * np.sin(longitude_rad)
        
        # Calculate the delay (seconds) based on the distance in kilometers
        delay_seconds = distance_km / speed_of_light_km_per_s
        delay_minutes = delay_seconds / 60  # Convert delay from seconds to minutes
        
        result.append({
            "Planet": planet_name,
            "Distance from Earth (AU)": f"{distance_AU:.5f}",
            "Distance from Earth (Million km)": f"{distance_million_km:.2f}",
            "Light Delay (s)": f"{delay_seconds:.2f}",
            "Light Delay (min)": f"{delay_minutes:.2f}",
            "Position (x, y)": (x, y),  # Store the position of the planet
        })
        positions.append((planet_name, x, y))  # Add position to the plot list
    return result, positions

# Function to handle the date input and display results
def on_calculate_button_click(event=None):
    # Get the date from the input field
    date_str = date_entry.get()
    
    if date_str == "":  # If the input is empty, use the current date
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Parse the date and convert it to ephem date format
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
        current_time = ephem.Date(date_obj)
        
        # Compute the distances and delays
        results, positions = compute_planet_distances(current_time)
        
        # Clear existing rows in the table
        for row in treeview.get_children():
            treeview.delete(row)
        
        # Insert the results into the table
        for result in results:
            treeview.insert("", "end", values=(
                result["Planet"],
                result["Distance from Earth (AU)"],
                result["Distance from Earth (Million km)"],
                result["Light Delay (s)"],
                result["Light Delay (min)"]
            ))
        
        # Store positions for plotting later
        global plot_positions, plot_current_time
        plot_positions = positions
        plot_current_time = current_time  # Store the current time to pass to the plot
        
        # Enable the show plot button after calculations
        show_plot_button.config(state="normal")
    except ValueError:
        print("Invalid date format. Please enter the date in YYYY-MM-DD format.")

# Function to show the plot with the Sun at the center and planets around it in spherical coordinates
def show_planet_plot():
    current_time = plot_current_time  # Get the current time for plotting
    # Create the plot
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    ax.set_xlim(-40, 40)
    ax.set_ylim(-40, 40)

    # Plot Earth at the center (0, 0)
    ax.plot(0, 0, 'bo', label="Earth", markersize=8)

    # Plot the planets around Earth using their geocentric ecliptic longitude
    for name, x, y in plot_positions:
        ax.plot(x, y, 'o', label=name)
        ax.text(x, y, name, fontsize=9, ha='right')
    
    # Add grid to the plot
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Add labels and legend
    ax.set_title("Planet Positions Relative to Earth")
    ax.set_xlabel("AU (x-axis)")
    ax.set_ylabel("AU (y-axis)")
    ax.legend(loc='upper left')

    # Show the plot
    plt.show()

# Initialize the planets dictionary
planets = {
    "Mercury": ephem.Mercury(),
    "Venus": ephem.Venus(),
    "Mars": ephem.Mars(),
    "Jupiter": ephem.Jupiter(),
    "Saturn": ephem.Saturn(),
    "Uranus": ephem.Uranus(),
    "Neptune": ephem.Neptune(),
}

# Create the main window
root = tk.Tk()
root.title("Planet Distance and Delay Calculator")

# Date input field and calculate button
date_label = tk.Label(root, text="Enter Date (YYYY-MM-DD):")
date_label.grid(row=0, column=0, padx=10, pady=10)

date_entry = tk.Entry(root)
date_entry.grid(row=0, column=1, padx=10, pady=10)
date_entry.insert(0, datetime.datetime.now().strftime('%Y-%m-%d'))  # Default to today

calculate_button = tk.Button(root, text="Calculate", command=on_calculate_button_click)
calculate_button.grid(row=0, column=2, padx=10, pady=10)

# Allow pressing Enter to trigger calculation
root.bind("<Return>", on_calculate_button_click)

# Treeview to display results
columns = ("Planet", "Distance from Earth (AU)", "Distance from Earth (Million km)", "Light Delay (s)", "Light Delay (min)")
treeview = ttk.Treeview(root, columns=columns, show="headings")
treeview.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Define column headings
for col in columns:
    treeview.heading(col, text=col)

# Show plot button
show_plot_button = tk.Button(root, text="Show Plot", command=show_planet_plot, state="disabled")
show_plot_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)

# Start the GUI
root.mainloop()
