# utils/data_processing.py
import pandas as pd
import json
import os

def load_all_game_data(data_dir='data'):
    """Load all game data from JSON/CSV files in the data directory."""
    games = []
    for filename in os.listdir(data_dir):
        if filename.endswith('.json'):
            with open(os.path.join(data_dir, filename), 'r') as f:
                game_data = json.load(f)
                games.append(game_data)
    return games

def process_logo_detections(games):
    """Process raw logo detection data into formats suitable for visualization."""
    all_detections = []
    
    for game in games:
        game_id = game['game_id']
        home_team = game['home_team']
        away_team = game['away_team']
        date = game['date']
        
        for frame in game['frames']:
            timestamp = frame['timestamp']
            for detection in frame['detections']:
                all_detections.append({
                    'game_id': game_id,
                    'home_team': home_team,
                    'away_team': away_team,
                    'date': date,
                    'timestamp': timestamp,
                    'logo': detection['logo_name'],
                    'confidence': detection['confidence'],
                    'x': detection['bbox'][0],
                    'y': detection['bbox'][1],
                    'width': detection['bbox'][2],
                    'height': detection['bbox'][3],
                    'visibility_score': detection.get('visibility_score', detection['confidence']),
                    'duration': detection.get('duration', 1)
                })
    
    return pd.DataFrame(all_detections)

def calculate_logo_value(detections_df, value_config=None):
    """Calculate estimated sponsor value based on detection data."""
    if value_config is None:
        # Default value calculation config
        value_config = {
            'base_rate': 100,  # Base rate per second of visibility
            'confidence_multiplier': 1.5,  # Multiplier for detection confidence
            'size_multiplier': 2,  # Multiplier for detection size
            'central_position_bonus': 1.2  # Bonus for central screen position
        }
    
    # Calculate value for each detection
    detections_df['area'] = detections_df['width'] * detections_df['height']
    detections_df['is_central'] = ((detections_df['x'] > 0.3) & 
                                    (detections_df['x'] < 0.7) & 
                                    (detections_df['y'] > 0.3) & 
                                    (detections_df['y'] < 0.7))
    
    detections_df['detection_value'] = (
        value_config['base_rate'] * 
        detections_df['duration'] * 
        (1 + (detections_df['confidence'] - 0.5) * value_config['confidence_multiplier']) *
        (1 + detections_df['area'] * value_config['size_multiplier']) *
        (value_config['central_position_bonus'] if detections_df['is_central'] else 1)
    )
    
    # Aggregate by logo and game
    logo_value = detections_df.groupby(['game_id', 'logo']).agg({
        'detection_value': 'sum',
        'timestamp': 'count',
        'duration': 'sum'
    }).reset_index()
    
    logo_value.columns = ['game_id', 'logo', 'estimated_value', 'appearances', 'screen_time']
    
    return logo_value