import math


def eval_volume(values_history, window):
    size = len(values_history)
    steps_history = []
    volume_history = []
    values_min = []
    values_max = []
    for i in range(size):
        values_min.append(float('inf'))
        values_max.append(-float('inf'))
    for step in range(len(values_history[0])):
        for i in range(size):
            value = values_history[i][step]
            if value > values_max[i]:
                values_max[i] = value
            elif value < values_min[i]:
                values_min[i] = value

        if step % window == 0:
            steps_history.append(step)
            volume = 1
            for i in range(size):
                volume *= values_max[i] - values_min[i]
                if math.isinf(volume):
                    volume = 0
                    break
            volume_history.append(volume)
            for i in range(size):
                values_min[i] = float('inf')
                values_max[i] = -float('inf')
    return steps_history, volume_history
