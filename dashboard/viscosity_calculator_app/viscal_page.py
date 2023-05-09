import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import numpy as np

from ..components import paragraph_comp, line_breaks


def formula(flwrate, chsize, n, k):
    """Formula to calculate the viscosity of a fluid based on its flow rate,
    channel size, and power law parameters.
    """
    shear_rate = 8 * flwrate / ((chsize * 1e-3) ** 3) * (0.6671 + 0.2121 / n)
    viscosity = k * (shear_rate ** (n - 1)) * 1000
    return viscosity


def compute_viscosity(float_feats):
    """This function takes in a list of floats and returns the viscosity
    of the fluid.
    """
    medium, temp, chsize, flwrate = float_feats
    temp_kelvin = temp + 273.15
    alpha = 0.00223
    lambd = 3379.7
    if medium == 1.0:
        n = alpha * temp_kelvin - 0.0056
        k = 2.3 * 10 ** -6 * np.exp(lambd * (1 / temp_kelvin))
        viscosity = formula(flwrate, chsize, n, k)
        return viscosity
    if medium == 2.0:
        n = alpha * temp_kelvin - 0.0744
        k = 5.7 * 10 ** -6 * np.exp(lambd * (1 / temp_kelvin))
        viscosity = formula(flwrate, chsize, n, k)
        return viscosity
    if medium == 3.0:
        n = alpha * temp_kelvin - 0.1455
        k = 16.52 * 10 ** -6 * np.exp(lambd * (1 / temp_kelvin))
        viscosity = formula(flwrate, chsize, n, k)
        return viscosity
    else:
        return None


def viscal_app():
    return dbc.Card([

        html.H4("RT-DC Buffer Viscosity Calculator"),
        line_breaks(2),
        html.H6("Medium"),
        dcc.Dropdown(id="medium",
                     searchable=True,
                     placeholder="Select a medium",
                     options=[
                         {"label": "0.5% MC-PBS",
                          "value": "1"},
                         {"label": "0.6% MC-PBS",
                          "value": "2"},
                         {"label": "0.84% MC-PBS",
                          "value": "3"}
                     ],
                     style={"width": "250px",
                            "height": "35px",
                            "color": "blue",
                            }),
        line_breaks(1),
        html.H6("Temperature [°C]"),
        dbc.Input(id="temperature",
                  persistence=False,
                  placeholder="Enter the temperature...",
                  style={"width": "250px",
                         "height": "39px",
                         },
                  type="text"),
        line_breaks(1),
        html.H6("Channel size [μm]"),
        dbc.Input(id="channel_size",
                  type="text",
                  persistence=False,
                  placeholder="Enter the channel size...",
                  style={"width": "250px",
                         "height": "39px"
                         }),
        line_breaks(1),
        html.H6("Flowrate [μl/s]"),
        dbc.Input(id="flow_rate",
                  type="text",
                  persistence=False,
                  placeholder="Enter the flow-rate...",
                  style={"width": "250px",
                         "height": "39px"
                         }),
        line_breaks(1),
        dbc.Button("Calculate", id="submit_button", color="primary",
                   className="my-button-class", disabled=True),
        line_breaks(1),
        html.H5("Computed viscosity [mPa.s]"),
        dbc.Card(
            id="display_viscosity",
            body=True,
            className="align-items-center",
            style={"width": "18rem", "height": "6rem"},
        ),
        dcc.Store(id="store_viscosity"),
        line_breaks(4),
        dbc.Alert([
            html.I(className="bi bi-exclamation-triangle-fill me-2"),
            "Note:",
            paragraph_comp(
                "The viscosity calculator was designed for the "
                "temperatures between 22 °C and 37 °C. For the temperatures "
                "outside of this range, the viscosity curve is extrapolated.",
                indent=2
            ),
        ],
            style={"color": "black", "width": "fit-content"},
            color="warning",
        ),
    ],
        style={"height": "80rem",
               "align-items": "center",
               "color": "white",
               "background-color": "#424447",
               },
    )


@callback(
    Output("store_viscosity", "data"),
    Input("medium", "value"),
    Input("temperature", "value"),
    Input("channel_size", "value"),
    Input("flow_rate", "value"))
def store_viscosity(medium, temperature, channel_size, flow_rate):
    """This callback function takes the inputs from the html components
    (see the id's), compute the viscosity and store it in dcc.Store
    component as s dictionary.
    """
    # dashboard inputs from users are of string type
    string_feats = [medium, temperature, channel_size, flow_rate]
    if len(string_feats) != 4 or None in string_feats or "" in string_feats:
        return None
    # Convert string inputs into floats
    float_feats = list(map(float, string_feats))
    viscosity = compute_viscosity(float_feats)
    return {"viscosity": viscosity}


@callback(
    Output("display_viscosity", "children"),
    Input("submit_button", "n_clicks"),
    State("store_viscosity", "data"))
def display_output(n_clicks, stored_viscosity):
    """This call back function is activated when user click on submit button.
    When do so, stored viscosity value will be displayed in the output
    component
    """
    trigger = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if stored_viscosity is not None:
        viscosity = stored_viscosity["viscosity"]
        if "submit_button" in trigger:
            return html.H5(f"{viscosity:.3f}")
        else:
            return dash.no_update
    else:
        return dash.no_update


@callback(Output("submit_button", "disabled"),
          Input("temperature", "value"),
          Input("channel_size", "value"),
          Input("flow_rate", "value"),
          Input("medium", "value"))
def toggle_submit_button(medium, temperature, channel_size, flow_rate):
    """This callback function checks if any of the given inputs are empty
    or None. If they are not empty or None, it disables the submit button.
    """
    string_feats = [medium, temperature, channel_size, flow_rate]
    if len(string_feats) != 4 or None in string_feats or "" in string_feats:
        return True
    else:
        return False


@callback(
    [Output("temperature", "value"),
     Output("channel_size", "value"),
     Output("flow_rate", "value"),
     Output("medium", "value")],
    Input("submit_button", "n_clicks"))
def reset_inputs(click):
    """This call back function will reset the input boxes as soon as user
      click on the submit button
    """
    trigger = [p["prop_id"] for p in dash.callback_context.triggered][0]
    if "submit_button" in trigger:
        return [None] * 4
    else:
        return dash.no_update
