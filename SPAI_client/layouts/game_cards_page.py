# layouts/home.py
from dash import html
import dash_bootstrap_components as dbc
from components.game_card import create_game_card, fetch_processed_games
from datetime import datetime

def create_game_cards_layout():
    # Fetch processed games from Supabase
    games = fetch_processed_games()
    
    # Sort games by date (newest first)
    sorted_games = sorted(
        games,
        key=lambda game: datetime.fromisoformat(game.get('match_date', '1970-01-01').replace('Z', '+00:00')),
        reverse=True  # Newest first
    )
    
    return html.Div([
        # Header
        html.H2("Match Analysis", className="mb-4"),
        
        # Cards grid
        dbc.Row([
            dbc.Col(
                create_game_card(game),
                xs=12, sm=6, md=4, lg=3,
                className="mb-4"
            ) for game in sorted_games
        ])
    ], className="p-4")