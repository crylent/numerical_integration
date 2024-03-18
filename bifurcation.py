from enum import IntEnum
from scipy.signal import find_peaks


class Param(IntEnum):
    A = 0
    B = 1
    C = 2


class Var(IntEnum):
    X = 0
    Y = 1
    Z = 2


def bifurcation(integrator, params, target_param, max_value, target_var):
    param_history = []
    peaks_history = []
    while params[target_param] <= max_value:
        _, values_history = integrator(params)
        threshold_index = int(0.3 * len(values_history))
        values = values_history[target_var][threshold_index:]
        peaks, _ = find_peaks(values)
        param_history.extend(params[target_param] for _ in range(len(peaks)))
        peaks_history.extend(values[peak] for peak in peaks)
        params[target_param] += 0.002
    return param_history, peaks_history
