from flask import Flask, render_template, redirect, url_for, send_from_directory, request
from pathlib import Path

import water_tank

app = Flask(__name__)

PLOT_FOLDER = Path("plots")
DATA_FOLDER = Path("data")

TANK_AREA = 2  # m2
TANK_HEIGHT = 10  # m
OUTFLOW_COEF = 0.035  # m5/2
INFLOW_RATE = 0.05  # m3/s
SAMPLING_PERIOD = 1  # s

SIMULATION_TIME = 30 * 60  # s

TARGET_LEVEL = 1.5  # m

SIGNAL_AMPLIFICATION = 0.015
DOUBLING_TIME = 0.5  # s 0.5 to 2
LEAD_TIME = 0.25  # s

CONTROL_SIGNAL_MAX = 10


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/plots/<filename>")
def show_plot(filename):
    return send_from_directory(PLOT_FOLDER, filename)


@app.route("/data/<filename>")
def show_water_tank_data(filename):
    return send_from_directory(DATA_FOLDER, filename)


@app.route("/water-tank")
def water_tank_simulation():
    target_level = float(request.args.get('target-level'))
    simulation_time = int(request.args.get('simulation-time'))

    signal_amplification = float(request.args.get('signal-amplification'))
    doubling_time = float(request.args.get('doubling-time'))
    lead_time = float(request.args.get('lead-time'))

    print(signal_amplification, doubling_time, lead_time)

    result = water_tank.simulate_watertank(TANK_AREA, TANK_HEIGHT, OUTFLOW_COEF, INFLOW_RATE,
                                           SAMPLING_PERIOD, simulation_time,
                                           signal_amplification, CONTROL_SIGNAL_MAX, target_level, doubling_time,
                                           lead_time)

    plot_name = water_tank.plot_save_water_levels(result, True, PLOT_FOLDER, DATA_FOLDER)

    return render_template('index.html',
                           plot_name=plot_name,
                           quality_indicators=result["quality_indicators"],
                           target_level=target_level,
                           simulation_time=simulation_time,
                           signal_amplification=signal_amplification,
                           doubling_time=doubling_time,
                           lead_time=lead_time)


if __name__ == '__main__':
    app.run()
