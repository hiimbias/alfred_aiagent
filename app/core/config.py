from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    Settings for the application.
    """
    # OpenAI API settings
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    WEATHERAPI_API_KEY: str
    WEATHERAPI_BASE_URL: str = "https://api.weatherapi.com/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields in the .env file

settings = Settings()