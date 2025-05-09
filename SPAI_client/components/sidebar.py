# components/sidebar.py
import dash_bootstrap_components as dbc
from dash import html

def create_sidebar():
    return html.Div([
        # Logo and Title
        html.Div([
            html.Div([
                html.Img(
                    src="/assets/images/SPAI_logo.png",
                    height="60px",
                    className="me-2 sidebar-logo"
                ),
                html.Span("SPAI.", className="sidebar-title")
            ], className="sidebar-brand d-flex align-items-center")
        ], className="sidebar-header"),
        
        # Season Dashboard Button
        dbc.Button([
            html.I(className="fas fa-chart-line me-2"),
            "Season Dashboard"
        ], 
        color="primary", 
        href="/season-overview",
        className="season-dashboard-btn mb-3"),
        
        # Navigation Section
        html.Div([
            html.Div("NAVIGATION", className="sidebar-section-title"),
            dbc.Nav([
                dbc.NavLink([
                    html.I(className="fas fa-home me-2"),
                    "Home"
                ], href="/", active="exact", className="sidebar-link"),
                
                dbc.NavLink([
                    html.I(className="fas fa-gamepad me-2"),
                    "Game Cards"
                ], href="/cards", className="sidebar-link"),
                
                dbc.NavLink([
                    html.I(className="fas fa-table me-2"),
                    "Tables"
                ], href="/tables", className="sidebar-link")
            ], vertical=True, className="sidebar-nav-group"),
        ], className="sidebar-nav-container"),
        
        # Spacer
        html.Div(className="flex-grow-1"),
        
        # System Section
        html.Div([
            html.Div("SYSTEM", className="sidebar-section-title"),
            dbc.Nav([
                dbc.NavLink([
                    html.I(className="fas fa-bell me-2"),
                    "Notifications"
                ], href="/notifications", className="sidebar-link"),
                
                dbc.NavLink([
                    html.I(className="fas fa-envelope me-2"),
                    "Contact Us"
                ], href="/contact", className="sidebar-link")
            ], vertical=True, className="sidebar-nav-group mb-3")
        ], className="sidebar-system-container")
        
    ], className="sidebar d-flex flex-column")