import math

from bifurcation import bifurcation
from volume import eval_volume
import matplotlib.pyplot as plt
from enum import Enum


class Method(Enum):
    EULER = 0
    MODIFIED_EULER = 1
    EULER_CROMER = 2
    RUNGE_KUTTA_5 = 3
    SEMI_IMPLICIT_CD = 4


def euler_step(system, params, values, h):
    size = len(system)
    temp_values = values.copy()
    for i in range(size):
        values[i] += system[i](params, temp_values) * h
        # if i == sync_var:
        #    values[i] += sync_fi * ()


def modified_euler_step(system, params, values, h):
    size = len(system)
    temp_values = []
    for i in range(size):
        temp_values.append(values[i] + h / 2 * system[i](params, values))
    for i in range(size):
        values[i] += system[i](params, temp_values) * h


def euler_cromer_step(system, params, values, h):
    size = len(system)
    for i in range(size):
        values[i] += system[i](params, values) * h


runge_kutta_a = [
    [1/5],
    [3/40, 9/40],
    [44/45, -56/15, 32/9],
    [19372/6561, -25360/2187, 64448/6561, -212/729],
    [9017/3168, -355/33, 46732/5247, 49/176, -5163/18656],
    [35/384, 0, 500/1113, 125/192, -2187/6784, 11/84]
]


def runge_kutta_5_step(system, params, values, h):
    size = len(system)
    k = []
    temp_values = [values.copy()]
    for rk_order in range(5):
        k.append([])
        temp_values.append(values.copy())
        for i in range(size):
            k[rk_order].append(system[i](params, temp_values[rk_order]))
        for rk_line in range(rk_order + 1):
            for i in range(size):
                temp_values[rk_order + 1][i] += h * runge_kutta_a[rk_order][rk_line] * k[rk_order][i]
    values[:] = temp_values[-1][:]


def semi_implicit_cd_step(system, params, values, h):
    size = len(system)
    for i in range(size):
        values[i] += h / 2 * system[i](params, values)
    for i in reversed(range(size)):
        values[i] += h / 2 * system[i](params, values)


def integration_step(system, params, values, h, method, sync_var=None, sync_val=None, sync_k=1):
    sync_fi = 0
    if sync_var:
        sync_fi = sync_k * (sync_val - values[sync_var])
    match method:
        case Method.EULER:
            euler_step(system, params, values, h)
        case Method.MODIFIED_EULER:
            modified_euler_step(system, params, values, h)
        case Method.EULER_CROMER:
            euler_cromer_step(system, params, values, h)
        case Method.RUNGE_KUTTA_5:
            runge_kutta_5_step(system, params, values, h)
        case Method.SEMI_IMPLICIT_CD:
            semi_implicit_cd_step(system, params, values, h)
    if sync_var:
        values[sync_var] += sync_fi


def distance(a, b):
    sqr_dist = .0
    for i in range(len(a)):
        sqr_dist += pow(a[i] - b[i], 2)
    return math.sqrt(sqr_dist)


def integrator(system, params, values, t, h, method, sync_var=None, sync_values=None, sync_k=1, lyapunov_steps=0):
    size = len(system)
    time_history = []
    values_history = []
    lyapunov_shift = 0.001
    lyapunov_values = []
    if lyapunov_steps > 0:
        for i in range(size):
            lyapunov_values.append(values[:])
            lyapunov_values[i][i] += lyapunov_shift
            for step in range(lyapunov_steps):
                integration_step(system, params, lyapunov_values[i], h, method)
    for i in range(size):
        values_history.append([])
    for step in range(0, int(t / h)):
        time_history.append(step * h)
        if sync_var is None:
            integration_step(system, params, values, h, method)
        else:
            integration_step(system, params, values, h, method, sync_var, sync_values[step], sync_k)
        for i in range(size):
            values_history[i].append(values[i])
    max_lyapunov = .0
    if lyapunov_steps > 0:
        values_history_zip = list(zip(*values_history))
        for i in range(size):
            lyapunov = distance(lyapunov_values[i], values_history_zip[lyapunov_steps - 1]) / lyapunov_shift
            if lyapunov > max_lyapunov:
                max_lyapunov = lyapunov
        max_lyapunov = math.log(max_lyapunov) / (h * lyapunov_steps)
    return time_history, values_history, max_lyapunov


def run(system, params, initial_values, t, h, window, method, bif, time_series, phase_portrait, sync=None):
    time_history, values_history, max_lyapunov = integrator(system, params, initial_values, t, h, method)
    slave_history = []
    enable_sync_error = False
    if sync:
        slave_method, slave_init_values, sync_var, sync_k, enable_sync_error = sync
        sync_values = values_history[sync_var]
        _, slave_history, _ = integrator(
            system, params, slave_init_values, t, h, slave_method, sync_var, sync_values, sync_k
        )
    size = len(initial_values)

    if time_series:
        plt.title("Time-Series Plot")
        for i in range(size):
            plt.plot(time_history, values_history[i])
            if sync:
                plt.plot(time_history, slave_history[i])
        plt.show()

    if phase_portrait:
        plt.title("Phase Portrait")
        if size == 3:
            ax = plt.axes(projection='3d')
            ax.plot3D(*values_history)
            if sync:
                ax.plot3D(*slave_history)
        else:
            plt.plot(*values_history)
        plt.show()

    if window is not None:
        steps_history, volume_history = eval_volume(values_history, window)
        plt.title("Volume Dynamics")
        plt.plot(steps_history, volume_history)
        plt.show()

    if enable_sync_error:
        plt.title("Synchronization Error")
        for i in range(size):
            error_history = []
            for step in range(len(time_history)):
                error_history.append(slave_history[i][step] - values_history[i][step])
            plt.plot(time_history, error_history)
        plt.show()

    if bif is None:
        return

    bif_target_params, bif_max_values, bif_target_var, bif_step, bif_threshold, l_steps = bif
    for i in range(len(bif_target_params)):
        param = bif_target_params[i]
        val = bif_max_values[i]
        param_history_for_peaks, peaks_history, param_history_for_lyapunov, lyapunov_history = bifurcation(
            lambda bif_params: integrator(system, bif_params, initial_values, t, h, method, lyapunov_steps=l_steps),
            params, param, val, bif_target_var, bif_step, bif_threshold
        )
        fig, ax1 = plt.subplots()
        ax2 = ax1.twinx()
        ax1.scatter(param_history_for_peaks, peaks_history, 1)
        ax2.plot(param_history_for_lyapunov, lyapunov_history, color='r')
        plt.title("Bifurcation Diagram (param=" + param.name
                  + ", var=" + bif_target_var.name + ") / Max Lyapunov Exponent")
        plt.show()
