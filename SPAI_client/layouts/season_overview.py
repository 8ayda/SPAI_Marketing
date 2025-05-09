# layouts/season_overview.py
import dash_bootstrap_components as dbc
from dash import html, dcc, callback, Input, Output, ctx
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from utils.supabase_client import supabase
import numpy as np
from datetime import datetime

def load_season_data():
    """Load and aggregate data from all processed games"""
    try:
        # Get all processed games from Supabase
        games = supabase.table('games')\
            .select('id, home_team, away_team, match_date, competition, thumbnail')\
            .eq('status', 'processed')\
            .execute()

        # Get logo metrics for all games
        metrics = supabase.table('logo_metrics')\
            .select('''
                game_id,
                logo_name,
                visibility_time,
                appearances,
                sponsorship_value,
                avg_area_percentage,
                avg_position_score
            ''')\
            .execute()
        
        # Convert to DataFrames
        df_games = pd.DataFrame(games.data)
        df_metrics = pd.DataFrame(metrics.data)
        
        if df_games.empty or df_metrics.empty:
            return None
            
        # Format dates for better display
        df_games['formatted_date'] = df_games['match_date'].apply(
            lambda d: datetime.fromisoformat(d.replace('Z', '+00:00')).strftime('%b %d, %Y') 
            if isinstance(d, str) else 'Unknown')
            
        # Calculate growth metrics - value per game over time
        if 'match_date' in df_games.columns and not df_games.empty:
            df_games['date_obj'] = pd.to_datetime(df_games['match_date'])
            df_games = df_games.sort_values('date_obj')
            
            # Merge games with metrics
            timeline_data = df_metrics.merge(df_games, left_on='game_id', right_on='id')
            
            # Calculate cumulative metrics for overall growth
            growth_data = timeline_data.groupby(['date_obj', 'formatted_date']).agg({
                'sponsorship_value': 'sum',
                'visibility_time': 'sum',
                'appearances': 'sum'
            }).reset_index().sort_values('date_obj')
            
            growth_data['cumulative_value'] = growth_data['sponsorship_value'].cumsum()
            growth_data['cumulative_time'] = growth_data['visibility_time'].cumsum()
            growth_data['cumulative_appearances'] = growth_data['appearances'].cumsum()
        else:
            growth_data = pd.DataFrame()
            
        # Calculate sponsor leaderboard with more metrics
        sponsor_stats = df_metrics.groupby('logo_name').agg({
            'visibility_time': 'sum',
            'appearances': 'sum',
            'sponsorship_value': 'sum',
            'avg_area_percentage': 'mean',
            'avg_position_score': 'mean',
            'game_id': 'nunique'
        }).reset_index()
        
        # Calculate value per second and appearance metrics
        sponsor_stats['Value Per Second'] = sponsor_stats['sponsorship_value'] / sponsor_stats['visibility_time']
        sponsor_stats['Value Per Appearance'] = sponsor_stats['sponsorship_value'] / sponsor_stats['appearances']
        
        sponsor_stats.columns = [
            'Logo',
            'Total Screen Time',
            'Total Appearances',
            'Total Value',
            'Avg Size',
            'Avg Position',
            'Games Sponsored',
            'Value Per Second',
            'Value Per Appearance'
        ]
        
        # Calculate competition data
        if 'competition' in df_games.columns:
            competition_data = timeline_data.groupby('competition').agg({
                'sponsorship_value': 'sum',
                'visibility_time': 'sum',
                'appearances': 'sum',
                'id': 'nunique'  # Count games per competition
            }).reset_index()
            
            competition_data.columns = [
                'Competition', 'Total Value', 'Total Screen Time', 
                'Total Appearances', 'Games'
            ]
            
            competition_data['Average Value per Game'] = competition_data['Total Value'] / competition_data['Games']
        else:
            competition_data = pd.DataFrame()
        
        # Calculate best matches per sponsor
        best_matches = []
        for logo in df_metrics['logo_name'].unique():
            logo_matches = df_metrics[df_metrics['logo_name'] == logo]\
                .merge(df_games, left_on='game_id', right_on='id')
            
            top_3 = logo_matches.nlargest(3, 'sponsorship_value')
            for _, match in top_3.iterrows():
                best_matches.append({
                    'logo': logo,
                    'match': f"{match['home_team']} vs {match['away_team']}",
                    'date': match['formatted_date'],
                    'value': match['sponsorship_value'],
                    'screen_time': match['visibility_time'],
                    'game_id': match['game_id'],
                    'thumbnail': match.get('thumbnail', '')
                })
        
        best_matches_df = pd.DataFrame(best_matches)
        
        # Get total games and appearances
        total_games = len(games.data)
        total_value = sponsor_stats['Total Value'].sum()
        total_appearances = sponsor_stats['Total Appearances'].sum()
        
        # Calculate averages
        avg_value_per_game = total_value / total_games if total_games > 0 else 0
        avg_appearances_per_game = total_appearances / total_games if total_games > 0 else 0
        
        # Set previous period metrics (for comparison)
        # In a real app, these would come from historical data
        prev_total_value = total_value * 0.9  # Just example values
        prev_avg_value_per_game = avg_value_per_game * 0.9
        prev_total_appearances = total_appearances * 0.9
        prev_total_games = max(0, total_games - 2)
        
        return {
            'sponsor_stats': sponsor_stats,
            'best_matches': best_matches_df,
            'total_games': total_games,
            'total_value': total_value,
            'total_appearances': total_appearances,
            'avg_value_per_game': avg_value_per_game,
            'avg_appearances_per_game': avg_appearances_per_game,
            'growth_data': growth_data,
            'competition_data': competition_data,
            'prev_total_value': prev_total_value,
            'prev_avg_value_per_game': prev_avg_value_per_game,
            'prev_total_appearances': prev_total_appearances,
            'prev_total_games': prev_total_games
        }
        
    except Exception as e:
        print(f"Error loading season data: {str(e)}")
        return None

