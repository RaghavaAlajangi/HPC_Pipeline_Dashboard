from pathlib import Path
import pickle

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import (callback, Input, Output, State, dcc, html, ALL, ctx, Patch)

from ..components import text_input_comp

DATA_DIR = Path(__file__).parents[2] / "resources"
CHUNK_DIR = DATA_DIR / "hsm_chunk_dir"
CHUNK_IDX_PATH = DATA_DIR / "hsm_chunk_index.pkl"


def load_data_chunk(chunk_id):
    """Load a specific chunk based on chunk_id"""
    if (CHUNK_DIR / f"chunk_num_{chunk_id}.pkl").exists():
        with open(CHUNK_DIR / f"chunk_num_{chunk_id}.pkl", "rb") as file:
            return pickle.load(file)
    else:
        return None


def determine_chunk_to_load(filter_value):
    if CHUNK_IDX_PATH.exists():
        with open(str(CHUNK_IDX_PATH), "rb") as f:
            index_file = pickle.load(f)
        # If the filter value is in the index, return the first chunk
        if filter_value in index_file:
            return list(index_file[filter_value])[0]
        else:
            return 0  # Default to the first chunk if keyword is not found
    else:
        return None


def create_hsm_grid():
    return html.Div([
        dcc.Store(id="store_input_paths", data=[]),
        text_input_comp(comp_id="grid_filter",
                        placeholder="Filter with name...",
                        width=30, middle=False),
        dag.AgGrid(
            id="hsm_grid",
            className="ag-theme-alpine-dark",
            columnDefs=[
                {"field": "dateModified"},
            ],
            defaultColDef={
                "flex": 1,
                "sortable": True,
            },
            dashGridOptions={
                "autoGroupColumnDef": {
                    "headerName": "HSMFS Drive",
                    "minWidth": 150,
                    "cellRendererParams": {
                        "suppressCount": True,
                        "checkbox": True,
                    },
                },
                "groupDefaultExpanded": 6,
                "getDataPath": {"function": "getDataPath(params)"},
                "treeData": True,
                "animateRows": True,
                "rowSelection": "multiple",
                "groupSelectsChildren": True,
                "suppressRowClickSelection": True,
                # no blue highlight
                "suppressRowHoverHighlight": True,
            },
            enableEnterpriseModules=True,
            style={"height": 600}
        ),
        dbc.Pagination(
            id="grid_pagination",
            min_value=1,
            max_value=1,
            active_page=1,
            first_last=True,
            previous_next=True,
            fully_expanded=False,
            style={"justify-content": "center"},
            class_name="pagination-custom"
        )
    ])


def display_paths_comp(comp_id):
    return html.Div(
        className="row justify-content-center",
        children=[
            html.Div(
                dbc.Button([
                    "Selected files:",
                    dbc.Badge(id="num_files", color="danger",
                              text_color="dark", className="ms-1"),
                ],
                    color="info",
                ),
                style={"marginLeft": "0px", "width": "80%"}
            ),
            dbc.Card(
                id=comp_id,
                body=True,
                style={"max-height": "25rem", "width": "80%",
                       "overflow-y": "scroll"},
            )
        ]
    )


def convert_paths_to_buttons(paths):
    return [
        dbc.Row([
            html.Li([
                dbc.Button(
                    "X",
                    n_clicks=0,
                    key=[name],
                    style={"width": "20px", "height": "20px",
                           "padding": "0px", "margin-right": "5px"},
                    class_name="btn btn-danger btn-sm",
                    id={"type": "remove_file", "index": name}
                ),
                html.Span(name)
            ]),
        ],
            style={"flexWrap": "nowrap"}
        ) for name in paths
    ]


@callback(
    Output("grid_pagination", "max_value"),
    Input("grid_pagination", "max_value")
)
def update_max_value(current_page):
    # Replace this with your logic to calculate the new max_value
    num_chunks = len(
        [f for f in CHUNK_DIR.glob("chunk_num_*.pkl") if f.is_file()])
    # new_max_value = 10
    return num_chunks


@callback(
    Output("hsm_grid", "rowData"),
    [Input("grid_filter", "value"),
     Input("grid_pagination", "active_page")],
)
def update_grid_data(filter_value, selected_chunk_page):
    if filter_value:
        chunk_id = determine_chunk_to_load(filter_value)
    else:
        chunk_id = selected_chunk_page

    return load_data_chunk(chunk_id)


@callback(
    Output("grid_pagination", "active_page"),
    [Input("grid_filter", "value")],
)
def update_pagination_page(filter_value):
    if filter_value:
        return determine_chunk_to_load(filter_value)
    raise PreventUpdate


@callback(
    Output("upload_show", "children"),
    Output("num_files", "children"),
    Input("hsm_grid", "selectedRows"),
    Input("store_input_paths", "data"),
)
def display_selected_paths(selected_rows, stored_input):
    original_paths = [] + stored_input
    if selected_rows:
        # Get the list of user selected hsmfs paths (each path is a list
        # of strings) and join them with "/"
        selected_paths = ["/".join(s["filepath"]) for s in selected_rows]
        original_paths = original_paths + selected_paths
    return convert_paths_to_buttons(original_paths), len(original_paths)


@callback(
    Output("hsm_grid", "dashGridOptions"),
    Input("grid_filter", "value"),
    State("hsm_grid", "dashGridOptions"),
)
def update_filter(filter_value, gridOptions):
    gridOptions["quickFilterText"] = filter_value
    return gridOptions


@callback(
    Output("hsm_grid", "selectedRows"),
    Input({"type": "remove_file", "index": ALL}, "n_clicks"),
    State("hsm_grid", "selectedRows"),
    prevent_initial_call=True
)
def remove_paths_from_list(remove_buttons, selected_rows):
    if sum(remove_buttons) > 0 and selected_rows is not None:
        selects = Patch()
        for x in range(len(selected_rows) - 1, -1, -1):
            if all(i in ctx.triggered_id.index.split("/") for i in
                   selected_rows[x]["filepath"]):
                del selects[x]
        return selects
    raise PreventUpdate
