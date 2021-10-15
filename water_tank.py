import math, time, csv, json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

PLOT_FOLDER = Path("plots")
DATA_FOLDER = Path("data")

TANK_AREA = 2  # m2
TANK_HEIGHT = 10  # m
OUTFLOW_COEF = 0.035  # m5/2
INFLOW_RATE = 0.05  # m3/s
SAMPLING_PERIOD = 1  # s

SIMULATION_TIME = 60 * 60  # s


def simulate_watertank(tank_area, tank_height, outflow_coef, inflow_rate, sampling_period, simulation_time):
    time_elapsed = 0  # s
    current_height = 0  # m
    time_samples = [time_elapsed]
    water_heights = [current_height]

    while time_elapsed < simulation_time:
        current_height = (1 / tank_area) * (
                -outflow_coef * math.sqrt(water_heights[-1]) + inflow_rate) * sampling_period + water_heights[-1]

        current_height = tank_height if current_height >= tank_height else current_height
        current_height = 0 if current_height <= 0 else current_height

        time_elapsed += sampling_period

        water_heights.append(current_height)
        time_samples.append(time_elapsed)

    result = {"water_heights": water_heights, "time_samples": time_samples}
    return result


def plot_save_water_levels(data, keep_result, plot_folder, data_folder):
    if not keep_result:
        plt.cla()

    plt.plot(data["time_samples"], data["water_heights"])
    plt.title("Water level in a tank")
    plt.ylabel("Water level [m]")
    plt.xlabel("Time [s]")
    # plt.show()

    timestamp = round(time.time())

    plot_filename = f"plot-{timestamp}.png"
    plt.savefig(plot_folder / plot_filename)

    data_filename = f"water_levels-{timestamp}.json"
    with open(data_folder / data_filename, 'w') as fp:
        json.dump(data, fp)

    return plot_filename


if __name__ == '__main__':
    results = simulate_watertank(TANK_AREA, TANK_HEIGHT, OUTFLOW_COEF, INFLOW_RATE, SAMPLING_PERIOD, SIMULATION_TIME)
    plot_save_water_levels(results, PLOT_FOLDER, DATA_FOLDER)
