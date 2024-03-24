from enums import Var
from gui import *
from integrator import run, Method

t_text, t_field = create_field("T", 10)
h_text, h_field = create_field("h", 0.01)

tab_group = SGui.TabGroup([
    [SGui.Tab("Rossler", create_sync_layout(Layout.Rossler), key=Layout.Rossler)],
    [SGui.Tab("Nose-Hoover", create_sync_layout(Layout.NoseHoover), key=Layout.NoseHoover)],
    [SGui.Tab("Lorens", create_sync_layout(Layout.Lorens), key=Layout.Lorens)]
], expand_x=True, key="System")

methods = ["Euler", "Modified Euler", "Euler-Cromer", "Runge-Kutta 5", "Semi-implicit CD"]
master_method_key = "Master Method"
slave_method_key = "Slave Method"
master_method_text, master_method_field = create_combo(master_method_key, methods)
slave_method_text, slave_method_field = create_combo(slave_method_key, methods)

sync_vars = ["x", "y", "z"]
sync_var_key = "Sync_Var"
sync_var_text, sync_var_field = create_combo("Sync. var.", sync_vars, sync_var_key)

sync_k_key = "Sync_k"
sync_k_text, sync_k_field = create_field("Sync. strength", 1, sync_k_key)

time_series_key = "TimeSeries"
phase_portrait_key = "PhasePortrait"
sync_error_key = "SyncError"

layout = [
    [t_text, t_field, h_text, h_field],
    [tab_group],
    [master_method_text, master_method_field],
    [slave_method_text, slave_method_field],
    [sync_var_text, sync_var_field],
    [sync_k_text, sync_k_field],
    [SGui.Checkbox("Time-Series", True, key=time_series_key)],
    [SGui.Checkbox("Phase Portrait", True, key=phase_portrait_key)],
    [SGui.Checkbox("Synchronization Error", True, key=sync_error_key)],
    [SGui.OK("Run", expand_x=True)]
]
app = SGui.Window("Synchronization", layout)

while True:
    event, values = app.read()
    if event == SGui.WIN_CLOSED:
        break
    elif event == 'Run':
        layout_name = str(tab_group.Get())
        t, h = get_float(values, 'T'), get_float(values, 'h')
        time_series, phase_portrait = values[time_series_key], values[phase_portrait_key]
        x, y, z, x2, y2, z2 = \
            get_float(values, 'x_' + layout_name),\
            get_float(values, 'y_' + layout_name),\
            get_float(values, 'z_' + layout_name),\
            get_float(values, 'x_' + layout_name + '_2'),\
            get_float(values, 'y_' + layout_name + '_2'),\
            get_float(values, 'z_' + layout_name + '_2')
        a, b, c, sigma, ro, beta = \
            get_float(values, 'a_' + layout_name),\
            get_float(values, 'b'),\
            get_float(values, 'c_' + layout_name),\
            get_float(values, 'σ'),\
            get_float(values, 'ρ'),\
            get_float(values, 'β')
        app.hide()
        master_method = Method(methods.index(values[master_method_key]))
        slave_method = Method(methods.index(values[slave_method_key]))
        sync_var = Var(sync_vars.index(values[sync_var_key]))
        sync_k = get_float(values, sync_k_key)
        enable_sync_error = values[sync_error_key]
        sync = [slave_method, [x2, y2, z2], sync_var, sync_k, sync_error_key]
        if values["System"] == Layout.Rossler:
            run(
                [
                    lambda param, var: -var[1] - var[2],  # -y - z
                    lambda param, var: var[0] + param[0] * var[1],  # x + a * y
                    lambda param, var: param[1] + var[2] * (var[0] - param[2])  # b + z * (x - c)
                ],
                [a, b, c],
                [x, y, z],
                t, h, None, master_method, None,
                time_series, phase_portrait, sync
            )
        elif values["System"] == Layout.Lorens:
            run(
                [
                    lambda param, var: param[0] * (var[1] - var[0]),  # σ * (y - x)
                    lambda param, var: var[0] * (param[1] - var[2]) - var[1],  # x * (ρ - z) - y
                    lambda param, var: var[0] * var[1] - param[2] * var[2]  # x * y - β * z
                ],
                [sigma, ro, beta],
                [x, y, z],
                t, h, None, master_method, None,
                time_series, phase_portrait, sync
            )
        else:  # Nose-Hoover
            run(
                [
                    lambda param, var: -param[2] * var[0] + param[0] * var[1],  # -cx + ay
                    lambda param, var: -var[0] + var[1] * var[2],  # -x + yz
                    lambda param, var: 1 - pow(var[1], 2)  # 1 - y^2
                ],
                [a, None, c],
                [x, y, z],
                t, h, None, master_method, None,
                time_series, phase_portrait, sync
            )
        app.un_hide()

app.close()
