from pathlib import Path
import pickle

from dash import callback, dcc, html, Input, Output, State
from dash import callback_context as cc
from dash.exceptions import PreventUpdate
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
from dash_iconify import DashIconify
import dash_mantine_components as dmc

from .common import hover_card, line_breaks

hsm_cached_dir = Path(__file__).parents[2] / "resources" / "gd2_drive.pkl"


def load_drive_data():
    """Load pickled drive saved in resources dir"""
    if hsm_cached_dir.exists():
        with open(hsm_cached_dir, "rb") as file:
            return pickle.load(file)
    else:
        return None


def create_gd2_grid():
    """Creates the GuckDivision2 file explorer grid"""
    return html.Div(
        [
            dcc.Store(id="cache_gd2_files", data=[]),

            dmc.Group(
                children=[
                    dmc.Text("Select GuckDivision2 file/s:", size="md"),
                    hover_card(
                        target=DashIconify(
                            icon="mage:message-question-mark-round-fill",
                            color="yellow", width=22
                        ),
                        notes="NOTE: The GuckDivision2 drive gets updated "
                              "every one hour. If you do not find your "
                              "dataset in the below grid, please comeback "
                              "after one hour."
                    )
                ],
                spacing=5
            ),
            line_breaks(times=1),
            dmc.TextInput(
                id="grid_filter",
                style={"width": 500, "color": "white"},
                placeholder="Search dataset name with a keyword",
                icon=DashIconify(icon="tabler:search", width=22),
                size="md"
            ),
            dag.AgGrid(
                id="guck_grid",
                className="ag-theme-alpine-dark",
                columnDefs=[
                    {"field": "size", "width": 50, "maxWidth": 200},
                    {"field": "dateModified", "width": 50, "maxWidth": 300},
                ],
                defaultColDef={
                    "flex": 1,
                    "sortable": True,
                    "resizable": True,
                    "filter": True
                },
                dashGridOptions={
                    "autoGroupColumnDef": {
                        "headerName": "GuckDivision2 Drive",
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
                        "loadingMessage": "GuckDivision2 drive is being "
                                          "updated...",
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
                enableEnterpriseModules=True,
                style={"height": 600},
                # getRowId="params.data.filepath",
            )
        ]
    )


def create_show_grid(comp_id):
    """Create show grid to display user selected files for final refining"""
    show_button = dbc.Button(
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
        style={"width": "70%", "height": 400},
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

    return dmc.Stack(
        children=[show_button, show_grid],
        align="center",
        spacing=1
    )


@callback(
    Output("guck_grid", "rowData"),
    Input("pipeline_accord", "active_item"),
)
def load_gd2_grid_data(pipeline_active_accord):
    """Show GuckDivision2 grid only when user clicks on `Data to Process` 
    accord"""
    if pipeline_active_accord == "guck_accord":
        return load_drive_data()
    return None


@callback(
    Output("show_grid", "rowData"),
    Output("show_grid", "selectedRows"),
    Input("cache_gd2_files", "data"),
    prevent_initial_call=True
)
def update_show_grid_data(gd2_files):
    """Collect the user-selected data files and send them to `show_grid`"""
    # Convert list of strings into ag grid rowdata
    rowdata = [{"filepath": i} for i in gd2_files]
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
    return True


@callback(
    Output("cache_gd2_files", "data"),
    Input("guck_grid", "selectedRows"),
    State("cache_gd2_files", "data"),
    prevent_initial_call=True
)
def cache_user_given_gd2_files(gd2_selection, cached_files):
    """Collects the user selected hsm files and cache them"""
    if gd2_selection:
        gd2_files = ["/".join(s["filepath"]) for s in gd2_selection]
        # Convert list of strings into ag grid rowdata
        for hfile in gd2_files:
            if hfile not in cached_files:
                cached_files.append(hfile)
        return cached_files
    raise PreventUpdate


@callback(
    Output("guck_grid", "dashGridOptions"),
    Input("grid_filter", "value"),
    State("guck_grid", "dashGridOptions"),
    prevent_initial_call=True
)
def update_filter(filter_value, grid_options):
    """Filter grid rows based on filter value"""
    grid_options["quickFilterText"] = filter_value
    return grid_options
