from flask import Flask, render_template, redirect, url_for, send_from_directory, request
from pathlib import Path

import water_tank
import drone

app = Flask(__name__)

PLOT_FOLDER = Path("plots")
DATA_FOLDER = Path("data")

# DRONE
GRAVITY = 10  # m/s^2
DRONE_MASS = 1  # kg

CONTROL_SIGNAL_MAX = 100
MAX_ENGINE_FORCE = 40  # N
MAX_FLIGHT_ALTITUDE = 1000  # m

# TARGET_ALTITUDE = 10  # m

SAMPLING_PERIOD = 0.01  # s
SIMULATION_TIME = 1 * 30  # s

SIGNAL_AMPLIFICATION = 10  # regulates the proportional part
DOUBLING_TIME = 10  # s regulates integral part
LEAD_TIME = 1  # s  regulates differential part

TARGET_ALTITUDES = [(0, 10), (5, 20), (10, 15), (15, 5)]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/plots/<filename>")
def show_plot(filename):
    return send_from_directory(PLOT_FOLDER, filename)


@app.route("/data/<filename>")
def show_water_tank_data(filename):
    return send_from_directory(DATA_FOLDER, filename)


@app.route("/drone")
def water_tank_simulation():
    target_altitudes = [(0, 10), (5, 20), (10, 15), (15, 5)]
    simulation_time = int(request.args.get('simulation-time'))

    signal_amplification = float(request.args.get('signal-amplification'))
    doubling_time = float(request.args.get('doubling-time'))
    lead_time = float(request.args.get('lead-time'))

    print(signal_amplification, doubling_time, lead_time)

    results = drone.simulate_drone(MAX_ENGINE_FORCE, GRAVITY, MAX_FLIGHT_ALTITUDE, DRONE_MASS,
                                   SAMPLING_PERIOD, simulation_time,
                                   signal_amplification, CONTROL_SIGNAL_MAX, target_altitudes, doubling_time, lead_time)

    plot_name = drone.plot_save_water_levels(results, True, PLOT_FOLDER, DATA_FOLDER)

    return render_template('index.html',
                           plot_name=plot_name,
                           quality_indicators=results["quality_indicators"],
                           target_altitudes=target_altitudes,
                           simulation_time=simulation_time,
                           signal_amplification=signal_amplification,
                           doubling_time=doubling_time,
                           lead_time=lead_time)


if __name__ == '__main__':
    app.run()
