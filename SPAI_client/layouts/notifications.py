from dash import html
import dash_bootstrap_components as dbc
from datetime import datetime
from utils.supabase_client import supabase

def get_recent_games(limit=5):
    """Fetch recently added games from Supabase"""
    try:
        response = supabase.table('games')\
            .select('id, home_team, away_team, match_date, status')\
            .eq('status', 'processed')\
            .order('created_at', desc=True)\
            .limit(limit)\
            .execute()
        
        games = response.data
        notifications = []
        
        for game in games:
            # Format the date
            date = datetime.strptime(game['match_date'], '%Y-%m-%d')
            formatted_date = date.strftime('%b %d, %Y')
            
            notifications.append({
                "id": game['id'],
                "type": "new_analysis",
                "title": "New Game Analysis Available",
                "message": f"{game['home_team']} vs {game['away_team']} ({formatted_date})",
                "timestamp": "New",
                "read": False
            })
            
        return notifications
        
    except Exception as e:
        print(f"Error fetching recent games: {str(e)}")
        return []

def create_notifications_layout():
    # Fetch real notifications from database
    notifications = get_recent_games()

    return html.Div([
        dbc.Container([
            # Header
            html.Div([
                html.H1("New Games", className="mb-4"),
                dbc.Button(
                    "Mark All as Read",
                    color="primary",
                    className="float-end"
                )
            ], className="d-flex justify-content-between align-items-center mb-4"),

            # Notifications List
            html.Div([
                dbc.Card([
                    dbc.CardBody([
                        html.Div([
                            # Game Icon
                            html.I(className="fas fa-futbol me-3"),
                            # Notification Content
                            html.Div([
                                html.H5(n["title"], className="notification-title"),
                                html.P(n["message"], className="notification-message mb-1"),
                                html.Small(n["timestamp"], className="text-muted")
                            ], className="flex-grow-1"),
                            # View Button
                            dbc.Button(
                                "View Analysis",
                                color="primary",
                                size="sm",
                                href=f"/game/{n['id']}"
                            )
                        ], className="d-flex align-items-center justify-content-between")
                    ])
                ], className=f"notification-card {'unread' if not n['read'] else ''} mb-3")
                for n in notifications
            ], className="notifications-list"),
            
            # Empty State
            html.Div(
                "No new games available",
                className="text-center text-muted p-5" if not notifications else "d-none"
            )
        ])
    ], className="notifications-page")