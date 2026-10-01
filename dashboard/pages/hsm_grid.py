import pickle
import re
from datetime import datetime
from pathlib import Path

import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_mantine_components as dmc
from dash import Input, Output, State, callback, dcc, html
from dash import callback_context as cc
from dash.exceptions import PreventUpdate
from dash_iconify import DashIconify

from .common_components import hover_card, line_breaks

HSM_DATA_FILE = Path(__file__).parents[2] / "resources" / "hsm_drive.pkl"

# Optional time (HH MM [SS]) that may follow a date in a file name
_TIME = (
    r"(?:[-_T ]?(?P<H>[01]\d|2[0-3])[-_.:h]?(?P<M>[0-5]\d)"
    r"(?:[-_.:m]?(?P<S>[0-5]\d))?)?"
)
# Supported date formats in file names: YYYY-MM-DD, YYYY_MM_DD, YYYY.MM.DD,
# YYYYMMDD, and DD-MM-YYYY / DD.MM.YYYY / DD_MM_YYYY
DATE_PATTERNS = [
    re.compile(
        r"(?<!\d)(?P<y>(?:19|20)\d{2})(?P<sep>[-_.]?)(?P<m>0[1-9]|1[0-2])"
        r"(?P=sep)(?P<d>0[1-9]|[12]\d|3[01])" + _TIME + r"(?!\d)"
    ),
    re.compile(
        r"(?<!\d)(?P<d>0[1-9]|[12]\d|3[01])(?P<sep>[-_.])"
        r"(?P<m>0[1-9]|1[0-2])(?P=sep)(?P<y>(?:19|20)\d{2})" + _TIME + r"(?!\d)"
    ),
]


def extract_date_from_path(filepath):
    """Extract the date (and time, if present) from a file path. The file
    name is searched first, then the rest of the path (e.g. dated folders).
    Returns None when no valid date is found."""
    for text in (filepath.rsplit("/", 1)[-1], filepath):
        for pattern in DATE_PATTERNS:
            for match in pattern.finditer(text):
                try:
                    return datetime(
                        int(match["y"]),
                        int(match["m"]),
                        int(match["d"]),
                        int(match["H"] or 0),
                        int(match["M"] or 0),
                        int(match["S"] or 0),
                    )
                except ValueError:
                    # e.g. 31st of February
                    continue
    return None


def sort_rows_by_date(rows, descending=False):
    """Sort grid rows by the date in their file path. Rows without a date
    are kept at the end in their original order"""
    dated, undated = [], []
    for row in rows:
        date = extract_date_from_path(row["filepath"])
        (dated if date else undated).append((date, row))
    dated.sort(key=lambda x: x[0], reverse=descending)
    return [row for _, row in dated] + [row for _, row in undated]


def load_hsm_data():
    """Load rtdc file paths from pickled HSMFS drive"""
    if HSM_DATA_FILE.exists():
        with open(HSM_DATA_FILE, "rb") as file:
            return pickle.load(file)
    else:
        return None


