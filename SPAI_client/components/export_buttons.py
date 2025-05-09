import dash_bootstrap_components as dbc
from dash import html

def create_export_buttons():
    return html.Div([
        dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem([
                    html.I(className="fas fa-file-csv me-2"),
                    "CSV"
                ], id="export-csv-btn", n_clicks=0),
                
                dbc.DropdownMenuItem([
                    html.I(className="fas fa-file-code me-2"),
                    "JSON"
                ], id="export-json-btn", n_clicks=0),
            ],
            label=[
                html.I(className="fas fa-download me-2"),
                "Export Data As..."
            ],
            color="primary",
            className="export-dropdown"  
        )
    ])