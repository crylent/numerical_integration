from volume import eval_volume
import matplotlib.pyplot as plt


def euler_integrator(system, values, t, h, use_modified_method=False):
    size = len(system)
    time_history = []
    values_history = []
    for i in range(size):
        values_history.append([])
    for step in range(0, int(t / h)):
        time_history.append(step * h)
        if use_modified_method:
            temp_values = []
            for i in range(size):
                temp_values.append(values[i] + h / 2 * system[i](values))
            for i in range(size):
                values[i] += system[i](temp_values) * h
                values_history[i].append(values[i])
        else:
            for i in range(size):
                values[i] += system[i](values) * h
                values_history[i].append(values[i])
    return time_history, values_history


def run(system, initial_values, t, h, window, use_modified_method=False):
    time_history, values_history = euler_integrator(system, initial_values, t, h, use_modified_method)
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
