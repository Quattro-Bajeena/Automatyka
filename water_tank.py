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

SIMULATION_TIME = 30 * 60  # s

TARGET_LEVEL = 1.5  # m

SIGNAL_AMPLIFICATION = 0.015
DOUBLING_TIME = 0.5  # s 0.5 to 2
LEAD_TIME = 0.25  # s

CONTROL_SIGNAL_MAX = 10


def simulate_watertank(tank_area, tank_height, outflow_coef, max_inflow_rate,
                       sampling_period, simulation_time,
                       signal_amplification, control_signal_max, target_level, doubling_time, lead_time):
    time_elapsed = 0  # s
    current_height = 0  # m
    difference = target_level - current_height  # m
    control_signal = 0

    time_samples = [time_elapsed]
    water_heights = [current_height]
    level_differences = [difference]
    signals = [control_signal]

    while time_elapsed < simulation_time:
        difference = target_level - current_height

        control_signal = signal_amplification * \
                         (level_differences[-1]
                          + (sampling_period / doubling_time) * sum(level_differences)
                          + (lead_time / sampling_period) * (level_differences[-1] - difference)
                          )

        control_signal = min(max(control_signal, 0), control_signal_max)

        #  a + (b - a) * t.
        inflow_rate = max_inflow_rate * (control_signal / control_signal_max)

        current_height = (1 / tank_area) * (
                -outflow_coef * math.sqrt(water_heights[-1]) + inflow_rate) * sampling_period + water_heights[-1]

        current_height = min(max(current_height, 0), tank_height)

        time_elapsed += sampling_period

        water_heights.append(current_height)
        time_samples.append(time_elapsed)
        level_differences.append(difference)
        signals.append(control_signal)

    final_error = target_level - current_height
    overshoot = ((max(water_heights) - target_level) / target_level) * 100  # %

    threshold = target_level * 0.05
    lower_bound = target_level - threshold
    upper_bound = target_level + threshold

    regulation_time = time_elapsed
    for i, level in enumerate(reversed(water_heights)):
        if level >= upper_bound or level <= lower_bound:
            regulation_time = time_elapsed - (i * sampling_period)
            break

    integral_regulation_accuracy_indicator = sampling_period * sum([abs(x) for x in level_differences])
    integral_regulation_accuracy_indicator_2 = sampling_period * sum([x * x for x in level_differences])

    integral_regulatory_cost_indicator = sampling_period * sum([abs(x) for x in signals])
    integral_regulatory_cost_indicator_2 = sampling_period * sum([x * x for x in signals])

    result = {
        "target_level" : target_level,
        "water_heights": water_heights,
        "time_samples": time_samples,
        "signals": signals,
        "quality_indicators": {
            "final_error": round(final_error, 5),
            "overshoot": round(overshoot, 1),
            "regulation_time": regulation_time,
            "Ie": round(integral_regulation_accuracy_indicator, 1),
            "Ie2": round(integral_regulation_accuracy_indicator_2, 1),
            "Iu": round(integral_regulatory_cost_indicator, 1),
            "Iu2": round(integral_regulatory_cost_indicator_2, 1)
        }}

    return result


def plot_save_water_levels(data, save_plot, plot_folder, data_folder):
    fig, ax1 = plt.subplots()

    color = 'tab:blue'
    ax1.set_ylabel("Water level [m]", color=color)
    ax1.set_xlabel("Time [s]")

    ax1.plot(data["time_samples"], data["water_heights"], color=color)
    ax1.tick_params(axis='y', labelcolor=color)

    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:red'
    ax2.set_ylabel("Signal strength", color=color)
    ax2.plot(data["time_samples"], data["signals"], color=color)
    ax2.tick_params(axis='y', labelcolor=color)

    ax1.axhline(y=data["target_level"], color='y', linestyle='--')


    fig.tight_layout()  # otherwise the right y-label is slightly clipped

    if save_plot:

        timestamp = round(time.time())

        plot_filename = f"plot-{timestamp}.png"
        fig.savefig(plot_folder / plot_filename)

        data_filename = f"water_levels-{timestamp}.json"
        with open(data_folder / data_filename, 'w') as fp:
            json.dump(data, fp)

        return plot_filename
    else:
        plt.show()


if __name__ == '__main__':
    results = simulate_watertank(TANK_AREA, TANK_HEIGHT, OUTFLOW_COEF, INFLOW_RATE,
                                 SAMPLING_PERIOD, SIMULATION_TIME,
                                 SIGNAL_AMPLIFICATION, CONTROL_SIGNAL_MAX, TARGET_LEVEL, DOUBLING_TIME, LEAD_TIME)

    plot_save_water_levels(results, False, PLOT_FOLDER, DATA_FOLDER)
