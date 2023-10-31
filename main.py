import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.api import api
from src.prisma import prisma
from src.config import get_settings
from src.type import SiteName

if get_settings().debug:
  print("DEBUG enabled. Loading logger")
  
  logging.basicConfig(filename="logs/debug.log", encoding="utf-8", level=logging.DEBUG, format="%(asctime)s:%(name)s %(levelname)s:%(message)s")

app = FastAPI(
  title="PriceComp",
  version="0.0.1"
)

app.add_middleware(
  CORSMiddleware,
  allow_origins=["*"], # TODO: set specific origins!!
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)

app.include_router(api, prefix="/api")

@app.on_event("startup")
async def startup():
  await prisma.connect()

  # Init competitor "analytics"
  for site in SiteName:
    await prisma.competitor.upsert(
      where={
        "store_id": site.value
      },
      data={
        "create": { "store_id": site.value },
        "update": { "store_id": site.value },
      }
    )

@app.on_event("shutdown")
async def shutdown():
  await prisma.disconnect()

@app.get("/")
def read_root():
  return {"version": "0.0.1"}
