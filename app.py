import dash
import dash_bootstrap_components as dbc
import dash_bootstrap_templates as dbt
from dash import Input, Output, dcc, html

from .components import groupby_columns, dropdown_menu_comp, paragraph_comp
from .hpc_pipeine_app import main_layout, simple_request, advanced_request
from .viscosity_calculator_app import viscal_app

url_theme1 = dbc.themes.SKETCHY
url_theme2 = dbc.themes.DARKLY

url_theme = url_theme2

dbc_css = ("https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap"
           "-templates@V1.0.1/dbc.min.css")

project_repo_url = "https://gitlab.gwdg.de/blood_data_analysis/" \
                   "hpc_pipeline_dashboard"
gitlab_logo_url = "https://about.gitlab.com/images/press" \
                  "/logo/png/gitlab-icon-rgb.png"

app = dash.Dash(
    assets_folder="assets",
    external_stylesheets=[dbc.themes.DARKLY, dbc_css],
    suppress_callback_exceptions=True,
    # these meta_tags ensure content is scaled correctly on different devices
    # see: https://www.w3schools.com/css/css_rwd_viewport.asp for more
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"}
    ])


def wrong_page(pathname):
    return html.Div(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ],
        className="p-3 bg-light rounded-3"
    )


def sidebar_menu():
    return html.Div([
        groupby_columns([
            html.H2("Guck Lab"),
            html.Br(),
            dbt.ThemeSwitchAIO(aio_id="theme",
                               themes=[url_theme, url_theme]),
            html.Br()
        ]),

        paragraph_comp(text="App Description"),

        groupby_columns([
            html.Br(),
            dropdown_menu_comp(name="Sign in / Sign up",
                               components=[
                                   dbc.NavLink("Sign in", href="/signin",
                                               id="signin_active"),
                                   dbc.NavLink("Sign up", href="/signup",
                                               id="signup_active")
                               ]),
            html.Br(),
            html.Br(),
        ]),

        groupby_columns([
            html.Br(),
            dbc.Nav([
                dbc.NavLink("Home", href="/", id="home_active"),
                dbc.NavLink("HPC Pipelines", href="/hpc_pipelines",
                            id="hpc_pipeline_active"),
                dbc.NavLink("Viscosity Calculator", href="/viscal",
                            id="viscal_active"),
            ],
                vertical=True,
                pills=True,
            ),
            html.Br(),
        ]),

        html.Div([
            html.Br(), html.Br(), html.Br(), html.Br(), html.Br(),
            html.A([
                html.Img(src=gitlab_logo_url, height=50),
                " Source code"
            ],
                href=project_repo_url,
                target='_blank',
                style={"text-decoration": "none"}
            )
        ])
    ],
        id="sidebar"
    )


def main_content_block():
    return html.Div(
        id="page-content",
        style={"align-items": "center"}
    )


# Build the layout of the app
app.layout = html.Div([
    dcc.Location(id="url"),
    sidebar_menu(),
    main_content_block(),
])


@app.callback([Output("page-content", "children"),
               Output("home_active", "active"),
               Output("signin_active", "active"),
               Output("signup_active", "active"),
               Output("hpc_pipeline_active", "active"),
               Output("viscal_active", "active")],
              Input("url", "pathname"),
              )
def render_page_content(pathname):
    # template = template_theme1 if toggle else template_theme2
    if pathname == "/":
        return [html.P("Oh cool, this is page 2!"),
                True, False, False, False, False]
    elif pathname == "/signin":
        return [html.P("This is signin page"),
                False, True, False, False, False]
    elif pathname == "/signup":
        return [html.P("This is signup page"),
                False, False, True, False, False]
    elif pathname == "/hpc_pipelines":
        return [main_layout(),
                False, False, False, True, False]
    elif pathname == "/viscal":
        return [viscal_app(),
                False, False, False, False, True]
    elif pathname == "/hpc_pipelines/simple":
        return [simple_request(),
                False, False, False, True, False]
    elif pathname == "/hpc_pipelines/advanced":
        return [advanced_request(),
                False, False, False, True, False]
    # Return a 404 message, if user tries to reach undefined page
    return wrong_page(pathname)
