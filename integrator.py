from volume import eval_volume
import matplotlib.pyplot as plt
from enum import Enum


class Method(Enum):
    EULER = 0
    MODIFIED_EULER = 1
    EULER_CROMER = 2
    RUNGE_KUTTA_5 = 3
    SEMI_IMPLICIT_CD = 4


def euler_step(system, values, h):
    size = len(system)
    temp_values = values.copy()
    for i in range(size):
        values[i] += system[i](temp_values) * h


def modified_euler_step(system, values, h):
    size = len(system)
    temp_values = []
    for i in range(size):
        temp_values.append(values[i] + h / 2 * system[i](values))
    for i in range(size):
        values[i] += system[i](temp_values) * h


def euler_cromer_step(system, values, h):
    size = len(system)
    for i in range(size):
        values[i] += system[i](values) * h


runge_kutta_a = [
    [1/5],
    [3/40, 9/40],
    [44/45, -56/15, 32/9],
    [19372/6561, -25360/2187, 64448/6561, -212/729],
    [9017/3168, -355/33, 46732/5247, 49/176, -5163/18656],
    [35/384, 0, 500/1113, 125/192, -2187/6784, 11/84]
]


def runge_kutta_5_step(system, values, h):
    size = len(system)
    k = []
    temp_values = [values.copy()]
    for rk_order in range(5):
        k.append([])
        temp_values.append(values.copy())
        for i in range(size):
            k[rk_order].append(system[i](temp_values[rk_order]))
        for rk_line in range(rk_order + 1):
            for i in range(size):
                temp_values[rk_order + 1][i] += h * runge_kutta_a[rk_order][rk_line] * k[rk_order][i]
    values[:] = temp_values[-1][:]


def semi_implicit_cd_step(system, values, h):
    size = len(system)
    for i in range(size):
        values[i] += h / 2 * system[i](values)
    for i in reversed(range(size)):
        values[i] += h / 2 * system[i](values)


def integrator(system, values, t, h, method):
    size = len(system)
    time_history = []
    values_history = []
    for i in range(size):
        values_history.append([])
    for step in range(0, int(t / h)):
        time_history.append(step * h)
        match method:
            case Method.EULER: euler_step(system, values, h)
            case Method.MODIFIED_EULER: modified_euler_step(system, values, h)
            case Method.EULER_CROMER: euler_cromer_step(system, values, h)
            case Method.RUNGE_KUTTA_5: runge_kutta_5_step(system, values, h)
            case Method.SEMI_IMPLICIT_CD: semi_implicit_cd_step(system, values, h)
        for i in range(size):
            values_history[i].append(values[i])
    return time_history, values_history


def run(system, initial_values, t, h, window, method):
    time_history, values_history = integrator(system, initial_values, t, h, method)
    steps_history, volume_history = eval_volume(values_history, window)
    size = len(initial_values)

    plt.title("Time-Series Plot")
    for i in range(size):
        plt.plot(time_history, values_history[i])
    plt.show()

    plt.title("Phase Portrait")
    if size == 3:
        ax = plt.axes(projection='3d')
        ax.plot3D(*values_history)
    else:
        plt.plot(*values_history)
    plt.show()

    plt.title("Volume Dynamics")
    plt.plot(steps_history, volume_history)
    plt.show()
