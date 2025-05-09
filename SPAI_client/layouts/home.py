import dash_bootstrap_components as dbc
from dash import html

def create_home_layout():
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    # SPAI Logo at the top
                    html.Img(
                        src="/assets/images/SPAI_logo.png",
                        className="spai-logo mb-5"
                    ),
                    
                    # Welcome Message first
                    html.H1([
                        "Welcome to ",
                        html.Span("SPAI", className="gradient-text")
                    ], className="welcome-title mb-4"),
                    
                    # Club Identity right under welcome message
                    html.Div([
                        html.Img(
                            src="/assets/images/barca_logo.png",
                            className="club-logo me-3"
                        ),
                        html.H2("FC Barcelona", className="club-name")
                    ], className="club-identity"),
                    
                    # Description
                    html.P(
                        "From detection to decision: visualize, evaluate, and optimize sponsor exposure like never before.",
                        className="lead mb-5"
                    ),
                    
                    # Action Buttons
                    dbc.Row([
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-gamepad me-2"),
                                "Game Analysis"
                            ],
                            href="/cards",
                            className="nav-button"
                            )
                        ], xs=12, md=6, className="mb-3 mb-md-0"),
                        
                        dbc.Col([
                            dbc.Button([
                                html.I(className="fas fa-chart-line me-2"),
                                "Season Dashboard"
                            ],
                            href="/season-overview",
                            className="nav-button"
                            )
                        ], xs=12, md=6),
                    ], className="g-4")
                ], 
                width={"size": 6, "offset": 0},
                className="d-flex flex-column justify-content-center align-items-center min-vh-100"
                )
            ])
        ], fluid=True)
    ], className="home-page")