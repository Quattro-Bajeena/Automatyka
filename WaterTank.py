import  math
from matplotlib import pyplot as plt

TANK_AREA = 2  #m2
TANK_HEIGHT = 10 #m
OUTFLOW_COEF = 0.035  #m5/2
INFLOW_RATE = 0.05 #m3/s
SAMPLING_PERIOD = 1 #s

simulation_time = 60 * 60 #s

time_elapsed = 0 #s
current_height = 0 #m
time_samples = [time_elapsed]
water_heights = [current_height]

while time_elapsed < simulation_time:
    current_height = (1/TANK_AREA) * (-OUTFLOW_COEF * math.sqrt(water_heights[-1]) + INFLOW_RATE) * SAMPLING_PERIOD +  water_heights[-1]
    time_elapsed += SAMPLING_PERIOD

    water_heights.append(current_height)
    time_samples.append(time_elapsed)

plt.plot(time_samples, water_heights)
plt.show()