def create_hsm_grid():
    """Creates the HSMFS file explorer grid"""
    return html.Div(
        [
            # Cache component to store selected files (dcor and hsm)
            dcc.Store(id="cache_dcor_files", data=[]),
            dcc.Store(id="cache_hsm_files", data=[]),
            # DCOR heading section
            dmc.Group(
                children=[
                    dmc.Text("Select DCOR-Colab file:", size="md"),
                    hover_card(
                        target=DashIconify(
                            icon="mage:message-question-mark-round-fill",
                            color="yellow",
                            width=22,
                        ),
                        notes="Copy and paste dataset ID / Circle name / "
                        "Collection name from DCOR-Colab and click "
                        "'add button' to add it to the pipeline ",
                    ),
                ],
                spacing=5,
            ),
            dmc.Text(
                "NOTE: HPC Pipeline does not work with DCOR data.",
                size="sm",
                color="red",
            ),
            line_breaks(times=1),
            # DCOR input bar
            dbc.InputGroup(
                [
                    dbc.Select(
                        placeholder="Source",
                        id="dcor_drop_down",
                        options=[
                            {"label": "DCOR-Colab", "value": "DCOR"},
                        ],
                        value="DCOR",
                        style={"width": "20%"},
                        disabled=False,
                    ),
                    dbc.Input(
                        type="text",
                        id="dcor_text_input",
                        placeholder="Enter DVC path or DCOR-colab Id, "
                        "Circle, or Dataset etc...",
                        style={"width": "70%"},
                        class_name="custom-placeholder",
                        disabled=False,
                    ),
                    dbc.Button(
                        "Add",
                        id="dcor_button",
                        color="info",
                        style={"width": "10%"},
                        disabled=False,
                    ),
                ],
                style={"width": "80%"},
            ),
            line_breaks(times=2),
            # HSMS heading and time bagde section
            dmc.Group(
                children=[
                    dmc.Text("Select HSMFS file/s:", size="md"),
                    dmc.Badge(
                        id="hsm_time_badge",
                        variant="outline",
                        size="md",
                        color="red",
                    ),
                    hover_card(
                        target=DashIconify(
                            icon="mage:message-question-mark-round-fill",
                            color="yellow",
                            width=22,
                        ),
                        notes="NOTE: The HSMFS drive gets updated every one "
                        "hour. If you do not find your dataset in the "
                        "below grid, please comeback after one hour.",
                    ),
                ],
                spacing=5,
            ),
            line_breaks(times=1),
            # HSMFS grid filter input
            dmc.TextInput(
                id="grid_filter_text",
                style={"width": 500, "color": "white"},
                placeholder="Search dataset name with a keyword",
                icon=DashIconify(icon="tabler:search", width=22),
                size="md",
            ),
            # HSMFS grid section
            dag.AgGrid(
                id="hsm_grid",
                className="ag-theme-alpine-dark",
                columnDefs=[
                    {"field": "size", "width": 50, "maxWidth": 200},
                    {"field": "dateModified", "width": 50, "maxWidth": 300},
                ],
                defaultColDef={
                    "flex": 1,
                    "sortable": True,
                    "resizable": True,
                    "filter": True,
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
                enableEnterpriseModules=True,
                style={"height": 600},
                # getRowId="params.data.filepath",
            ),
        ]
    )


def create_show_grid(show_grid_id):
    """Create show grid to display user selected files for final refining"""
    # Selected files number indicatir
    show_button = dbc.Button(
        [
            "Selected files:",
            dbc.Badge(
                id="num_files",
                color="danger",
                text_color="dark",
                className="ms-1",
            ),
        ],
        color="info",
        style={"margin-right": "10px"},
    )
    # Sort selected files by the date in their file names
    sort_button = dbc.Button(
        [
            DashIconify(
                id="sort_by_date_icon",
                icon="mdi:sort-calendar-ascending",
                width=20,
                style={"margin-right": "5px"},
            ),
            "Sort by file date",
        ],
        id="sort_by_date_button",
        color="secondary",
        n_clicks=0,
    )
    # Show grid section
    show_grid = dag.AgGrid(
        id=show_grid_id,
        className="ag-theme-alpine-dark",
        columnDefs=[
            {
                "field": "filepath",
                "checkboxSelection": True,
                "headerCheckboxSelection": True,
            }
        ],
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
        children=[
            dmc.Group(children=[show_button, sort_button], spacing=5),
            show_grid,
        ],
        align="center",
        spacing=1,
    )


@callback(
    Output("hsm_grid", "rowData"),
    Output("hsm_time_badge", "children"),
    Input("pipeline_accord", "active_item"),
)
def load_hms_grid_data(pipeline_active_accord):
    """Show HSMFS grid and update time only when user clicks on
    `Data to Process` accord"""
    data = load_hsm_data()
    if pipeline_active_accord == "hsm_accord" and data:
        hsm_grid_data, hsm_time = data["cache_data"], data["update_time"]
        return hsm_grid_data, f"Last Update: {hsm_time}"
    return None, "Last Update: N/A"


@callback(
    Output("show_grid", "rowData"),
    Output("show_grid", "selectedRows"),
    Output("sort_by_date_icon", "icon"),
    Input("cache_dcor_files", "data"),
    Input("cache_hsm_files", "data"),
    Input("sort_by_date_button", "n_clicks"),
    State("show_grid", "selectedRows"),
    prevent_initial_call=True,
)
def update_show_grid_data(dcor_files, hsm_files, sort_clicks, selected_rows):
    """Collect the user-selected data files and send them to `show_grid`.
    Once the sort button is clicked, rows are sorted by the date in their
    file names (oldest first, then toggles to newest first on every click)"""
    # Convert list of strings into ag grid rowdata
    rowdata = [{"filepath": i} for i in (dcor_files + hsm_files)]
    descending = sort_clicks % 2 == 0
    icon = (
        "mdi:sort-calendar-descending"
        if sort_clicks and descending
        else "mdi:sort-calendar-ascending"
    )
    if sort_clicks:
        rowdata = sort_rows_by_date(rowdata, descending=descending)

    button_triggered = cc.triggered[0]["prop_id"].split(".")[0]
    if button_triggered == "sort_by_date_button":
        # Only reorder, keep the user's current (de)selection
        selected = {r["filepath"] for r in (selected_rows or [])}
        return (
            rowdata,
            [r for r in rowdata if r["filepath"] in selected],
            icon,
        )
    return rowdata, rowdata, icon


@callback(
    Output("num_files", "children"),
    Input("show_grid", "selectedRows"),
    prevent_initial_call=True,
)
def display_selected_files_number(show_grid_rows):
    """Display the number of selected files"""
    return len(show_grid_rows)


@callback(
    Output("dcor_button", "disabled"),
    Input("dcor_drop_down", "value"),
    Input("dcor_text_input", "value"),
)
def toggle_dcor_button(drop_value, filename):
    """Activates Add button in DCOR input bar only when the dropdown value
    and DCOR identifier is entered"""
    if drop_value and filename:
        return False
    return True


@callback(
    Output("cache_dcor_files", "data"),
    Output("dcor_drop_down", "value"),
    Output("dcor_text_input", "value"),
    Input("dcor_button", "n_clicks"),
    Input("dcor_drop_down", "value"),
    Input("dcor_text_input", "value"),
    State("cache_dcor_files", "data"),
    prevent_initial_call=True,
)
def cache_user_given_dcor_files(_, drop_input, text_input, cached_files):
    """Collects the user selected dcor files and cache them"""
    button_triggered = cc.triggered[0]["prop_id"].split(".")[0]

    if button_triggered == "dcor_button":
        if text_input and drop_input:
            input_path = f"{drop_input}: {text_input}"
            if input_path not in cached_files:
                cached_files.append(input_path)
            return cached_files, drop_input, None
    raise PreventUpdate


@callback(
    Output("cache_hsm_files", "data"),
    Input("hsm_grid", "selectedRows"),
    State("cache_hsm_files", "data"),
    prevent_initial_call=True,
)
def cache_user_given_hsm_files(hsm_selection, cached_files):
    """Collects the user selected hsm files and cache them"""
    if hsm_selection:
        hsm_files = ["/".join(s["filepath"]) for s in hsm_selection]
        # Convert list of strings into ag grid rowdata
        for hfile in hsm_files:
            if hfile not in cached_files:
                cached_files.append(hfile)
        return cached_files
    raise PreventUpdate


@callback(
    Output("hsm_grid", "dashGridOptions"),
    Input("grid_filter_text", "value"),
    State("hsm_grid", "dashGridOptions"),
    prevent_initial_call=True,
)
def update_filter(filter_value, grid_options):
    """Filter grid rows based on filter value"""
    grid_options["quickFilterText"] = filter_value
    return grid_options
