from dash import html
import dash_bootstrap_components as dbc

def create_processing_status(status, progress, logs):
    return dbc.Card(
        dbc.CardBody([
            html.H4("Processing Status"),
            dbc.Progress(value=progress, striped=True, animated=True),
            html.Pre(
                logs,
                style={
                    'maxHeight': '200px',
                    'overflowY': 'scroll',
                    'backgroundColor': '#f8f9fa',
                    'padding': '10px',
                    'marginTop': '10px'
                }
            )
        ])
    )