import enum
import PySimpleGUI as SGui


def create_field(name, key=None, length=6):
    input_key = key
    if input_key is None:
        input_key = name
    return SGui.Text(name + ":"), SGui.Input(size=(length, None), key=input_key)


class Layout(enum.Enum):
    VanDerPol = 1
    Rossler = 2
    NoseHoover = 3


def create_layout(selected_layout):
    layout_name = str(selected_layout)
    x_text, x_field = create_field("x", "x_" + layout_name)
    y_text, y_field = create_field("y", "y_" + layout_name)
    z_text, z_field = create_field("z", "z_" + layout_name)
    mu_text, mu_field = create_field("μ")
    a_text, a_field = create_field("a", "a_" + layout_name)
    b_text, b_field = create_field("b")
    c_text, c_field = create_field("c")

    if selected_layout == Layout.VanDerPol:
        return [
            [x_text, x_field],
            [y_text, y_field],
            [mu_text, mu_field]
        ]
    if selected_layout == Layout.NoseHoover:
        return [
            [x_text, x_field, a_text, a_field],
            [y_text, y_field],
            [z_text, z_field]
        ]
    return [
        [x_text, x_field, a_text, a_field],
        [y_text, y_field, b_text, b_field],
        [z_text, z_field, c_text, c_field]
    ]


def get_float(vals, key):
    try:
        return float(vals[key])
    except (ValueError, KeyError):
        return .0


def get_int(vals, key):
    return int(vals[key])
