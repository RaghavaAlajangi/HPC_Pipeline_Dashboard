from pathlib import Path
import pickle

import dash
import dash_ag_grid as dag
from dash import callback_context as cc
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import (callback, Input, Output, State, dcc, html)

from ..components import text_input_comp

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
    return html.Div(
        [
            html.Div(id="dummy_div"),
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
                        "loadingMessage": "One moment please...",
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
                rowData=load_data_chunk(1),
                enableEnterpriseModules=True,
                style={"height": 600},
                # getRowId="params.data.filepath",
            )
        ]
    )


def display_paths_comp(comp_id):
    show_btn = dbc.Button(
        [
            "Selected files:",
            dbc.Badge(id="num_files", color="danger", text_color="dark",
                      className="ms-1"),
        ],
        color="info",
        style={"margin-right": "10px"}
    )
    remove_btn = dbc.Button("Remove Selected", id="remove_entries",
                            color="info")

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
                dbc.Col(remove_btn, width="auto"),
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
    Output("show_grid", "rowData"),
    Output("num_files", "children"),
    Input("hsm_grid", "selectedRows"),
    Input("store_input_paths", "data"),
)
def display_selected_paths(hsm_selection, stored_input):
    original_paths = [] + stored_input
    if hsm_selection:
        # Get the list of user selected hsmfs paths (each path is a list
        # of strings) and join them with "/"
        selected_paths = ["/".join(s["filepath"]) for s in hsm_selection]
        original_paths = original_paths + selected_paths
    if original_paths:
        rowdata = [{"filepath": i} for i in original_paths]
        return rowdata, len(original_paths)
    else:
        rowdata = [{"filepath": i} for i in original_paths]
        return rowdata, len(original_paths)


@callback(
    Output("store_input_paths", "data"),
    Output("input_group_drop", "value"),
    Output("input_group_text", "value"),
    Input("input_group_button", "n_clicks"),
    Input("input_group_drop", "value"),
    Input("input_group_text", "value"),
    State("show_grid", "selectedRows"),
    Input("remove_entries", "n_clicks"),
    State("store_input_paths", "data"),
    prevent_initial_call=True
)
def store_input_group_paths(click_button, drop_input, text_input,
                            show_selection, remove_click, cached_paths):
    button_triggered = cc.triggered[0]["prop_id"].split(".")[0]

    if button_triggered == "input_group_button":
        if text_input and drop_input:
            input_path = f"{drop_input}: {text_input}"
            cached_paths.append(input_path)
            return cached_paths, None, None
    elif button_triggered == "remove_entries" and show_selection:
        cached_paths = [path for path in cached_paths if
                        path not in (sentry["filepath"] for sentry in
                                     show_selection)]
        return cached_paths, drop_input, text_input
    raise PreventUpdate


@callback(
    Output("hsm_grid", "selectedRows"),
    Input("remove_entries", "n_clicks"),
    State("show_grid", "selectedRows"),
    State("hsm_grid", "selectedRows"),
)
def update_hsm_grid_rowdata(click, show_selection, hsm_selection):
    if not click or not show_selection or not hsm_selection:
        return dash.no_update
    # Filter out matching entries from hms_selection. If a matching
    # filepath is found, the corresponding entry is removed from the
    # "hsm_grid" selection.
    selected_paths = set(dic["filepath"] for dic in show_selection)
    updated_hsm_selection = [hs for hs in hsm_selection if
                             "/".join(hs["filepath"]) not in selected_paths]
    return updated_hsm_selection


@callback(
    Output("hsm_grid", "dashGridOptions"),
    Input("grid_filter", "value"),
    State("hsm_grid", "dashGridOptions"),
)
def update_filter(filter_value, gridOptions):
    gridOptions["quickFilterText"] = filter_value
    return gridOptions


@callback(
    Output("remove_entries", "disabled"),
    Input("show_grid", "selectedRows"),
)
def update_filter(show_selection):
    if show_selection:
        return False
    else:
        return True
