import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output
from layouts.upload_page import create_upload_page
from layouts.admin_dashboard import create_admin_dashboard
from layouts.contact_messages import create_contact_messages_page

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True
)

# Define the navigation bar
navbar = dbc.NavbarSimple(
    brand=html.Div([
        html.Img(
            src="/assets/images/SPAI_logo.png",
            height="70px",
            className="me-2"
        ),
        "SPAI"
    ], className="d-flex align-items-center h3 mb-0"),
    brand_href="/",
    color="primary",
    dark=True,
    className="shadow-sm",
    children=[
        dbc.NavItem(dbc.NavLink([
            html.I(className="fas fa-chart-line me-2"), 
            "Dashboard"
        ], href="/dashboard")),
        dbc.NavItem(dbc.NavLink([
            html.I(className="fas fa-upload me-2"), 
            "Upload Game"
        ], href="/upload")),
        dbc.NavItem(dbc.NavLink([
            html.I(className="fas fa-envelope me-2"), 
            "Messages"
        ], href="/messages"))
    ]
)

# Define the layout with a placeholder for pages
app.layout = html.Div([
    dcc.Location(id="url", refresh=False),
    navbar,
    html.Div(id="page-content", className="mt-4")
])

# Define the callback to handle page navigation
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def display_page(pathname):
    if pathname == "/dashboard":
        return create_admin_dashboard()
    elif pathname == "/upload":
        return create_upload_page()
    elif pathname == "/messages":
        return create_contact_messages_page()
    else:
        return html.Div([
            html.H3("Welcome to the Admin Dashboard!", className="text-center mt-4")
        ])

# Import callbacks
from layouts.upload_page import handle_upload

if __name__ == "__main__":
    app.run(debug=True)