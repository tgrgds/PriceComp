from functools import lru_cache

from pydantic import BaseSettings

class Settings(BaseSettings):
  admin_key: str
  debug: bool = False
  discord_webhook_url: str

  class Config:
    env_file = ".env"

@lru_cache()
def get_settings():
  return Settings()
