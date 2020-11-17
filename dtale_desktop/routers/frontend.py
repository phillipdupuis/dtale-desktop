import os

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, Response

from dtale_desktop.settings import settings

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def frontend_view():
    with open(os.path.join(settings.REACT_APP_DIR, "index.html")) as f:
        return f.read()


@router.get("/manifest.json", include_in_schema=False)
async def manifest():
    with open(os.path.join(settings.REACT_APP_DIR, "manifest.json")) as f:
        return Response(content=f.read(), media_type="application/json")


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    with open(os.path.join(settings.REACT_APP_DIR, "favicon.ico"), "rb") as f:
        return Response(content=f.read(), media_type="image/x-icon")


@router.get("/logo192.png", include_in_schema=False)
async def logo192():
    with open(os.path.join(settings.REACT_APP_DIR, "logo192.png"), "rb") as f:
        return Response(content=f.read(), media_type="image/png")


@router.get("/logo512.png", include_in_schema=False)
async def logo512():
    with open(os.path.join(settings.REACT_APP_DIR, "logo512.png"), "rb") as f:
        return Response(content=f.read(), media_type="image/png")
