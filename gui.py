import enum
import PySimpleGUI as SGui


def create_field(name, default, key=None, two_fields=False, length=6):
    input_key = key
    if input_key is None:
        input_key = name
    text = SGui.Text(name)
    field1 = SGui.Input(size=(length, None), default_text=default, key=input_key)
    if not two_fields:
        return text, field1
    return text, field1, SGui.Input(size=(length, None), default_text=default, key=input_key + "_2")


def create_combo(name, values, key=None):
    input_key = key
    if input_key is None:
        input_key = name
    return SGui.Text(name), SGui.Combo(values, default_value=values[0], key=input_key)


class Layout(enum.Enum):
    VanDerPol = 1
    Rossler = 2
    NoseHoover = 3


def create_layout(selected_layout):
    layout_name = str(selected_layout)
    x_text, x_field = create_field("x", 1, "x_" + layout_name)
    y_text, y_field = create_field("y", 1, "y_" + layout_name)
    z_text, z_field = create_field("z", 1, "z_" + layout_name)
    mu_text, mu_field = create_field("μ", 1)
    a_text, a_field, a2_field = create_field("a", 0.2, "a_" + layout_name, True)
    b_text, b_field, b2_field = create_field("b", 0.2, two_fields=True)
    c_default = 0
    if selected_layout == Layout.Rossler:
        c_default = 5.7
    c_text, c_field, c2_field = create_field("c", c_default, "c_" + layout_name, two_fields=True)

    if selected_layout == Layout.VanDerPol:
        return [
            [x_text, x_field],
            [y_text, y_field],
            [mu_text, mu_field]
        ]
    if selected_layout == Layout.NoseHoover:
        return [
            [x_text, x_field, a_text, a_field, a2_field],
            [y_text, y_field, c_text, c_field, c2_field],
            [z_text, z_field]
        ]
    return [  # Rossler
        [x_text, x_field, a_text, a_field, a2_field],
        [y_text, y_field, b_text, b_field, b2_field],
        [z_text, z_field, c_text, c_field, c2_field]
    ]


def get_float(vals, key):
    try:
        return float(vals[key])
    except (ValueError, KeyError):
        return .0


def get_int(vals, key):
    return int(vals[key])
