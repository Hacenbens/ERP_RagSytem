from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings (BaseSettings):
    APP_NAME :str
    APP_VERSION :str
    OPENAI_API_KEY :str 
    
    FILE_EXTENTIONS_ALLOWED : list
    FILE_MAX_SIZE : int
    FILE_CHUNK_SIZE : int
    
    model_config = SettingsConfigDict(
            env_file=".env",  # Looks in current working directory
            env_file_encoding="utf-8",
        )

def get_settings ():
    return Settings()       
        