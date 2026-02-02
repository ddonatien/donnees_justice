from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/")
async def read_root():
    return HTMLResponse(content="<h1>Welcome</h1>")
