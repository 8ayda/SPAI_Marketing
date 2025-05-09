from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from datetime import datetime
from config.supabase_client import supabase
from config.teams import LALIGA_TEAMS, UCL_TEAMS
import logging
import base64
import io
from PIL import Image
from supabase.lib.client_options import ClientOptions

# Configure logging
logger = logging.getLogger(__name__)

# Define competitions
COMPETITIONS = ["LaLiga", "Champions League", "Copa del Rey"]

def create_upload_page():
    return html.Div([
        dbc.Container([
            html.H2("Upload New Game", className="text-center my-4"),
            dbc.Card(
                dbc.CardBody([
                    dbc.Form([
                        # Competition Select
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Competition", className="form-label"),
                                dbc.Select(
                                    id="competition-select",
                                    options=[
                                        {"label": comp, "value": comp}
                                        for comp in COMPETITIONS
                                    ],
                                    placeholder="Select competition",
                                    className="mb-3 shadow-sm"
                                )
                            ], width=12),
                        ]),
                        # Team Selects
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Home Team", className="form-label"),
                                dcc.Dropdown(
                                    id="home-team-input",
                                    options=[],
                                    placeholder="Type or select home team",
                                    className="mb-3 shadow-sm",
                                    clearable=True,
                                    searchable=True
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Away Team", className="form-label"),
                                dcc.Dropdown(
                                    id="away-team-input",
                                    options=[],
                                    placeholder="Type or select away team",
                                    className="mb-3 shadow-sm",
                                    clearable=True,
                                    searchable=True
                                )
                            ], width=6),
                        ]),
                        # Video Path
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Video Path"),
                                dbc.Input(
                                    id="video-path",
                                    type="text",
                                    placeholder="Enter video path",
                                    className="mb-3 shadow-sm"
                                )
                            ], width=12),
                        ]),
                        # Game Date
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Game Date"),
                                dcc.DatePickerSingle(
                                    id='game-date',
                                    date=datetime.now().date(),
                                    display_format='YYYY-MM-DD',
                                    className="mb-3 shadow-sm"
                                ),
                            ], width=6),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Thumbnail Image (Optional)"),
                                dcc.Upload(
                                    id="thumbnail-upload",
                                    children=html.Div([
                                        'Drag and Drop or ',
                                        html.A('Select a Thumbnail')
                                    ]),
                                    style={
                                        'width': '100%',
                                        'height': '60px',
                                        'lineHeight': '60px',
                                        'borderWidth': '1px',
                                        'borderStyle': 'dashed',
                                        'borderRadius': '5px',
                                        'textAlign': 'center',
                                        'margin': '10px 0'
                                    },
                                    multiple=False
                                ),
                                html.Div(id="thumbnail-preview")
                            ], width=12),
                        ]),
                        dbc.Row([
                            dbc.Col([
                                dbc.Button(
                                    "Upload Game",
                                    id="submit-button",
                                    n_clicks=0,
                                    color="primary",
                                    className="mt-3 w-100"
                                ),
                            ], width=12),
                        ]),
                        html.Div(id="submit-result", className="mt-3")
                    ])
                ])
            )
        ])
    ])

# Update the callback for team options
@callback(
    [Output("home-team-input", "options"),
     Output("away-team-input", "options")],
    [Input("competition-select", "value")]
)
def update_team_options(competition):
    if not competition:
        return [], []
        
    if competition == "Champions League":
        teams = UCL_TEAMS
    else:  # LaLiga or Copa del Rey
        teams = LALIGA_TEAMS
        
    team_options = [{"label": team, "value": team} for team in sorted(teams)]
    return team_options, team_options

@callback(
    Output("submit-result", "children"),
    [Input("submit-button", "n_clicks")],
    [
        State("competition-select", "value"),
        State("home-team-input", "value"),
        State("away-team-input", "value"),
        State("game-date", "date"),
        State("video-path", "value"),  # Added video path input
        State("thumbnail-upload", "contents"),
        State("thumbnail-upload", "filename")
    ]
)
def handle_upload(n_clicks, competition, home_team, away_team, match_date, 
                 video_path, thumbnail_contents, thumbnail_filename):
    if n_clicks is None or n_clicks == 0:
        return ""

    # Validate required fields
    if not all([competition, home_team, away_team, match_date, video_path]):
        return dbc.Alert(
            "Please fill all required fields.",
            color="danger",
            dismissable=True,
            is_open=True
        )

    # Process thumbnail if provided
    thumbnail_url = None
    if thumbnail_contents:
        try:
            bucket_name = 'game-thumbnails'
            
            # Decode base64 image
            content_type, content_string = thumbnail_contents.split(',')
            decoded = base64.b64decode(content_string)
            
            # Generate simple file path
            file_path = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            
            try:
                logger.info(f"Attempting to upload file to bucket: {bucket_name}")
                # Direct upload without bucket check
                response = supabase.storage.from_(bucket_name).upload(
                    path=file_path,
                    file=decoded,
                    file_options={"content-type": "image/jpeg"}
                )
                
                if response:
                    thumbnail_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
                    logger.info(f"Upload successful. URL: {thumbnail_url}")
                else:
                    logger.error("Upload response was empty")
                    raise Exception("Upload failed - no response from server")
                
            except Exception as upload_error:
                logger.error(f"Storage upload error: {str(upload_error)}")
                return dbc.Alert(
                    f"Upload failed: {str(upload_error)}",
                    color="danger",
                    dismissable=True,
                    is_open=True
                )
                
        except Exception as e:
            logger.error(f"Thumbnail processing error: {str(e)}")
            return dbc.Alert(
                f"Error processing thumbnail: {str(e)}",
                color="danger",
                dismissable=True,
                is_open=True
            )

    # Prepare data with video_path
    data = {
        "competition": competition,
        "home_team": home_team,
        "away_team": away_team,
        "match_date": match_date,
        "thumbnail": thumbnail_url,
        "video_path": video_path,  # Added video_path
        "status": "pending"
    }

    try:
        logger.info("Attempting to insert game data into database")
        response = supabase.table("games").insert(data).execute()
        if response and response.data:
            logger.info("Game data inserted successfully")
            return dbc.Alert(
                "Game uploaded successfully!",
                color="success",
                dismissable=True,
                is_open=True
            )
        else:
            logger.error("Database insert response was empty")
            return dbc.Alert(
                "Upload failed. No response from server.",
                color="danger",
                dismissable=True,
                is_open=True
            )
    except Exception as e:
        logger.error(f"Database insert error: {str(e)}")
        return dbc.Alert(
            f"Error: {str(e)}",
            color="danger",
            dismissable=True,
            is_open=True
        )

@callback(
    Output("thumbnail-preview", "children"),
    Input("thumbnail-upload", "contents"),
    State("thumbnail-upload", "filename")
)
def update_thumbnail_preview(contents, filename):
    if contents is None:
        return ""
    
    return html.Div([
        html.Img(src=contents, style={'height': '100px', 'margin': '10px'}),
        html.Div(filename)
    ])
