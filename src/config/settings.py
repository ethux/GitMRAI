from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    MODEL: str
    API_KEY: str
    GITLAB_URL: str
    GITLAB_TOKEN: str
    SECRET_TOKEN: str
    SUPABASE_URL: str
    SUPABASE_KEY: str

    class Config:
        env_file = ".env"

# Create an instance of Settings
supersettings = Settings()