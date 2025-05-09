from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from config.supabase_client import supabase
import logging

logger = logging.getLogger(__name__)

def create_contact_messages_page():
    return html.Div([
        dbc.Container([
            html.H2("Contact Messages", className="text-center my-4"),
            dbc.Row([
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-sync-alt me-2"),
                        "Refresh"
                    ], id="refresh-messages", color="primary", className="mb-3"),
                    html.Div(id="messages-table", className="mt-3"),
                    dcc.Interval(id='message-refresh', interval=30000)  # 30 seconds refresh
                ])
            ])
        ])
    ])

@callback(
    Output("messages-table", "children"),
    [Input("refresh-messages", "n_clicks"),
     Input("message-refresh", "n_intervals")]
)
def update_messages_table(n_clicks, n_intervals):
    try:
        # Fetch messages from Supabase
        response = supabase.table('contact_submissions').select("*").order('created_at', desc=True).execute()
        messages = response.data

        if not messages:
            return html.Div("No messages found", className="text-center text-muted")

        return dbc.Table([
            html.Thead([
                html.Tr([
                    html.Th("Date", className="text-center"),
                    html.Th("Name", className="text-center"),
                    html.Th("Subject", className="text-center"),
                    html.Th("Email", className="text-center"),
                    html.Th("Message", className="text-center"),
                    html.Th("Status", className="text-center")
                ], style={"backgroundColor": "#f8f9fa"})
            ]),
            html.Tbody([
                html.Tr([
                    html.Td(
                        message['created_at'].split('T')[0], 
                        className="text-center align-middle"
                    ),
                    html.Td(
                        message['name'],
                        className="text-center align-middle"
                    ),
                    html.Td(
                        message['subject'],
                        className="text-center align-middle"
                    ),
                    html.Td(
                        message['email'],
                        className="text-center align-middle"
                    ),
                    html.Td(
                        message['message'],
                        className="text-center align-middle"
                    ),
                    html.Td([
                        dbc.Badge(
                            message['status'],
                            color="primary" if message['status'] == "new" else "success",
                            className="px-3 py-2"
                        )
                    ], className="text-center align-middle")
                ]) for message in messages
            ])
        ], bordered=True, hover=True, responsive=True, className="shadow-sm")

    except Exception as e:
        logger.error(f"Failed to fetch messages: {str(e)}")
        return html.Div(f"Error loading messages: {str(e)}", className="text-danger")