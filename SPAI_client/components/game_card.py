import dash_bootstrap_components as dbc
from dash import html
from datetime import datetime
from utils.supabase_client import supabase

def fetch_processed_games():
    """Fetch all processed games from Supabase"""
    try:
        response = supabase.table('games')\
            .select('id, home_team, away_team, match_date, competition, thumbnail')\
            .eq('status', 'processed')\
            .execute()
        return response.data
    except Exception as e:
        print(f"Error fetching games: {str(e)}")
        return []

def format_date(date_str):
    """Format date string to a readable format"""
    try:
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime('%B %d, %Y')
    except:
        return date_str

def create_game_card(game):
    """Create a card component for a game"""
    # Default image in case thumbnail is not available
    thumbnail_url = game.get('thumbnail') or "https://via.placeholder.com/300x180?text=No+Image"
    
    return dbc.Card([
        # Add thumbnail image at the top of the card
        dbc.CardImg(src=thumbnail_url, top=True, 
                   style={"height": "180px", "objectFit": "cover"}),
        dbc.CardBody([
            # Competition badge
            html.Div(
                game['competition'],
                className="badge bg-primary mb-2",
                style={"fontSize": "12px"}
            ),
            
            # Teams
            html.H4(
                f"{game['home_team']} vs {game['away_team']}", 
                className="card-title",
                style={"fontSize": "18px", "fontWeight": "bold"}
            ),
            
            # Match date
            html.P(
                f"Match Date: {format_date(game['match_date'])}", 
                className="card-text text-muted",
                style={"fontSize": "14px"}
            ),
            
            # View details button
            dbc.Button(
                [
                    html.I(className="fas fa-chart-bar me-2"),
                    "View Analysis"
                ],
                href=f"/game/{game['id']}",
                color="primary",
                className="w-100 mt-3"
            )
        ])
    ], 
    className="h-100 shadow-sm",
    style={
        "border": "1px solid #eee",
        "borderRadius": "8px",
        "transition": "transform 0.2s ease, box-shadow 0.2s ease",
        "cursor": "pointer",
        "hover": {
            "transform": "translateY(-5px)",
            "boxShadow": "0 4px 12px rgba(0,0,0,0.1)"
        }
    })