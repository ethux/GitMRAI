from supabase import create_client, Client
from src.config.settings import supersettings

def get_db() -> Client:
    url = supersettings.SUPABASE_URL
    key = supersettings.SUPABASE_KEY
    return create_client(url, key)