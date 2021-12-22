import math, time, csv, json
from pathlib import Path
import matplotlib

# comment line below when only running this file.
# but when its used on the website it has to be there
matplotlib.use('Agg')


import matplotlib.pyplot as plt

PLOT_FOLDER = Path("plots")
DATA_FOLDER = Path("data")

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


def simulate_drone(max_engine_force, gravity, max_flight_altitude, drone_mass,
                   sampling_period, simulation_time,
                   signal_amplification, control_signal_max, target_altitudes, doubling_time, lead_time):
    target_altitudes_orig = target_altitudes.copy()
    target_altitude = target_altitudes[0][1]
    target_altitudes.pop(0)

    time_elapsed = 0  # s
    current_altitude = 0  # m
    current_velocity = 0
    current_acceleration = 0
    difference = target_altitude - current_altitude  # m
    control_signal = 0

    base_force = (gravity * drone_mass) * 0.

    time_samples = [time_elapsed]
    altitudes = [current_altitude]
    altitude_differences = [difference]
    signals = [control_signal]
    velocities = [current_velocity]
    accelerations = [current_acceleration]

    while time_elapsed < simulation_time:
        if len(target_altitudes) > 0 and time_elapsed > target_altitudes[0][0]:
            target_altitude = target_altitudes[0][1]
            target_altitudes.pop(0)

        # PID CONTROLLER
        difference = target_altitude - current_altitude

        proportional_part = altitude_differences[-1]  # proporcjonalna
        integral_part = (sampling_period / doubling_time) * sum(altitude_differences)  # calkowanie
        differential_part = (lead_time / sampling_period) * (difference - altitude_differences[-1])  # rozniczkowanie
        # print(proportional_part, integral_part, differential_part)

        control_signal = signal_amplification * (proportional_part + integral_part + differential_part)

        control_signal = max(min(control_signal, control_signal_max), 0)

        #  a + (b - a) * t.
        lifting_force = base_force + max_engine_force * (control_signal / control_signal_max)

        # SYSTEM SIMULATION
        current_acceleration = (lifting_force / drone_mass) - gravity
        current_velocity = current_acceleration * sampling_period + velocities[-1]
        current_altitude = velocities[-1] * sampling_period + altitudes[-1]

        current_altitude = max(current_altitude, 0)
        if current_altitude == 0:
            current_velocity = max(current_velocity, 0)

        # print(control_signal, lifting_force, current_altitude, current_acceleration, current_velocity )

        # DATA RECORDING
        time_elapsed += sampling_period

        altitudes.append(current_altitude)
        time_samples.append(time_elapsed)
        altitude_differences.append(difference)
        signals.append(control_signal)
        velocities.append(current_velocity)
        accelerations.append(current_acceleration)

    # QUALITY INDICATORS
    # because the target altitude changes those are not really reflacting reality
    final_error = target_altitude - current_altitude
    overshoot = ((max(altitudes) - target_altitude) / target_altitude) * 100  # %

    threshold = target_altitude * 0.05
    lower_bound = target_altitude - threshold
    upper_bound = target_altitude + threshold

    regulation_time = time_elapsed
    for i, level in enumerate(reversed(altitudes)):
        if level >= upper_bound or level <= lower_bound:
            regulation_time = time_elapsed - (i * sampling_period)
            break

    integral_regulation_accuracy_indicator = sampling_period * sum([abs(x) for x in altitude_differences])
    integral_regulation_accuracy_indicator_2 = sampling_period * sum([x * x for x in altitude_differences])

    integral_regulatory_cost_indicator = sampling_period * sum([abs(x) for x in signals])
    integral_regulatory_cost_indicator_2 = sampling_period * sum([x * x for x in signals])

    result = {
        "target_altitudes": target_altitudes_orig,
        "altitudes": altitudes,
        "time_samples": time_samples,
        "signals": signals,
        "velocities": velocities,
        "accelerations": accelerations,
        "simulation_time": simulation_time,
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
    fig, (ax1, ax2_1) = plt.subplots(2, 1, sharex=True)

    color = 'tab:red'
    ax1.set_ylabel("Signal", color=color)
    ax1.set_xlabel("Time [s]")

    ax1.plot(data["time_samples"], data["signals"], color=color)
    ax1.tick_params(axis='y', labelcolor=color)


    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis

    color = 'tab:blue'
    ax2.set_ylabel("Altitude [m]", color=color)
    ax2.plot(data["time_samples"], data["altitudes"], color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    ax2.set_ylim(bottom=0)

    for (alt_time, altitude), (next_alt_time, next_altitude) in zip(data["target_altitudes"],
                                                                    data["target_altitudes"][1:]):
        begin = alt_time / data["simulation_time"]
        end = next_alt_time / data["simulation_time"]
        ax2.axhline(y=altitude, xmin=begin, xmax=end, color='y', linestyle='--')

    alt_time = data["target_altitudes"][-1][0]
    begin = alt_time / data["simulation_time"]
    ax2.axhline(y=data["target_altitudes"][-1][1], xmin=begin, xmax=1, color='y', linestyle='--')

    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    color = 'tab:green'
    ax2_1.set_ylabel("velocities [m/s]", color=color)
    ax2_1.set_xlabel("Time [s]")

    ax2_1.plot(data["time_samples"], data["velocities"], color=color)
    ax2_1.tick_params(axis='y', labelcolor=color)

    ax2_2 = ax2_1.twinx()  # instantiate a second axes that shares the same x-axis

    # ax2_2.axhline(y=9.807, color='y', linestyle='--')
    color = 'tab:purple'
    ax2_2.set_ylabel("Accelerations [m/s^2]", color=color)
    ax2_2.plot(data["time_samples"], data["accelerations"], color=color)
    ax2_2.tick_params(axis='y', labelcolor=color)

    if save_plot:

        timestamp = round(time.time())

        plot_filename = f"drone_plot-{timestamp}.png"
        fig.savefig(plot_folder / plot_filename)

        data_filename = f"altitudes-{timestamp}.json"
        with open(data_folder / data_filename, 'w') as fp:
            json.dump(data, fp)

        return plot_filename
    else:
        plt.show()


if __name__ == '__main__':
    results = simulate_drone(MAX_ENGINE_FORCE, GRAVITY, MAX_FLIGHT_ALTITUDE, DRONE_MASS,
                             SAMPLING_PERIOD, SIMULATION_TIME,
                             SIGNAL_AMPLIFICATION, CONTROL_SIGNAL_MAX, TARGET_ALTITUDES, DOUBLING_TIME, LEAD_TIME)

    plot_save_water_levels(results, False, PLOT_FOLDER, DATA_FOLDER)
