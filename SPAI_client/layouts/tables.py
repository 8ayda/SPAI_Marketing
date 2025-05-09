from dash import html, dash_table
import pandas as pd
from utils.supabase_client import supabase

def fetch_game_data(game_id):
    """Fetch game-specific data from Supabase"""
    try:
        # Get game info first
        game = supabase.table('games')\
            .select('home_team, away_team, match_date, competition')\
            .eq('id', game_id)\
            .single()\
            .execute()
        
        # Get logo metrics for the specific game
        metrics = supabase.table('logo_metrics')\
            .select('''
                logo_name,
                sponsorship_value,
                visibility_time,
                appearances
            ''')\
            .eq('game_id', game_id)\
            .execute()
        
        # Convert to DataFrame
        df = pd.DataFrame(metrics.data)
        
        # Rename columns
        df.columns = [
            'Logo',
            'Value ($)',
            'Screen Time (s)',
            'Appearances'
        ]
        
        # Add totals row
        totals = df.sum(numeric_only=True)
        totals['Logo'] = 'Total'
        df = pd.concat([df, pd.DataFrame([totals])], ignore_index=True)
        
        # Ensure specific logo order
        logo_order = ['spotify_logo', 'nike_logo', 'AMBILIGHTtv_logo', 'UNHCR_logo', 'Total']
        df['order'] = df['Logo'].map({name: i for i, name in enumerate(logo_order)})
        df = df.sort_values('order').drop('order', axis=1)
        
        # Format numeric columns
        df['Value ($)'] = df['Value ($)'].round(2)
        df['Screen Time (s)'] = df['Screen Time (s)'].round(1)
        df['Appearances'] = df['Appearances'].astype(int)
        
        return df, game.data
    except Exception as e:
        print(f"Error fetching game data: {str(e)}")
        return pd.DataFrame(), None

def fetch_season_summary():
    """Fetch and aggregate season data from Supabase"""
    try:
        # Get all completed games
        games = supabase.table('games')\
            .select('id, home_team, away_team, competition')\
            .eq('status', 'processed')\
            .execute()
        
        # Get all logo metrics
        metrics = supabase.table('logo_metrics')\
            .select('game_id, logo_name, visibility_time, appearances, sponsorship_value')\
            .execute()
        
        # Convert to DataFrame
        df = pd.DataFrame(metrics.data)
        
        # Calculate season totals by logo
        summary = df.groupby('logo_name').agg({
            'sponsorship_value': 'sum',
            'visibility_time': 'sum',
            'appearances': 'sum'
        }).reset_index()
        
        # Rename columns
        summary.columns = [
            'Logo',
            'Total Value ($)',
            'Total Screen Time (s)',
            'Total Appearances'
        ]
        
        # Add totals row
        totals = summary.sum(numeric_only=True)
        totals['Logo'] = 'Total'
        summary = pd.concat([summary, pd.DataFrame([totals])], ignore_index=True)
        
        # Ensure specific logo order
        logo_order = ['spotify_logo', 'nike_logo', 'AMBILIGHTtv_logo', 'UNHCR_logo', 'Total']
        summary['order'] = summary['Logo'].map({name: i for i, name in enumerate(logo_order)})
        summary = summary.sort_values('order').drop('order', axis=1)
        
        return summary, len(games.data)
    except Exception as e:
        print(f"Error fetching season summary: {str(e)}")
        return pd.DataFrame(), 0

def create_tables_layout(game_id=None):
    # Fetch season summary data first
    season_data, total_games = fetch_season_summary()
    
    content = [
        html.H1("Sponsorship Analysis", className="mb-4")
    ]
    
    # Only fetch and show game data if game_id is provided
    if game_id:
        game_data, game_info = fetch_game_data(game_id)
        if game_info:
            content.extend([
                # Game-Specific Table
                html.Div([
                    html.H2([
                        f"{game_info['home_team']} vs {game_info['away_team']}",
                        html.Small(
                            f" ({game_info['competition']})",
                            className="text-muted ms-2"
                        )
                    ], className="mb-3"),
                    
                    dash_table.DataTable(
                        data=game_data.to_dict("records"),
                        columns=[{
                            "name": col,
                            "id": col,
                            "type": "numeric" if col != "Logo" else "text",
                            "format": {
                                "specifier": ",.0f" if "Appearances" in col
                                else ",.2f" if "Value ($)" in col
                                else ",.1f"
                            } if col != "Logo" else None
                        } for col in game_data.columns],
                        style_table={"overflowX": "auto"},
                        style_cell={
                            "textAlign": "left",
                            "padding": "12px",
                            "minWidth": "120px"
                        },
                        style_header={
                            "backgroundColor": "#f8f9fa",
                            "fontWeight": "bold",
                            "border": "1px solid #dee2e6"
                        },
                        style_data={
                            "backgroundColor": "white",
                            "border": "1px solid #dee2e6"
                        },
                        style_cell_conditional=[
                            {'if': {'column_id': 'Logo'},
                             'width': '180px',
                             'textAlign': 'left'}
                        ] + [
                            {'if': {'column_id': col},
                             'textAlign': 'right'}
                            for col in game_data.columns 
                            if col != 'Logo'
                        ],
                        style_data_conditional=[{
                            'if': {'filter_query': '{Logo} = "Total"'},
                            'backgroundColor': '#f8f9fa',
                            'fontWeight': 'bold'
                        }]
                    )
                ], className="mb-5"),
                html.Hr(className="my-4"),
            ])
    
    # Add Season Summary Table
    content.extend([
        html.Div([
            html.H2([
                "Season Summary ",
                html.Small(
                    f"({total_games} games)",
                    className="text-muted"
                )
            ], className="mb-3"),
            
            dash_table.DataTable(
                data=season_data.to_dict("records"),
                columns=[{
                    "name": col,
                    "id": col,
                    "type": "numeric" if col != "Logo" else "text",
                    "format": {
                        "specifier": ",.0f" if "Appearances" in col
                        else ",.2f" if "Total Value ($)" in col
                        else ",.1f"
                    } if col != "Logo" else None
                } for col in season_data.columns],
                style_table={"overflowX": "auto"},
                style_cell={"textAlign": "left", "padding": "12px"},
                style_header={
                    "backgroundColor": "#f8f9fa",
                    "fontWeight": "bold",
                    "border": "1px solid #dee2e6"
                },
                style_data={
                    "backgroundColor": "white",
                    "border": "1px solid #dee2e6"
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'Logo'},
                     'width': '180px',
                     'textAlign': 'left'}
                ] + [
                    {'if': {'column_id': col},
                     'textAlign': 'right'}
                    for col in season_data.columns 
                    if col != 'Logo'
                ],
                style_data_conditional=[{
                    'if': {'filter_query': '{Logo} = "Total"'},
                    'backgroundColor': '#f8f9fa',
                    'fontWeight': 'bold'
                }]
            )
        ])
    ])
    
    return html.Div(content)