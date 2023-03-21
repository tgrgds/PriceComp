from fastapi import APIRouter, Depends, HTTPException

from typing_extensions import Annotated

from src.auth import generate_api_key
from src.config import get_settings, Settings

router = APIRouter()

# Create a new API key
# right now has a hardcoded password to avoid giving everyone api keys
# todo: find a better way LOL
@router.post("/auth/new", tags=["auth"])
async def new_api_key(admin_key: str, settings: Annotated[Settings, Depends(get_settings)]):
  if admin_key == settings.admin_key:
    key = await generate_api_key()

    return { "key": key }
  
  else:
    raise HTTPException(status_code=401, detail="admin_key incorrect")
