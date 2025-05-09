from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
from config.supabase_client import supabase
import logging

# Configure logging
logger = logging.getLogger(__name__)

def create_admin_dashboard():
    # Fetch stats from Supabase
    response = supabase.table('games').select("*").execute()
    games = response.data if response.data else []

    total_games = len(games)
    pending_games = len([game for game in games if game['status'] == 'pending'])
    processed_games = len([game for game in games if game['status'] == 'processed'])

    return html.Div([
        dbc.Container([
            html.H1("SPAI Admin Dashboard", className="text-center my-4"),
            
            # Stats Cards
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Total Games"),
                            html.H2(total_games, className="text-primary"),
                        ])
                    ], className="mb-4 shadow-sm")
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Pending Games"),
                            html.H2(pending_games, className="text-warning"),
                        ])
                    ], className="mb-4 shadow-sm")
                ], md=4),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H4("Processed Games"),
                            html.H2(processed_games, className="text-success"),
                        ])
                    ], className="mb-4 shadow-sm")
                ], md=4),
            ]),
            
            # Games tables container
            dbc.Row([
                dbc.Col([
                    dbc.Button([
                        html.I(className="fas fa-sync-alt me-2"),
                        "Refresh"
                    ], id="refresh-button", color="primary", className="mb-3"),
                    html.Div(id="games-table", className="mt-3"),
                    dcc.Interval(id='auto-refresh', interval=30000)  # 30 seconds
                ])
            ])
        ])
    ])

@callback(
    Output("games-table", "children"),
    [Input("refresh-button", "n_clicks"),
     Input("auto-refresh", "n_intervals")]
)
def update_games_table(n_clicks, n_intervals):
    try:
        response = supabase.table('games').select("*").order('match_date', desc=True).execute()
        games = response.data

        if not games:
            return html.Div("No games found", className="text-center text-muted")
        
        return create_all_games_table(games)

    except Exception as e:
        logger.error(f"Failed to fetch games: {str(e)}")
        return html.Div(f"Error loading games: {str(e)}", className="text-danger text-center")

def create_all_games_table(games):
    """Create a standard table with all games"""
    return dbc.Table([
        html.Thead([
            html.Tr([
                html.Th("Competition", className="text-center text-dark"),
                html.Th("Teams", className="text-center text-dark"),
                html.Th("Match Date", className="text-center text-dark"),
                html.Th("Status", className="text-center text-dark")
            ], style={"backgroundColor": "#f8f9fa"})
        ]),
        html.Tbody([
            html.Tr([
                html.Td(
                    game['competition'] or "-",
                    className="text-center align-middle"
                ),
                html.Td(
                    f"{game['home_team']} vs {game['away_team']}", 
                    className="text-center align-middle fw-bold"
                ),
                html.Td(
                    game['match_date'].split('T')[0] if game['match_date'] else "-", 
                    className="text-center align-middle"
                ),
                html.Td([
                    dbc.Badge(
                        game['status'],
                        color="success" if game['status'] == "processed"
                        else "warning" if game['status'] == "processing" 
                        else "primary",
                        className="px-3 py-2"
                    )
                ], className="text-center align-middle")
            ], className="align-middle") for game in games
        ])
    ], bordered=True, hover=True, responsive=True, className="shadow-sm")