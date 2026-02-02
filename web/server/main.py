from fastapi import FastAPI
from . import server
app = FastAPI()
app.include_router(server.router)
