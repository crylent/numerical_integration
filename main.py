from bifurcation import Param, Var
from integrator import run, Method
from gui import *


def collapse(section_layout, key):
    """
    Helper function that creates a Column that can be later made hidden, thus appearing "collapsed"
    :param section_layout: The layout for the section
    :param key: Key used to make this section visible / invisible
    :return: A pinned column that can be placed directly into your layout
    :rtype: sg.pin
    """
    return SGui.pin(SGui.Column(section_layout, key=key))


t_text, t_field = create_field("T", 1000)
h_text, h_field = create_field("h", 0.1)
window_key = "Window"
window_text, window_field = create_field(window_key, 100)

tab_group = SGui.TabGroup([
    [SGui.Tab("Van der Pol", create_layout(Layout.VanDerPol), key=Layout.VanDerPol)],
    [SGui.Tab("Rossler", create_layout(Layout.Rossler), key=Layout.Rossler)],
    [SGui.Tab("Nose-Hoover", create_layout(Layout.NoseHoover), key=Layout.NoseHoover)]
], expand_x=True, key="System")

methods = ["Euler", "Modified Euler", "Euler-Cromer", "Runge-Kutta 5", "Semi-implicit CD"]
method_key = "Method"
method_text, method_field = create_combo(method_key, methods)

bif_vars = ["x", "y", "z"]
bif_var_key = "Bif_Var"
bif_var_text, bif_var_field = create_combo("Bif. var.", bif_vars, bif_var_key)

bif_step_key = "Bif_Step"
bif_step_text, bif_step_field = create_field("Bif. param. step", 0.0002, bif_step_key)

bif_threshold_key = "Bif_Threshold"
bif_threshold_text, bif_threshold_field = create_field("Bif. threshold", 0.3, bif_threshold_key)

time_series_key = "TimeSeries"
phase_portrait_key = "PhasePortrait"
bifurcation_key = "Bifurcation"
volume_key = "Volume"

bifurcation_panel = [
    [bif_var_text, bif_var_field],
    [bif_step_text, bif_step_field],
    [bif_threshold_text, bif_threshold_field],
]
bif_section_key = "Bif_section"
volume_section_key = "Volume_section"

layout = [
    [t_text, t_field, h_text, h_field],
    [tab_group],
    [method_text, method_field],
    [SGui.Checkbox("Time-Series", True, key=time_series_key)],
    [SGui.Checkbox("Phase Portrait", True, key=phase_portrait_key)],
    [SGui.Checkbox("Bifurcation", True, key=bifurcation_key, enable_events=True)],
    [collapse(bifurcation_panel, bif_section_key)],
    [SGui.Checkbox("Volume", True, key=volume_key, enable_events=True)],
    [collapse([[window_text, window_field]], volume_section_key)],
    [SGui.OK("Run", expand_x=True)]
]
app = SGui.Window("Numerical Integrator", layout)

while True:
    event, values = app.read()
    if event == SGui.WIN_CLOSED:
        break
    enable_bifurcation = values[bifurcation_key]
    enable_volume = values[volume_key]
    if event == bifurcation_key:
        for key, elem in app.AllKeysDict.items():
            if str(key).endswith("_2"):
                elem.update(visible=enable_bifurcation)
        app[bif_section_key].update(visible=enable_bifurcation)
    elif event == volume_key:
        app[volume_section_key].update(visible=enable_volume)
    elif event == 'Run':
        layout_name = str(tab_group.Get())
        t, h, window = get_float(values, 'T'), get_float(values, 'h'), get_int(values, 'Window')
        time_series, phase_portrait = values[time_series_key], values[phase_portrait_key]
        if not enable_volume:
            window = None
        x, y, z = get_float(values, 'x_' + layout_name), \
            get_float(values, 'y_' + layout_name), \
            get_float(values, 'z_' + layout_name)
        a, b, c, a2, b2, c2 = \
            get_float(values, 'a_' + layout_name),\
            get_float(values, 'b'),\
            get_float(values, 'c_' + layout_name),\
            get_float(values, 'a_' + layout_name + '_2'),\
            get_float(values, 'b_2'),\
            get_float(values, 'c_' + layout_name + '_2')
        bif_target_params = []
        bif_max_values = []
        if a2 > a:
            bif_target_params.append(Param.A)
            bif_max_values.append(a2)
        if b2 > b:
            bif_target_params.append(Param.B)
            bif_max_values.append(b2)
        if c2 > c:
            bif_target_params.append(Param.C)
            bif_max_values.append(c2)
        bif_var = Var(bif_vars.index(values[bif_var_key]))
        app.hide()
        method = Method(methods.index(values[method_key]))
        bif = (bif_target_params, bif_max_values, bif_var)
        if not enable_bifurcation:
            bif = None
        if values["System"] == Layout.VanDerPol:
            mu = get_float(values, 'μ')
            run(
                [
                    lambda param, var: var[1],  # y
                    lambda param, var: param[0] * (1 - pow(var[0], 2)) * var[1] - var[0]  # mu * (1 - x^2) * y - x
                ],
                [mu],
                [x, y],
                t, h, window, method, bif,
                time_series, phase_portrait
            )
        elif values["System"] == Layout.Rossler:
            run(
                [
                    lambda param, var: -var[1] - var[2],  # -y - z
                    lambda param, var: var[0] + param[0] * var[1],  # x + a * y
                    lambda param, var: param[1] + var[2] * (var[0] - param[2])  # b + z * (x - c)
                ],
                [a, b, c],
                [x, y, get_float(values, 'z')],
                t, h, window, method, bif,
                time_series, phase_portrait
            )
        else:  # Nose-Hoover
            run(
                [
                    lambda param, var: -param[2] * var[0] + param[0] * var[1],  # -cx + ay
                    lambda param, var: -var[0] + var[1] * var[2],  # -x + yz
                    lambda param, var: 1 - pow(var[1], 2)  # 1 - y^2
                ],
                [a, None, c],
                [x, y, get_float(values, 'z')],
                t, h, window, method, bif,
                time_series, phase_portrait
            )
        app.un_hide()

app.close()