def create_season_overview():
    data = load_season_data()
    if not data:
        return html.Div([
            html.H3("No data available", className="text-center my-5"),
            html.P("There are no processed games in the database yet.", className="text-center text-muted")
        ])
    
    # Create the layout
    layout = html.Div([
        # Dashboard Header with Title
        dbc.Row([
            dbc.Col([
                html.H1("Season Analytics Dashboard", className="mb-2"),
                html.P("Comprehensive overview of sponsor performance across all games", 
                       className="text-muted")
            ], width=True)
        ], className="mb-4 align-items-center"),
        
        # Key Performance Metrics
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${data['total_value']:,.2f}", 
                               className="value-card-number mb-2"),
                        html.P("Total Sponsorship Value", 
                               className="text-muted text-uppercase mb-0"),
                        html.Div([
                            html.I(className="fas fa-arrow-up text-success me-1"),
                            html.Small(f"{((data['total_value']/data['prev_total_value'])-1)*100:.1f}% vs. previous period", 
                                      className="text-success")
                        ], className="mt-2")
                    ], className="text-center")
                ], className="value-card h-100 shadow-sm")
            ], width=12, md=3, className="mb-4"),
            
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"${data['avg_value_per_game']:,.2f}", 
                               className="value-card-number mb-2"),
                        html.P("Average Value per Game", 
                               className="text-muted text-uppercase mb-0"),
                        html.Div([
                            html.I(className="fas fa-arrow-up text-success me-1"),
                            html.Small(f"{((data['avg_value_per_game']/data['prev_avg_value_per_game'])-1)*100:.1f}% vs. previous period", 
                                      className="text-success")
                        ], className="mt-2")
                    ], className="text-center")
                ], className="value-card h-100 shadow-sm")
            ], width=12, md=3, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{data['total_appearances']:,}", 
                               className="value-card-number mb-2"),
                        html.P("Total Sponsor Appearances", 
                               className="text-muted text-uppercase mb-0"),
                        html.Div([
                            html.I(className="fas fa-arrow-up text-success me-1"),
                            html.Small(f"{((data['total_appearances']/data['prev_total_appearances'])-1)*100:.1f}% vs. previous period", 
                                      className="text-success")
                        ], className="mt-2")
                    ], className="text-center")
                ], className="value-card h-100 shadow-sm")
            ], width=12, md=3, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardBody([
                        html.H4(f"{data['total_games']}", 
                               className="value-card-number mb-2"),
                        html.P("Games Analyzed", 
                               className="text-muted text-uppercase mb-0"),
                        html.Div([
                            html.I(className="fas fa-arrow-up text-success me-1"),
                            html.Small(f"{data['total_games'] - data['prev_total_games']} more than previous period", 
                                      className="text-success")
                        ], className="mt-2")
                    ], className="text-center")
                ], className="value-card h-100 shadow-sm")
            ], width=12, md=3, className="mb-4")
        ]),
        
        # Growth Charts Section
        dbc.Card([
            dbc.CardHeader([
                html.H3("Value Growth Over Time", className="mb-0"),
                html.Small("Cumulative sponsorship metrics across the season", className="text-muted")
            ], className="d-flex flex-column"),
            dbc.CardBody([
                dcc.Graph(
                    figure=go.Figure(
                        data=[
                            go.Scatter(
                                x=data['growth_data']['formatted_date'] if not data['growth_data'].empty else [],
                                y=data['growth_data']['cumulative_value'] if not data['growth_data'].empty else [],
                                mode='lines+markers',
                                name='Total Value',
                                line=dict(color='#1f77b4', width=3),
                                marker=dict(size=8)
                            )
                        ],
                        layout=go.Layout(
                            title='Cumulative Sponsorship Value Growth',
                            xaxis=dict(title='Match Date', tickangle=-45, showgrid=True, gridcolor='rgba(211, 211, 211, 0.5)'),
                            yaxis=dict(title='Cumulative Value ($)', showgrid=True, gridcolor='rgba(211, 211, 211, 0.5)'),
                            hovermode='closest',
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            margin=dict(t=50, b=70, l=50, r=30)
                        )
                    ),
                    config={'displayModeBar': True, 'responsive': True}
                )
            ])
        ], className="mb-4 shadow-sm"),
        
        # Leaderboard section with enhanced metrics and sorting
        dbc.Card([
            dbc.CardHeader([
                html.Div([
                    html.H3("Sponsor Performance Leaderboard", className="mb-0"),
                    html.Div([
                        html.Span("Sort by:", className="me-2"),
                        dbc.ButtonGroup([
                            dbc.Button("Value", id="sort-by-value", color="outline-primary", size="sm", active=True),
                            dbc.Button("Screen Time", id="sort-by-screentime", color="outline-primary", size="sm"),
                            dbc.Button("Efficiency", id="sort-by-efficiency", color="outline-primary", size="sm")
                        ], size="sm")
                    ], className="mt-2")
                ], className="d-flex justify-content-between align-items-center flex-wrap")
            ]),
            dbc.CardBody([
                html.Div([
                    dbc.Table([
                        html.Thead([
                            html.Tr([
                                html.Th("Sponsor"),
                                html.Th("Value ($)", className="text-end"),
                                html.Th("Value/Sec ($)", className="text-end"),
                                html.Th("Screen Time (s)", className="text-end"),
                                html.Th("Appearances", className="text-end"),
                                html.Th("Games", className="text-end"),
                                html.Th("Trend", className="text-center")
                            ])
                        ]),
                        html.Tbody([
                            html.Tr([
                                html.Td([
                                    html.Div([
                                        html.Span(f"{i+1}. ", className="me-2 text-muted"),
                                        html.Strong(row['Logo'])
                                    ], className="d-flex align-items-center")
                                ]),
                                html.Td(f"${row['Total Value']:,.2f}", className="text-end"),
                                html.Td(f"${row['Value Per Second']:,.2f}", className="text-end"),
                                html.Td(f"{row['Total Screen Time']:,.1f}", className="text-end"),
                                html.Td(f"{row['Total Appearances']:,}", className="text-end"),
                                html.Td(f"{row['Games Sponsored']}", className="text-end"),
                                html.Td([
                                    html.Div([
                                        dbc.Progress(
                                            value=min(row['Value Per Second']/max(data['sponsor_stats']['Value Per Second'])*100, 100), 
                                            className="mb-0", 
                                            style={"height": "8px"}, 
                                            color="success"
                                        )
                                    ], className="d-flex align-items-center")
                                ], className="text-center")
                            ], className=("table-primary" if i==0 else "")) 
                            for i, (_, row) in enumerate(data['sponsor_stats'].sort_values('Total Value', ascending=False).iterrows())
                        ])
                    ], bordered=True, hover=True, responsive=True, striped=True, className="mb-0")
                ], style={"overflowX": "auto"})
            ])
        ], className="mb-4 shadow-sm"),
        
        # Competition Performance Section
        dbc.Card([
            dbc.CardHeader(html.H3("Performance by Competition", className="mb-0")),
            dbc.CardBody([
                dbc.Row([
                    dbc.Col([
                        dcc.Graph(
                            figure=px.bar(
                                data['competition_data'] if not data['competition_data'].empty else pd.DataFrame(),
                                x='Competition',
                                y='Average Value per Game',
                                color='Competition',
                                title='Average Sponsorship Value per Game by Competition',
                                text_auto=True
                            ).update_layout(
                                paper_bgcolor='white',
                                plot_bgcolor='white',
                                margin=dict(t=50, b=20, l=20, r=20),
                                xaxis={'tickangle': -45},
                                yaxis={'title': 'Average Value ($)'},
                                showlegend=False
                            ).update_traces(
                                texttemplate='$%{y:,.2f}',
                                textposition='outside'
                            )
                        )
                    ], width=12)
                ])
            ])
        ], className="mb-4 shadow-sm"),
        
        # Charts section with more insights
        dbc.Row([
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Visibility Distribution", className="mb-0")),
                    dbc.CardBody(dcc.Graph(
                        figure=px.pie(
                            data['sponsor_stats'],
                            values='Total Screen Time',
                            names='Logo',
                            title='Share of Screen Time by Sponsor',
                            hole=0.4
                        ).update_layout(
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            legend=dict(orientation="h", y=-0.2),
                            margin=dict(t=50, b=70, l=20, r=20)
                        ).update_traces(
                            textinfo='percent+label'
                        )
                    ))
                ], className="shadow-sm h-100")
            ], width=12, md=6, className="mb-4"),
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader(html.H4("Value Per Appearance", className="mb-0")),
                    dbc.CardBody(dcc.Graph(
                        figure=px.bar(
                            data['sponsor_stats'].sort_values('Value Per Appearance', ascending=False),
                            x='Logo',
                            y='Value Per Appearance',
                            color='Logo',
                            title='Value Generated Per Logo Appearance',
                            text_auto=True
                        ).update_layout(
                            paper_bgcolor='white',
                            plot_bgcolor='white',
                            margin=dict(t=50, b=20, l=20, r=20),
                            xaxis={'tickangle': -45},
                            showlegend=False
                        ).update_traces(
                            texttemplate='$%{y:,.2f}',
                            textposition='outside'
                        ).update_yaxes(
                            title='$ Per Appearance',
                            showgrid=True,
                            gridcolor='rgba(211, 211, 211, 0.5)'
                        )
                    ))
                ], className="shadow-sm h-100")
            ], width=12, md=6, className="mb-4")
        ])
    ], className="dashboard-container p-4")
    
    return layout

