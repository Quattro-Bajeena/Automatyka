from flask import Flask, render_template, redirect, url_for, send_from_directory, request
from pathlib import Path

import water_tank


app = Flask(__name__)

PLOT_FOLDER = Path("plots")
DATA_FOLDER = Path("data")


@app.route("/")
def index():
    plot_name = request.args.get('plot_name')
    return render_template("index.html", plot_filename=plot_name)


@app.route("/plots/<filename>")
def show_plot(filename):
    return send_from_directory(PLOT_FOLDER, filename)


@app.route("/data/<filename>")
def show_water_tank_data(filename):
    return send_from_directory(DATA_FOLDER, filename)


@app.route("/water-tank", methods=['POST'])
def water_tank_simulation():
    print(request.form)
    tank_area = float(request.form['tank-area'])
    tank_height = float(request.form['tank-height'])
    outflow_coef = float(request.form['outflow-coef'])
    inflow_rate = float(request.form['inflow-rate'])
    sampling_period = float(request.form['sampling-period'])
    simulation_time = int(request.form['simulation-time'])
    keep_result = bool(request.form.get('keep-result'))
    print(keep_result)

    result = water_tank.simulate_watertank(tank_area, tank_height, outflow_coef, inflow_rate, sampling_period,
                                           simulation_time)
    plot_name = water_tank.plot_save_water_levels(result, keep_result, PLOT_FOLDER, DATA_FOLDER)

    return redirect(url_for('index', plot_name=plot_name))


if __name__ == '__main__':
    app.run()
