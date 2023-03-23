import dash
from dash import dcc, html, callback, Input, Output, State
import dash_bootstrap_components as dbc
import numpy as np


def compute_viscosity(parameters):
    global k_mc0x, n_mc0x
    medium, temp, chsize, flwrate = parameters
    if medium == 1.0:
        n_mc0x = 0.0026 * temp + 0.590
        k_mc0x = 0.05 * np.exp(35 * (1 / temp))
    if medium == 2.0:
        n_mc0x = 0.0024 * temp + 0.529
        k_mc0x = 0.15 * np.exp(27.8 * (1 / temp))
    if medium == 3.0:
        n_mc0x = 0.0021 * temp + 0.467
        k_mc0x = 0.40 * np.exp(30.6 * (1 / temp))
    shear_rate = 8 * flwrate / ((chsize * 1e-3) ** 3) * (
            0.6671 + 0.2121 / n_mc0x)
    viscosity = k_mc0x * (shear_rate ** (n_mc0x - 1)) * 1000
    viscosity = round(viscosity, 3)
    return viscosity


def viscal_app():
    return dbc.Card([
        html.Br(), html.Br(), html.Br(),
        html.H4('RT-DC Buffer Viscosity Calculator'),
        html.Br(), html.Br(),
        html.H6('Medium'),
        dcc.Dropdown(id="medium",
                     searchable=True,
                     placeholder='Select a medium',
                     options=[
                         {'label': '0.5% MC-PBS',
                          'value': '1'},
                         {'label': '0.6% MC-PBS',
                          'value': '2'},
                         {'label': '0.84% MC-PBS',
                          'value': '3'}
                     ],
                     style={'width': '250px',
                            'height': '35px',
                            'color': 'blue',
                            }),
        html.Br(),
        html.H6('Temperature [°C]'),
        dbc.Input(id="temperature",
                  persistence=False,
                  placeholder="Enter the temperature...",
                  style={'width': '250px',
                         'height': '39px',
                         },
                  type="text"),
        html.Br(),
        html.H6('Channel size [μm]'),
        dbc.Input(id="channel_size",
                  type='text',
                  persistence=False,
                  placeholder='Enter the channel size...',
                  style={'width': '250px',
                         'height': '39px'
                         }),
        html.Br(),
        html.H6('Flowrate [μl/s]'),
        dbc.Input(id="flow_rate",
                  type='text',
                  persistence=False,
                  placeholder='Enter the flow-rate...',
                  style={'width': '250px',
                         'height': '39px'
                         }),
        html.Br(),
        dbc.Button("Calculate", id="submit_button", color="primary",
                   className="my-button-class"),
        html.Br(),
        html.H5("Computed viscosity [mPa.s]"),
        dbc.Card(
            id='display_viscosity',
            body=True,
            className="align-items-center",
            style={"width": "18rem", "height": "6rem"},
        ),
        dcc.Store(id='store_viscosity'),
    ],
        style={"height": "50rem",
               "align-items": "center",
               "color": "white",
               'background-color': "#424447",
               },
    )


# This callback function takes the inputs from
# the html components (see the id's), compute
# the viscosity and store it in dcc.Store
# component as s dictionary.
@callback(
    Output("store_viscosity", "data"),
    [Input("medium", "value"),
     Input("temperature", "value"),
     Input("channel_size", "value"),
     Input("flow_rate", "value")])
def store_viscosity(medium, temperature, channel_size, flow_rate):
    # dashboard inputs from users are of string type
    string_feats = [medium, temperature, channel_size, flow_rate]
    if len(string_feats) != 4 or None in string_feats or '' in string_feats:
        return None
    # Convert string inputs into floats
    float_feats = list(map(float, string_feats))
    viscosity = compute_viscosity(float_feats)
    return {'viscosity': viscosity}


# This call back function is activated when
# user click on submit button. When do so, stored
# viscosity value will be displayed in the output
# component
@callback(
    Output('display_viscosity', 'children'),
    Input('submit_button', 'n_clicks'),
    State('store_viscosity', 'data'))
def display_output(n_clicks, stored_viscosity):
    trigger = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if stored_viscosity is not None:
        viscosity = stored_viscosity['viscosity']
        if 'submit_button' in trigger:
            return html.H5(f"{viscosity}")
        else:
            return dash.no_update
    else:
        return dash.no_update


# This call back function will reset the input boxes
# as soon as user click on the submit button
@callback(
    [Output("temperature", "value"),
     Output("channel_size", "value"),
     Output("flow_rate", "value")],
    Input('submit_button', 'n_clicks'))
def reset_inputs(click):
    trigger = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'submit_button' in trigger:
        return [''] * 3
    else:
        return dash.no_update
