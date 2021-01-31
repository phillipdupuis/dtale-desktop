import os
import socket

import uvicorn
from fastapi import FastAPI
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from dtale_desktop import default_sources, routers, dtale_app
from dtale_desktop.actions import UpdateSettings
from dtale_desktop.file_system import fs
from dtale_desktop.logger import get_logger
from dtale_desktop.models import register_existing_source
from dtale_desktop.settings import settings
from dtale_desktop.subprocesses import launch_browser_opener
from dtale_desktop.websocket_connections import websocket_path, websocket_endpoint

logger = get_logger()

_description = f"""
API Documentation for the backend routes.
It can also be viewed using <a href="{settings.ROOT_URL}/redoc" target="_blank" rel="noopener noreferrer">redoc</a>.
"""

app = FastAPI(title=settings.APP_TITLE, description=_description)

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(settings.REACT_APP_DIR, "static")),
    name="static",
)

app.mount(
    "/themes",
    StaticFiles(directory=os.path.join(settings.REACT_APP_DIR, "themes")),
    name="themes",
)


@app.on_event("startup")
def register_any_existing_sources() -> None:
    """
    Register the default data sources and any existing custom data sources.
    """
    if not settings.EXCLUDE_DEFAULT_LOADERS:
        for pkg in [default_sources.csv, default_sources.excel, default_sources.json]:
            register_existing_source(pkg.__path__[0], editable=False)

    for loaders_dir in [fs.LOADERS_DIR, *fs.ADDITIONAL_LOADERS_DIRS]:
        for path in (os.path.join(loaders_dir, p) for p in os.listdir(loaders_dir)):
            if os.path.isdir(path):
                register_existing_source(path)


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request, exc: StarletteHTTPException):
    """
    Log the exception and then pass it through to the default handler
    """
    logger.exception(str(exc))
    return await http_exception_handler(request, exc)


@app.get("/health/")
async def health_check():
    return Response(status_code=204)


@app.get("/settings/", response_model=UpdateSettings)
async def get_settings():
    return UpdateSettings(settings=settings.serialize())


app.include_router(routers.frontend.router, tags=["Frontend"])
app.include_router(routers.sources.router, tags=["Sources"])
app.include_router(routers.nodes.router, tags=["Nodes"])

if not settings.DISABLE_PROFILE_REPORTS:
    app.include_router(routers.profile_reports.router, tags=["Profile Reports"])

if settings.ENABLE_WEBSOCKET_CONNECTIONS:
    app.add_api_websocket_route(websocket_path, websocket_endpoint)


def run():
    if not settings.DISABLE_OPEN_BROWSER:
        launch_browser_opener(f"http://{settings.HOST}:{settings.PORT}")

    dtale_app.run()

    uvicorn.run(
        app, host=socket.gethostbyname(settings.HOST), port=settings.PORT, debug=True,
    )


if __name__ == "__main__":
    run()
