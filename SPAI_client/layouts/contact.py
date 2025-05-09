from dash import html, Input, Output, State, callback
import dash_bootstrap_components as dbc
from utils.supabase_client import supabase
import json

def create_contact_layout():
    return html.Div([
        dbc.Container([
            dbc.Row([
                dbc.Col([
                    html.H1("Contact Us", className="mb-4"),
                    html.P("Get in touch with our team for any questions or support.", className="lead mb-4"),
                    
                    # Contact Form with IDs for callbacks
                    dbc.Form([
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Name"),
                                dbc.Input(
                                    type="text",
                                    placeholder="Enter your name",
                                    id="contact-name"
                                )
                            ], width=6),
                            dbc.Col([
                                dbc.Label("Email"),
                                dbc.Input(
                                    type="email",
                                    placeholder="Enter your email",
                                    id="contact-email"
                                )
                            ], width=6),
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Subject"),
                                dbc.Input(
                                    type="text",
                                    placeholder="Enter subject",
                                    id="contact-subject"
                                )
                            ], width=12),
                        ], className="mb-3"),
                        
                        dbc.Row([
                            dbc.Col([
                                dbc.Label("Message"),
                                dbc.Textarea(
                                    placeholder="Enter your message",
                                    rows=5,
                                    id="contact-message"
                                )
                            ], width=12),
                        ], className="mb-4"),
                        
                        html.Div([
                            dbc.Button(
                                "Send Message",
                                color="primary",
                                size="lg",
                                id="submit-contact"
                            ),
                            # Success/Error message
                            html.Div(id="contact-feedback", className="mt-3")
                        ], className="text-center")
                    ])
                ], width=8, className="mx-auto")
            ])
        ], className="py-5")
    ], className="contact-page")

# Callback for form submission
@callback(
    [
        Output("contact-feedback", "children"),
        Output("contact-name", "value"),
        Output("contact-email", "value"),
        Output("contact-subject", "value"),
        Output("contact-message", "value")
    ],
    [Input("submit-contact", "n_clicks")],
    [
        State("contact-name", "value"),
        State("contact-email", "value"),
        State("contact-subject", "value"),
        State("contact-message", "value")
    ]
)
def submit_contact_form(n_clicks, name, email, subject, message):
    if not n_clicks:
        return "", None, None, None, None
    
    try:
        # Validate inputs
        if not all([name, email, subject, message]):
            return html.Div("Please fill in all fields", className="text-danger"), name, email, subject, message
        
        # Submit to Supabase
        data = supabase.table('contact_submissions').insert({
            "name": name,
            "email": email,
            "subject": subject,
            "message": message
        }).execute()
        
        # Return success message and reset all inputs
        return (
            html.Div("Thank you for your message. We'll get back to you soon!", className="text-success"),
            "",  # Reset name
            "",  # Reset email
            "",  # Reset subject
            ""   # Reset message
        )
        
    except Exception as e:
        print(f"Error submitting contact form: {str(e)}")
        return (
            html.Div("An error occurred. Please try again later.", className="text-danger"),
            name, email, subject, message  # Keep values on error
        )