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


def bifurcation(integrator, params, target_param, max_value, target_var, step, threshold):
    param_history_for_peaks = []
    peaks_history = []
    param_history_for_lyapunov = []
    lyapunov_history = []
    while params[target_param] <= max_value:
        _, values_history, lyapunov = integrator(params)
        threshold_index = int(threshold * len(values_history))
        values = values_history[target_var][threshold_index:]
        peaks, _ = find_peaks(values)
        param_history_for_lyapunov.append(params[target_param])
        lyapunov_history.append(lyapunov)
        param_history_for_peaks.extend(params[target_param] for _ in range(len(peaks)))
        peaks_history.extend(values[peak] for peak in peaks)
        params[target_param] += step
    return param_history_for_peaks, peaks_history, param_history_for_lyapunov, lyapunov_history
