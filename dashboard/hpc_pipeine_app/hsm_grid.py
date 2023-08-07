from pathlib import Path
from datetime import datetime as dt

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from dash import (callback, Input, Output, State, dcc, html, ALL, ctx, Patch,
                  clientside_callback)


def extract_rows_from_data(groupKeys, hsm_path):
    response = []
    current_path = Path(*groupKeys) if groupKeys else Path(hsm_path)
    if current_path.is_dir():
        for entry in current_path.iterdir():
            if entry.is_file() and entry.suffix == ".rtdc":
                modified_time = dt.fromtimestamp(
                    entry.stat().st_mtime).strftime("%d-%b-%Y %I.%M %p")
                response.append({
                    "group": entry.is_dir(),
                    "name": entry.name,
                    "path": str(entry),  # Convert Path object to a string
                    "modified_time": modified_time
                })
            elif entry.is_dir():
                modified_time = dt.fromtimestamp(
                    entry.stat().st_mtime).strftime("%d-%b-%Y %I.%M %p")
                response.append({
                    "group": entry.is_dir(),
                    "name": entry.name,
                    "path": str(entry),  # Convert Path object to a string
                    "modified_time": modified_time
                })
    return response


def create_hsm_grid():
    return html.Div([
        dcc.Store(id="store_input_paths", data=[]),
        dag.AgGrid(
            id="hsm_grid",
            className="ag-theme-alpine-dark",
            columnDefs=[
                {"field": "modified_time", "hide": False},
            ],
            style={"height": 500, "width": "100%"},
            defaultColDef={
                "flex": 1,
                "sortable": True,
                "filter": True
            },
            dashGridOptions={
                "autoGroupColumnDef": {
                    "field": "name",
                    "cellRendererParams": {
                        "suppressCount": True,
                        "checkbox": True
                    },
                },
                "treeData": True,
                "rowSelection": "multiple",
                "groupSelectsChildren": True,
                # "groupDefaultExpanded": 0,
                "suppressRowClickSelection": True,
                # "isRowSelectable": {
                #     "function": "params.data ? params.data.path.endsWith('.rtdc') : false",
                # },
                "isServerSideGroupOpenByDefault": {
                    "function": "params ? params.rowNode.level < 0: null"},
                "isServerSideGroup": {
                    "function": "params ? params.group : null"},
                "getServerSideGroupKey": {
                    "function": "params ? params.path : null"}
            },
            enableEnterpriseModules=True,
            rowModelType="serverSide",
        ),
    ])


clientside_callback(
    """async function (id) {
        const delay = ms => new Promise(res => setTimeout(res, ms));
        const updateData = (grid) => {
          var datasource = createServerSideDatasource();
          grid.setServerSideDatasource(datasource);
        };
        var grid;
            try {
                grid = dash_ag_grid.getApi(id)
            } catch {}
            count = 0
            while (!grid) {
                await delay(200)
                try {
                    grid = dash_ag_grid.getApi(id)
                } catch {}
                count++
                if (count > 20) {
                    break;
                }
            }
            if (grid) {
                updateData(grid)
            }
        return window.dash_clientside.no_update
    }""",
    Output("hsm_grid", "id"), Input("hsm_grid", "id")
)


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
    Output("upload_show", "children"),
    Output("num_files", "children"),
    Input("hsm_grid", "selectedRows"),
    Input("store_input_paths", "data"),
)
def display_selected_paths(selected_rows, stored_input):
    original_paths = [] + stored_input
    if selected_rows:
        # Get the list of user selected hsm paths
        selected_paths = [s["path"] for s in selected_rows if
                          ".rtdc" in s["path"]]
        original_paths = original_paths + selected_paths
    return convert_paths_to_buttons(original_paths), len(original_paths)


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
            if all(i in ctx.triggered_id.index for i in
                   selected_rows[x]["path"]):
                del selects[x]
        return selects
    raise PreventUpdate


@callback(
    Output("hsm_grid", "dashGridOptions"),
    Input("grid_filter", "value"),
    State("hsm_grid", "dashGridOptions"),
)
def update_filter(filter_value, grid_options):
    grid_options["quickFilterText"] = filter_value
    return grid_options
