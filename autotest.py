import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks


df = pd.DataFrame({'price':[340.6, 35.66, 33.98, 38.67, 32.99, 32.04, 37.64, 
                            38.22, 37.13, 38.57, 32.4,  34.98, 36.74, 32.9,
                            32.52, 38.83, 33.9,  32.62, 38.93, 32.14, 33.09, 
                            34.25, 34.39, 33.28, 38.13, 36.25, 38.91, 38.9, 
                            36.85, 32.17, -2.07, 34.49, 35.7, 32.54, 37.91, 
                            37.35, 32.05, 38.03, 0.32,  33.87, 33.16, 34.74, 
                            32.47, 33.31, 34.54, 36.6,  36.09, 35.49, 370.51, 
                            37.33, 37.54, 33.32, 35.09, 33.08, 38.3,  34.32, 
                            37.01, 33.63, 36.35, 33.77, 33.74, 36.62, 36.74, 
                            37.76, 35.58, 38.76, 36.57, 37.05, 35.33, 36.41, 
                            35.54, 37.48, 36.22, 36.19, 36.43, 34.31, 34.85, 
                            38.76, 38.52, 38.02, 36.67, 32.51, 321.6, 37.82,
                            34.76, 33.55, 32.85, 32.99, 35.06]}, 
                   index = pd.date_range('2014-03-03 06:00','2014-03-06 22:00',freq='H'))


import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

if __name__ == '__main__':
    # example data
    df = pd.DataFrame(
        {
            'time': np.arange(0, 8),
            'data': [1, 1.01, 2.0, 2.01, 2.5, 2.7, 3.1, 3.101]}
    )
    plt.plot(
        df['time'], df['data'], label=f"original data",
        marker='x', lw=0.5, ms=2.0, color="black",
    )

    # filter and group plateaus
    max_difference = 0.05 #difference across plateau
    min_number_points = 2
    # group by maximum difference
    group_ids = (abs(df['data'].diff(1)) > max_difference).cumsum()
    plateau_idx = 0
    for group_idx, group_data in df.groupby(group_ids):
        # filter non-plateaus by min number of points
        if len(group_data) < min_number_points:
            continue
        plateau_idx += 1
        plt.plot(
            group_data['time'], group_data['data'], label=f"Plateau-{plateau_idx}",
            marker='x', lw=1.5, ms=5.0,
        )
        _time = group_data['time'].mean()
        _value = group_data['data'].mean()
        plt.annotate(
            f"Plateau-{plateau_idx}", (_time, _value), ha="center",
        )
    plt.legend()
    plt.show()