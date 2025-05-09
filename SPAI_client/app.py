# app.py
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import dash
from dash import html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import pandas as pd
import json
import io
from components.sidebar import create_sidebar
from layouts.home import create_home_layout  # This will be your new home page
from layouts.game_dashboard import create_game_dashboard, load_game_data
from layouts.season_overview import create_season_overview
from layouts.game_cards_page import create_game_cards_layout
from layouts.tables import create_tables_layout  # Import the new layout
from layouts.contact import create_contact_layout  # Add this import at the top
from layouts.notifications import create_notifications_layout

# Initialize the app
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
    ],
    suppress_callback_exceptions=True  # This is important for multi-page apps
)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),  # This will contain either the home page or the sidebar+content layout
    dcc.Download(id="download-dataframe-csv"),
    dcc.Download(id="download-json"),
])

# Add a new callback to handle the page content structure
@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')]
)
def render_page_structure(pathname):
    if pathname == '/':
        return html.Div(id='page-layout')  # Just the content for home page
    else:
        return html.Div([  # Sidebar + content for other pages
            create_sidebar(),
            html.Div([
                html.Div(id='page-layout')
            ], className="content")
        ], className="app-container")

# Update the callback to handle page content
@app.callback(
    Output('page-layout', 'children'),
    [Input('url', 'pathname')]
)
def display_page(pathname):
    if pathname == '/':
        return create_home_layout()  # Home page without sidebar
    elif pathname == '/cards':
        return create_game_cards_layout()
    elif pathname == '/season-overview':
        return create_season_overview()
    elif pathname == '/tables':
        return create_tables_layout()
    elif pathname == '/contact':
        return create_contact_layout()
    elif pathname == '/notifications':
        return create_notifications_layout()
    elif pathname and pathname.startswith('/game/'):
        game_id = pathname.split('/')[-1]
        return create_game_dashboard(game_id)
    return "404 Page Not Found"

@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("export-csv-btn", "n_clicks"),
    State('url', 'pathname'),
    prevent_initial_call=True
)
def export_csv(n_clicks, pathname):
    if n_clicks is None or n_clicks == 0:
        return None
    
    if pathname and pathname.startswith('/game/'):
        try:
            game_id = pathname.split('/')[-1]
            data = load_game_data(game_id)
            
            # Create DataFrame for each data type
            sponsor_df = pd.DataFrame(data['value_data'])
            visibility_df = pd.DataFrame(data['visibility_data'])
            
            # Combine into a single buffer
            buffer = io.StringIO()
            buffer.write("Sponsor Data:\n")
            sponsor_df.to_csv(buffer, index=False)
            buffer.write("\n\nVisibility Data:\n")
            visibility_df.to_csv(buffer, index=False)
            
            return dict(
                content=buffer.getvalue(),
                filename=f"game_{game_id}_analysis.csv"
            )
        except Exception as e:
            print(f"CSV Export Error: {str(e)}")
            return None
    return None

@app.callback(
    Output("download-json", "data"),
    Input("export-json-btn", "n_clicks"),
    State('url', 'pathname'),
    prevent_initial_call=True
)
def export_json(n_clicks, pathname):
    if n_clicks is None or n_clicks == 0:
        return None
    
    if pathname and pathname.startswith('/game/'):
        try:
            game_id = pathname.split('/')[-1]
            data = load_game_data(game_id)
            
            # Format the data for JSON export
            export_data = {
                'game_info': data['game_info'],
                'sponsor_data': data['value_data'],
                'visibility_data': data['visibility_data']
            }
            
            return dict(
                content=json.dumps(export_data, indent=2, default=str),
                filename=f"game_{game_id}_analysis.json"
            )
        except Exception as e:
            print(f"JSON Export Error: {str(e)}")
            return None
    return None

if __name__ == '__main__':
    app.run(debug=True, port=8050)