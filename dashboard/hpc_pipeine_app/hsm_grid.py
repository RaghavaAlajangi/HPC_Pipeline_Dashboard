from pathlib import Path
import pickle

import dash_ag_grid as dag
from dash import callback_context as cc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import (callback, Input, Output, State, dcc, html)

from ..components import (text_input_comp, drop_input_button, line_breaks,
                          paragraph_comp)

DATA_DIR = Path(__file__).parents[2] / "resources"
CHUNK_DIR = DATA_DIR / "hsm_chunk_dir"


def load_data_chunk(chunk_id):
    """Load a specific chunk based on chunk_id"""
    if (CHUNK_DIR / f"chunk_num_{chunk_id}.pkl").exists():
        with open(CHUNK_DIR / f"chunk_num_{chunk_id}.pkl", "rb") as file:
            return pickle.load(file)
    else:
        return None


def create_hsm_grid():
    """Creates the HSMFS file explorer grid"""
    return html.Div(
        [
            dcc.Store(id="store_dcor_files", data=[]),

            paragraph_comp("Select DCOR-Colab file:"),

            line_breaks(times=1),
            drop_input_button(
                comp_id="input_group",
                drop_options=["DCOR"],
                default_drop="DCOR",
                drop_placeholder="Source",
                input_placeholder="Enter DVC path or DCOR-colab Id, "
                                  "Circle, or Dataset etc...",
                width=80
            ),
            line_breaks(times=2),
            paragraph_comp("Select HSMFS file/s:"),
            text_input_comp(comp_id="grid_filter",
                            placeholder="Search dataset name with a keyword",
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
                    "resizable": True,
                    "filter": True
                },
                dashGridOptions={
                    "autoGroupColumnDef": {
                        "headerName": "HSMFS Drive",
                        "cellRendererParams": {
                            "suppressCount": True,
                            "checkbox": True,
                        },
                    },
                    # Enable row copying
                    "enableCellTextSelection": True,
                    "ensureDomOrder": True,
                    "loadingOverlayComponent": "CustomLoadingOverlayForHSM",
                    "loadingOverlayComponentParams": {
                        "loadingMessage": "HSM drive is being updated...",
                        "color": "yellow",
                    },
                    "groupDefaultExpanded": 3,
                    "getDataPath": {"function": "getDataPath(params)"},
                    "treeData": True,
                    "animateRows": True,
                    # Select multiple rows
                    "rowSelection": "multiple",
                    # Select children rows with group selection
                    "groupSelectsChildren": True,
                    # Disable row selection by clicking
                    "suppressRowClickSelection": True,
                    "suppressAggFuncInHeader": True,
                    # Select only filtered rows
                    "groupSelectsFiltered": True,
                    # No blue highlight
                    "suppressRowHoverHighlight": True,
                },
                # rowData=load_data_chunk(1),
                enableEnterpriseModules=True,
                style={"height": 600},
                # getRowId="params.data.filepath",
            )
        ]
    )


def create_show_grid(comp_id):
    """Create show grid to display user selected files for final refining"""
    show_btn = dbc.Button(
        [
            "Selected files:",
            dbc.Badge(id="num_files", color="danger", text_color="dark",
                      className="ms-1"),
        ],
        color="info",
        style={"margin-right": "10px"}
    )

    show_grid = dag.AgGrid(
        id=comp_id,
        className="ag-theme-alpine-dark",
        columnDefs=[{"field": "filepath", "checkboxSelection": True,
                     "headerCheckboxSelection": True}],
        style={"width": "100%", "height": 400},
        dashGridOptions={
            "autoGroupColumnDef": {
                "headerName": "filepath",
                "cellRendererParams": {
                    "suppressCount": False,
                    "checkbox": True,
                },
            },
            "loadingOverlayComponent": "CustomLoadingOverlayForShow",
            "loadingOverlayComponentParams": {
                "loadingMessage": "Nothing to show....",
                "color": "red",
            },
            "animateRows": True,
            "rowSelection": "multiple",
            "suppressRowClickSelection": True,
            # no blue highlight
            "suppressRowHoverHighlight": True,
            "suppressAggFuncInHeader": True,
        },
        # rowData=rowdata,
        defaultColDef={"resizable": True, "sortable": True, "filter": True},
        columnSize="sizeToFit",
        # getRowId="params.data.filepath"
    )

    return html.Div(
        [
            dbc.Row([
                dbc.Col(show_btn, width="auto"),
            ],
                justify="center"
            ),
            dbc.Row([
                dbc.Col(show_grid, width=9),
            ],
                justify="center"
            )
        ],
        className="row justify-content-center"
    )


@callback(
    Output("hsm_grid", "rowData"),
    Input("pipeline_accord", "active_item"),
)
def load_hms_grid_data(pipeline_active_accord):
    """Show HSMFS grid only when user clicks on `Data to Process` accord"""
    if pipeline_active_accord == "hsm_accord":
        return load_data_chunk(1)
    else:
        return None


@callback(
    Output("show_grid", "rowData"),
    Output("show_grid", "selectedRows"),
    Input("hsm_grid", "selectedRows"),
    Input("store_dcor_files", "data"),
    prevent_initial_call=True
)
def update_show_grid_data(hsm_selection, selected_files):
    """Collect the user-selected data files and send them to `show_grid`"""
    if hsm_selection:
        hsm_files = ["/".join(s["filepath"]) for s in hsm_selection]
        selected_files = selected_files + hsm_files
    # Convert list of strings into ag grid rowdata
    rowdata = [{"filepath": i} for i in selected_files]
    return rowdata, rowdata


@callback(
    Output("num_files", "children"),
    Input("show_grid", "selectedRows"),
    prevent_initial_call=True
)
def display_selected_files_number(show_grid_rows):
    """Display the number of selected files"""
    return len(show_grid_rows)


@callback(
    Output("input_group_button", "disabled"),
    Input("input_group_drop", "value"),
    Input("input_group_text", "value")
)
def toggle_input_group_button(drop_value, filename):
    """Activates Add button in DCOR input bar only when the dropdown value
    and DCOR identifier is entered"""
    if drop_value and filename:
        return False
    else:
        return True


@callback(
    Output("store_dcor_files", "data"),
    Output("input_group_drop", "value"),
    Output("input_group_text", "value"),
    Input("input_group_button", "n_clicks"),
    Input("input_group_drop", "value"),
    Input("input_group_text", "value"),
    State("store_dcor_files", "data"),
    prevent_initial_call=True
)
def store_input_group_files(_, drop_input, text_input, cached_files):
    """Collects the user selected dcor files and cache them"""
    button_triggered = cc.triggered[0]["prop_id"].split(".")[0]

    if button_triggered == "input_group_button":
        if text_input and drop_input:
            input_path = f"{drop_input}: {text_input}"
            cached_files.append(input_path)
            return cached_files, drop_input, None
    raise PreventUpdate


@callback(
    Output("hsm_grid", "dashGridOptions"),
    Input("grid_filter", "value"),
    State("hsm_grid", "dashGridOptions"),
    prevent_initial_call=True
)
def update_filter(filter_value, gridOptions):
    """Filter grid rows based on filter value"""
    gridOptions["quickFilterText"] = filter_value
    return gridOptions
