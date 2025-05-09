from config.supabase_client import supabase
from datetime import datetime

class GameOperations:
    @staticmethod
    def add_game(competition, home_team, away_team, game_date, video_path, thumbnail_path=None):
        try:
            data = {
                "competition": competition,
                "home_team": home_team,
                "away_team": away_team,
                "game_date": game_date,
                "video_path": video_path,
                "thumbnail_path": thumbnail_path,
                "status": "pending"
            }
            
            response = supabase.table('games').insert(data).execute()
            return response.data[0] if response.data else None
            
        except Exception as e:
            print(f"Error adding game: {str(e)}")
            return None

    @staticmethod
    def get_all_games():
        try:
            response = supabase.table('games').select("*").order('created_at', desc=True).execute()
            return response.data
        except Exception as e:
            print(f"Error fetching games: {str(e)}")
            return []

    @staticmethod
    def update_game_status(game_id, status):
        try:
            response = supabase.table('games').update({"status": status}).eq("id", game_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"Error updating game status: {str(e)}")
            return None

    @staticmethod
    def delete_game(game_id):
        try:
            response = supabase.table('games').delete().eq("id", game_id).execute()
            return True
        except Exception as e:
            print(f"Error deleting game: {str(e)}")
            return False