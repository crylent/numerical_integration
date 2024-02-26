from integrator import run
from gui import *


t_text, t_field = create_field("T")
h_text, h_field = create_field("h")
window_text, window_field = create_field("Window")

tab_group = SGui.TabGroup([
        [SGui.Tab("Default", create_layout(Layout.Default), key=Layout.Default)],
        [SGui.Tab("Rossler", create_layout(Layout.Rossler), key=Layout.Rossler)]
    ], expand_x=True)

modified_method_checkbox = SGui.Checkbox("Use Modified Method")

layout = [
    [t_text, t_field, h_text, h_field],
    [tab_group],
    [modified_method_checkbox],
    [window_text, window_field, SGui.OK("Run", expand_x=True)]
]
app = SGui.Window("Numerical Integrator", layout)

while True:
    event, values = app.read()
    if event == SGui.WIN_CLOSED:
        break
    elif event == 'Run':
        layout_name = str(tab_group.Get())
        t, h, window = get_float(values, 'T'), get_float(values, 'h'), get_int(values, 'Window')
        x, y = get_float(values, 'x_' + layout_name), get_float(values, 'y_' + layout_name)
        app.hide()
        if tab_group.Get() == Layout.Default:
            mu = get_float(values, 'μ')
            run(
                [
                    lambda var: var[1],  # y
                    lambda var: mu * (1 - pow(var[0], 2)) * var[1] - var[0]  # mu * (1 - pow(x, 2)) * y - x
                ],
                [x, y],
                t, h, window,
                modified_method_checkbox.Get()
            )
        else:
            a, b, c = get_float(values, 'a'), get_float(values, 'b'), get_float(values, 'c')
            run(
                [
                   lambda var: -var[1] - var[2],  # -y - z
                   lambda var: var[0] + a * var[1],  # x + a * y
                   lambda var: b + var[2] * (var[0] - c)  # b + z * (x - c)
                ],
                [x, y, get_float(values, 'z')],
                t, h, window,
                modified_method_checkbox.Get()
            )
        app.un_hide()

app.close()
