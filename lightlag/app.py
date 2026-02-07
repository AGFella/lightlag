import ephem
import datetime
import tkinter as tk
from tkinter import ttk
from tkcalendar import Calendar
import matplotlib.pyplot as plt
import numpy as np

# Constants
AU_to_km = 149597870.7  # AU to kilometers
speed_of_light_km_per_s = 299792  # km/s

# Function to compute distances and delays
def compute_planet_distances(current_time):
    result = []
    positions = []  # Store positions for plotting
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

# Function to show the plot with the Sun at the center and planets around it in spherical coordinates
def show_planet_plot():
    current_time = plot_current_time  # Get the current time for plotting
    selected = [name for name, var in planet_vars.items() if var.get()]
    if not selected:
        return
    # Create the plot
    fig, ax = plt.subplots()
    ax.set_aspect('equal')
    # Plot the Sun at the center (0, 0)
    ax.plot(0, 0, 'yo', markersize=8)

    color_map = {
        "Mercury": "#8c8c8c",
        "Venus": "#c9a227",
        "Earth": "#2b7cff",
        "Mars": "#d14b3a",
        "Jupiter": "#c58b5a",
        "Saturn": "#d9c27a",
        "Uranus": "#68c2c8",
        "Neptune": "#3b5bd6",
    }

    orbital_period_days = {
        "Mercury": 87.969,
        "Venus": 224.701,
        "Earth": 365.256,
        "Mars": 686.980,
        "Jupiter": 4332.589,
        "Saturn": 10759.22,
        "Uranus": 30688.5,
        "Neptune": 60182.0,
    }

    def heliocentric_xy_for(body_name, date_obj):
        if body_name == "Earth":
            sun = ephem.Sun()
            sun.compute(date_obj)
            sun_ecl = ephem.Ecliptic(sun)
            r = sun.earth_distance
            lon = float(sun_ecl.lon) + np.pi
            return r * np.cos(lon), r * np.sin(lon), r
        planet = planets[body_name]
        planet.compute(date_obj)
        r = planet.sun_distance
        lon = float(planet.hlon)
        return r * np.cos(lon), r * np.sin(lon), r

    # Current positions
    positions = []
    max_r = 1.0
    for planet_name in selected:
        if planet_name not in planets and planet_name != "Earth":
            continue
        x, y, r = heliocentric_xy_for(planet_name, current_time)
        max_r = max(max_r, r)
        positions.append((planet_name, x, y))

    # Trajectories (one full orbital period for each selected planet)
    samples = 360
    for planet_name in selected:
        if planet_name not in planets and planet_name != "Earth":
            continue
        period_days = orbital_period_days.get(planet_name)
        if period_days is None:
            continue
        xs = []
        ys = []
        for i in range(samples + 1):
            dt = ephem.Date(current_time + (i / samples) * period_days)
            x, y, _ = heliocentric_xy_for(planet_name, dt)
            xs.append(x)
            ys.append(y)
        color = color_map.get(planet_name, "#666666")
        ax.plot(xs, ys, color=color, linewidth=0.8, alpha=0.6)

    # Plot the planets around the Sun
    label_offset = 0.05 * max_r
    for name, x, y in positions:
        color = color_map.get(name, "#666666")
        ax.plot(x, y, 'o', color=color)
        ax.text(x, y - label_offset, name, fontsize=9, ha='center', va='top')

    # Sun label uses the same offset as planets
    ax.text(0, -label_offset, "Sun", fontsize=9, ha='center', va='top')

    # Set bounds based on farthest planet
    padding = 0.15 * max_r
    lim = max_r + padding
    ax.set_xlim(-lim, lim)
    ax.set_ylim(-lim, lim)
    
    # Add grid to the plot
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    
    # Add labels
    ax.set_title("Planet Positions Relative to the Sun")
    ax.set_xlabel("AU (x-axis)")
    ax.set_ylabel("AU (y-axis)")

    # Show the plot
    plt.show()

# Initialize the planets dictionary
planets = {
    "Mercury": ephem.Mercury(),
    "Venus": ephem.Venus(),
    "Moon": ephem.Moon(),
    "Mars": ephem.Mars(),
    "Jupiter": ephem.Jupiter(),
    "Saturn": ephem.Saturn(),
    "Uranus": ephem.Uranus(),
    "Neptune": ephem.Neptune(),
}

# Create the main window
root = tk.Tk()
root.title("Planet Distance and Delay Calculator")

