from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from . import router

app = FastAPI(title="French Court Decisions Analytics", 
              description="Web interface for analyzing French administrative court decisions",
              version="0.1.0")

# Mount static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")
app.mount("/plots", StaticFiles(directory="analytics"), name="plots")

# Include router
app.include_router(router.router)