# Add callbacks for interactive sorting
@callback(
    Output("sponsor-table", "children"),
    [
        Input("sort-by-value", "n_clicks"),
        Input("sort-by-screentime", "n_clicks"),
        Input("sort-by-efficiency", "n_clicks")
    ]
)
def update_table_sorting(value_clicks, screentime_clicks, efficiency_clicks):
    # Determine which button was clicked last
    if not ctx.triggered:
        sort_by = 'Total Value'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if button_id == "sort-by-value":
            sort_by = 'Total Value'
        elif button_id == "sort-by-screentime":
            sort_by = 'Total Screen Time'
        else:
            sort_by = 'Value Per Second'
    
    data = load_season_data()
    sorted_data = data['sponsor_stats'].sort_values(sort_by, ascending=False)
    
    # Return updated table
    return dbc.Table(
        [
            html.Thead([
                html.Tr([
                    html.Th("Sponsor"),
                    html.Th("Value ($)", className="text-end"),
                    html.Th("Value/Sec ($)", className="text-end"),
                    html.Th("Screen Time (s)", className="text-end"),
                    html.Th("Appearances", className="text-end"),
                    html.Th("Games", className="text-end"),
                    html.Th("Trend", className="text-center")
                ])
            ]),
            html.Tbody([
                html.Tr([
                    html.Td([
                        html.Div([
                            html.Span(f"{i+1}. ", className="me-2 text-muted"),
                            html.Strong(row['Logo'])
                        ], className="d-flex align-items-center")
                    ]),
                    html.Td(f"${row['Total Value']:,.2f}", className="text-end"),
                    html.Td(f"${row['Value Per Second']:,.2f}", className="text-end"),
                    html.Td(f"{row['Total Screen Time']:,.1f}", className="text-end"),
                    html.Td(f"{row['Total Appearances']:,}", className="text-end"),
                    html.Td(f"{row['Games Sponsored']}", className="text-end"),
                    html.Td([
                        html.Div([
                            dbc.Progress(
                                value=min(row['Value Per Second']/max(data['sponsor_stats']['Value Per Second'])*100, 100), 
                                className="mb-0", 
                                style={"height": "8px"}, 
                                color="success"
                            )
                        ], className="d-flex align-items-center")
                    ], className="text-center")
                ], className=("table-primary" if i==0 else "")) 
                for i, (_, row) in enumerate(sorted_data.iterrows())
            ])
        ], bordered=True, hover=True, responsive=True, striped=True, className="mb-0"
    )