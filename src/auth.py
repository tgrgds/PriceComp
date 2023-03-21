from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from uuid import uuid4, UUID
from hashlib import sha256

from src.prisma import prisma

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def api_key_auth(api_key: str = Depends(oauth2_scheme)):
  key = await prisma.user.find_unique(
    where={
      "hash": hash_key(api_key)
    }
  )

  if not key:
    raise HTTPException(status_code=401, detail="Forbidden")

def hash_key(api_key: str):
  return sha256(api_key.encode("utf-8")).hexdigest()

# generate an api key and store its hash in the database
# returns the plain uuid
async def generate_api_key():
  key = str(uuid4())

  await prisma.user.create(
    data={
      "hash": hash_key(key)
    }
  )

  return key
