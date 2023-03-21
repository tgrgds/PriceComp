from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.api import api
from src.prisma import prisma

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

@app.on_event("shutdown")
async def shutdown():
  await prisma.disconnect()

@app.get("/")
def read_root():
  return {"version": "0.0.1"}