# Date input field
date_label = tk.Label(root, text="Enter Date (YYYY-MM-DD):")
date_label.grid(row=0, column=0, padx=(10, 4), pady=10)

date_var = tk.StringVar()
date_entry = tk.Entry(root, textvariable=date_var)
date_entry.grid(row=0, column=1, padx=(4, 10), pady=10)
date_var.set(datetime.datetime.now().strftime('%Y-%m-%d'))  # Default to today

date_picker = None

def open_date_picker(event=None):
    global date_picker
    if date_picker is not None and date_picker.winfo_exists():
        date_picker.lift()
        date_picker.focus_force()
        return "break"

    date_picker = tk.Toplevel(root)
    date_picker.title("Select Date")
    date_picker.resizable(False, False)
    date_picker.transient(root)
    date_picker.focus_force()

    today = datetime.date.today()
    cal = Calendar(
        date_picker,
        selectmode="day",
        year=today.year,
        month=today.month,
        day=today.day,
        date_pattern="y-mm-dd",
    )
    cal.pack(padx=10, pady=10)

    def set_date():
        global date_picker
        date_entry.delete(0, tk.END)
        date_entry.insert(0, cal.get_date())
        date_entry.configure(insertontime=0)
        root.focus_force()
        if date_picker is not None and date_picker.winfo_exists():
            date_picker.destroy()
        date_picker = None
        update_from_date_field()

    def set_today():
        cal.selection_set(today)
        set_date()

    button_frame = tk.Frame(date_picker)
    button_frame.pack(padx=10, pady=(0, 10), fill="x")

    select_button = tk.Button(button_frame, text="Select", command=set_date)
    select_button.pack(side="left")

    today_button = tk.Button(button_frame, text="Today", command=set_today)
    today_button.pack(side="right")

    # Position the calendar near the entry field
    root.update_idletasks()
    x = date_entry.winfo_rootx()
    y = date_entry.winfo_rooty() + date_entry.winfo_height() + 4
    date_picker.geometry(f"+{x}+{y}")

    def on_close():
        global date_picker
        if date_picker is not None and date_picker.winfo_exists():
            date_picker.destroy()
        date_picker = None
        root.focus_force()

    date_picker.protocol("WM_DELETE_WINDOW", on_close)

date_entry.bind("<Button-1>", open_date_picker)

def force_focus(event=None):
    root.focus_force()

root.bind_all("<Button-1>", force_focus, add="+")

def update_from_date_field(event=None):
    date_str = date_entry.get().strip()
    if len(date_str) != 10:
        return
    try:
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return

    current_time = ephem.Date(date_obj)
    results, positions = compute_planet_distances(current_time)

    for row in treeview.get_children():
        treeview.delete(row)

    for result in results:
        treeview.insert("", "end", values=(
            result["Planet"],
            result["Distance from Earth (AU)"],
            result["Distance from Earth (Million km)"],
            result["Light Delay (s)"],
            result["Light Delay (min)"]
        ))

    global plot_positions, plot_current_time
    plot_positions = positions
    plot_current_time = current_time

    show_plot_button.config(state="normal")

# Treeview to display results
columns = ("Planet", "Distance from Earth (AU)", "Distance from Earth (Million km)", "Light Delay (s)", "Light Delay (min)")
treeview = ttk.Treeview(root, columns=columns, show="headings")
treeview.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# Define column headings
for col in columns:
    treeview.heading(col, text=col)

# Show plot button
show_plot_button = tk.Button(root, text="Show Plot", command=show_planet_plot, state="disabled")
show_plot_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

def on_date_var_change(*_):
    update_from_date_field()

date_var.trace_add("write", on_date_var_change)
root.bind("<Return>", update_from_date_field)
date_entry.bind("<FocusOut>", update_from_date_field)

# Initial calculation for today's date
update_from_date_field()

# Planet selection for plot
planet_vars = {}
planet_order = ["Mercury", "Venus", "Earth", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune"]
planets_frame = tk.LabelFrame(root, text="Planets to Plot")
planets_frame.grid(row=2, column=0, columnspan=3, padx=10, pady=(0, 10), sticky="w")

for idx, name in enumerate(planet_order):
    var = tk.BooleanVar(value=False)
    planet_vars[name] = var
    cb = tk.Checkbutton(planets_frame, text=name, variable=var)
    cb.grid(row=0, column=idx, padx=(0, 6), sticky="w")

# Start the GUI
root.mainloop()
