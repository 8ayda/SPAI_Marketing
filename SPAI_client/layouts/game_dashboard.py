# layouts/game_dashboard.py
import dash_bootstrap_components as dbc
from dash import html, dcc
import plotly.express as px
import pandas as pd
import numpy as np
from components.export_buttons import create_export_buttons
from utils.supabase_client import supabase
import json

def load_game_data(game_id):
    try:
        # Fetch game info
        game = supabase.table('games')\
            .select('*')\
            .eq('id', game_id)\
            .single()\
            .execute()

        # Format the date to remove time component
        match_date = game.data['match_date']
        if match_date and 'T' in match_date:
            formatted_date = match_date.split('T')[0]  # Extract just the date part
        else:
            formatted_date = match_date
            
        # Convert YYYY-MM-DD to a more readable format
        try:
            from datetime import datetime
            date_obj = datetime.strptime(formatted_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%B %d, %Y')  # e.g., "March 31, 2025"
        except:
            pass

        # Fetch logo metrics - using the metrics calculated by the processing script
        metrics = supabase.table('logo_metrics')\
            .select('''
                logo_name,
                visibility_time,
                appearances,
                unique_appearances,
                avg_sequence_duration,
                avg_area_percentage,
                avg_position_score,
                dominant_position,
                dominant_size,
                center_percentage,
                edge_percentage,
                corner_percentage,
                sponsorship_value
            ''')\
            .eq('game_id', game_id)\
            .execute()

        # Fetch timeline data for visibility chart
        timeline = supabase.table('logo_timeline')\
            .select('timestamp, logo_name, sponsor_score')\
            .eq('game_id', game_id)\
            .order('timestamp')\
            .execute()

        # Fetch heatmap data
        heatmaps = supabase.table('logo_heatmaps')\
            .select('logo_name, positions')\
            .eq('game_id', game_id)\
            .execute()

        # Process metrics for value cards
        value_data = [
            {
                'logo': metric['logo_name'],
                'estimated_value': metric['sponsorship_value'],
                'screen_time': metric['visibility_time'],
                'appearances': metric['appearances'],
                'position_score': metric['avg_position_score'],
                'area_percentage': metric['avg_area_percentage'],
                'dominant_position': metric['dominant_position'],
                'center_percentage': metric['center_percentage']
            }
            for metric in metrics.data
        ]

        # Process timeline data for visibility chart
        # The data structure is already optimized in the timeline table
        visibility_data = [
            {
                'timestamp': entry['timestamp'],
                'logo': entry['logo_name'],
                'visibility_score': entry['sponsor_score']
            }
            for entry in timeline.data
        ]

        # Process heatmap data - properly handle positions JSON
        heatmap_data = []
        for hm in heatmaps.data:
            # Check if positions is already a list or needs parsing
            positions = hm['positions']
            if isinstance(positions, str):
                positions = json.loads(positions)
            
            for pos in positions:
                heatmap_data.append({
                    'x': pos['x'],
                    'y': pos['y'],
                    'logo': hm['logo_name'],
                    'score': pos.get('score', 1.0)  # Use score if available
                })

        return {
            'game_info': {
                'home_team': game.data['home_team'],
                'away_team': game.data['away_team'],
                'date': formatted_date,
                'competition': game.data['competition']
            },
            'visibility_data': pd.DataFrame(visibility_data),
            'heatmap_data': pd.DataFrame(heatmap_data),
            'value_data': pd.DataFrame(value_data)
        }
        
    except Exception as e:
        print(f"Error loading game data: {str(e)}")
        return None


def create_game_card(game):
    return dbc.Card([
        dbc.CardImg(
            src=game['thumbnail'],  
            top=True,
            style={
                "height": "200px",
                "objectFit": "cover",
                "borderTopLeftRadius": "var(--radius-lg)",
                "borderTopRightRadius": "var(--radius-lg)"
            }
        ),
        dbc.CardBody([
            html.H5(f"{game['home_team']} vs {game['away_team']}", className="card-title"),
            html.P(f"Date: {game['date']}", className="card-text"),
            dbc.Button("View Analysis", href=f"/game/{game['game_id']}", color="primary")
        ])
    ], className="game-card")

def get_logo_image_mapping():
    """Map database logo names to image paths"""
    return {
        'spotify_logo': '/assets/images/spotify_logo.png',
        'nike_logo': '/assets/images/nike_logo.png',
        'AMBILIGHTtv_logo': '/assets/images/AMBILIGHTtv_logo.png',
        'UNHCR_logo': '/assets/images/UNHCR_logo.png'
    }

def create_game_dashboard(game_id):
    data = load_game_data(game_id)
    
    # Return loading state if no data
    if data is None:
        return html.Div([
            html.H3("Loading game data...", className="text-muted text-center my-5"),
            dbc.Spinner(size="lg", color="primary")
        ])

    # Create header with match details
    header = dbc.Row([
        dbc.Col([
            html.H1(f"{data['game_info']['home_team']} vs {data['game_info']['away_team']}"),
            html.P(f"{data['game_info']['competition']} • {data['game_info']['date']}", 
                  className="text-muted")
        ], width=True),
        dbc.Col([
            create_export_buttons()
        ], width="auto", className="d-flex align-items-center")
    ], className="mb-4 align-items-center")

    # Create value cards with enhanced metrics and specific order
    try:
        value_df = pd.DataFrame(data['value_data'])
        
        # Define card order: Spotify first, AMBILIGHTtv third
        card_order = ['spotify_logo', 'nike_logo', 'AMBILIGHTtv_logo', 'UNHCR_logo']
        
        # Map order position to each logo
        value_df['sort_order'] = value_df['logo'].map({logo: idx for idx, logo in enumerate(card_order)})
        
        # Sort by defined order
        value_df = value_df.sort_values('sort_order').reset_index(drop=True)
        
        # Create sponsor value cards
        value_cards = dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.Img(
                            src=get_logo_image_mapping().get(logo, '/assets/images/default_logo.png'),
                            height="30px",
                            style={"objectFit": "contain"}
                        ),
                        html.H4(f"${value:,.2f}", className="mt-2"),
                        html.P([
                            f"Screen Time: {screen_time}s",
                            html.Br(),
                            f"Appearances: {appearances}",
                            html.Br(),
                            f"Position: {position.capitalize()} ({position_score:.2f})"
                        ], className="text-muted small mb-0")
                    ])
                ], className="value-card h-100")
            ], width=12, md=6, lg=3, className="mb-3")
            for logo, value, screen_time, appearances, position, position_score
            in zip(value_df['logo'], 
                   value_df['estimated_value'],
                   value_df['screen_time'],
                   value_df['appearances'],
                   value_df['dominant_position'],
                   value_df['position_score'])
        ])

    except Exception as e:
        print(f"Error creating value cards: {str(e)}")
        value_cards = html.Div("Error loading sponsor data", className="text-danger")

    # Apply same ordering to the chart data
    try:
        # Also sort the value data for charts to maintain consistency
        for chart_data in [data['value_data']]:
            if not chart_data.empty:
                chart_data['sort_order'] = chart_data['logo'].map({logo: idx for idx, logo in enumerate(card_order)})
                chart_data.sort_values('sort_order', inplace=True)
                chart_data.reset_index(drop=True, inplace=True)
                if 'sort_order' in chart_data.columns:
                    chart_data.drop('sort_order', axis=1, inplace=True)
        
        # Rest of the visualization code remains the same...
    except Exception as e:
        print(f"Error ordering chart data: {str(e)}")
        
    # Create visualization charts
    try:
        # Visibility timeline
        timeline_fig = px.line(
            data['visibility_data'], 
            x='timestamp', 
            y='visibility_score',
            color='logo',
            title='Sponsor Visibility Score Over Time',
            labels={'timestamp': 'Match Time (seconds)', 
                    'visibility_score': 'Visibility Score'}
        )
        timeline_fig.update_layout(
            hovermode='x unified',
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(t=50, b=20, l=20, r=20)
        )
        # Add grid for better visibility
        timeline_fig.update_xaxes(
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(211, 211, 211, 0.5)'
        )
        timeline_fig.update_yaxes(
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(211, 211, 211, 0.5)'
        )

        # Screen time distribution pie chart
        pie_fig = px.pie(
            data['value_data'],
            values='screen_time',
            names='logo',
            title='Share of Screen Time'
        )
        pie_fig.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(t=50, b=20, l=20, r=20)
        )

        # Appearances bar chart
        bar_fig = px.bar(
            data['value_data'],
            x='logo',
            y='appearances',
            color='logo',
            title='Number of Logo Appearances'
        )
        bar_fig.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            showlegend=False,
            margin=dict(t=50, b=20, l=20, r=20)
        )
        # Add grid for better visibility
        bar_fig.update_yaxes(
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(211, 211, 211, 0.5)'
        )

        # Position heatmap
        heatmap_fig = px.density_heatmap(
            data['heatmap_data'],
            x='x', 
            y='y',
            facet_col='logo',
            title='Logo Position Heatmap',
            nbinsx=30,
            nbinsy=17,
            z='score' if 'score' in data['heatmap_data'].columns else None
        )
        
        # Update heatmap layout with screen proportions and grid
        heatmap_fig.update_layout(
            height=500,
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(t=50, b=20, l=20, r=20)
        )

        # Update axes to match screen coordinates with enhanced grid
        heatmap_fig.update_yaxes(
            scaleanchor="x",
            scaleratio=9/16,  # Screen aspect ratio
            range=[1, 0],     # Flip Y axis to match screen coordinates
            gridcolor='rgba(180, 180, 180, 0.7)',
            gridwidth=0.7,
            showgrid=True
        )
        
        heatmap_fig.update_xaxes(
            gridcolor='rgba(180, 180, 180, 0.7)',
            gridwidth=0.7,
            showgrid=True
        )

        # Add position distribution chart
        position_data = data['value_data'][['logo', 'center_percentage']].copy()
        position_data['edge_percentage'] = data['value_data']['center_percentage']
        position_data['corner_percentage'] = 100 - position_data['center_percentage'] - position_data['edge_percentage']
        
        position_data = position_data.melt(
            id_vars=['logo'],
            value_vars=['center_percentage', 'edge_percentage', 'corner_percentage'],
            var_name='position',
            value_name='percentage'
        )
        
        position_fig = px.bar(
            position_data,
            x='logo',
            y='percentage',
            color='position',
            title='Logo Position Distribution',
            labels={'percentage': 'Percentage (%)', 'position': 'Position'}
        )
        position_fig.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            margin=dict(t=50, b=20, l=20, r=20),
            barmode='stack'
        )
        # Add grid for better visibility
        position_fig.update_yaxes(
            showgrid=True,
            gridwidth=0.5,
            gridcolor='rgba(211, 211, 211, 0.5)'
        )

        # Arrange charts in layout
        graphs = [
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=timeline_fig)
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=pie_fig)
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6),
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=bar_fig)
                        ])
                    ], className="shadow-sm")
                ], width=12, lg=6)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=position_fig)
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ], className="mb-4"),
            
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            dcc.Graph(figure=heatmap_fig)
                        ])
                    ], className="shadow-sm")
                ], width=12)
            ], className="mb-4")
        ]
    except Exception as e:
        print(f"Error creating graphs: {str(e)}")
        graphs = [html.Div(f"Error loading visualizations: {str(e)}", className="text-danger p-3")]

    # Return the complete dashboard layout
    return html.Div([
        header,
        value_cards,
        *graphs
    ], className="dashboard-container p-4")