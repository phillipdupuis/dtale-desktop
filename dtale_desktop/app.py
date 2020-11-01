import os
import asyncio
from typing import List

import uvicorn
from fastapi import FastAPI, Depends
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from dtale_desktop import default_sources
from dtale_desktop.file_system import fs
from dtale_desktop.models import (
    SOURCES,
    DataSourceSerialized,
    DataSourceLayoutChange,
    Node,
    register_existing_source,
)
from dtale_desktop.settings import settings
from dtale_desktop.subprocesses import launch_browser_opener

REACT_APP_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "frontend", "build"
)

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")

app = FastAPI(title="D-Tale Desktop")

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(REACT_APP_DIR, "static")),
    name="static",
)


@app.on_event("startup")
def register_any_existing_sources() -> None:
    """
    Register the default data sources and any existing custom data sources.
    """
    for pkg in [default_sources.csv, default_sources.excel, default_sources.json]:
        register_existing_source(pkg.__path__[0], editable=False)

    for loaders_dir in [fs.LOADERS_DIR, *fs.ADDITIONAL_LOADERS_DIRS]:
        for path in (os.path.join(loaders_dir, p) for p in os.listdir(loaders_dir)):
            register_existing_source(path)


@app.get("/", response_class=HTMLResponse)
async def frontend_view():
    with open(os.path.join(REACT_APP_DIR, "index.html")) as f:
        return f.read()


@app.get("/health/")
async def health_check():
    return Response(status_code=204)


@app.get("/manifest.json", include_in_schema=False)
async def manifest():
    with open(os.path.join(REACT_APP_DIR, "manifest.json")) as f:
        return Response(content=f.read(), media_type="application/json")


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    with open(os.path.join(REACT_APP_DIR, "favicon.ico"), "rb") as f:
        return Response(content=f.read(), media_type="image/x-icon")


@app.get("/logo192.png", include_in_schema=False)
async def logo192():
    with open(os.path.join(REACT_APP_DIR, "logo192.png"), "rb") as f:
        return Response(content=f.read(), media_type="image/png")


@app.get("/logo512.png", include_in_schema=False)
async def logo512():
    with open(os.path.join(REACT_APP_DIR, "logo512.png"), "rb") as f:
        return Response(content=f.read(), media_type="image/png")


@app.get("/settings/")
async def get_settings():
    return {
        "disableAddDataSources": settings.DISABLE_ADD_DATA_SOURCES,
        "disableEditDataSources": settings.DISABLE_EDIT_DATA_SOURCES,
        "disableEditLayout": settings.DISABLE_EDIT_LAYOUT,
    }


@app.get("/source/list/", response_model=List[DataSourceSerialized])
async def get_source_list():
    return [source.serialize() for source in SOURCES.values()]


@app.post("/source/create/", response_model=DataSourceSerialized)
async def create_source(serialized: DataSourceSerialized):
    source = serialized.deserialize()
    return source.serialize()


@app.post("/source/update/", response_model=DataSourceSerialized)
async def update_source(serialized: DataSourceSerialized):
    source = serialized.deserialize(overwrite_existing=True)
    return source.serialize()


@app.post("/source/update-layout/", response_model=List[DataSourceSerialized])
async def update_source_layout(changes: List[DataSourceLayoutChange]):
    return [change.apply() for change in changes]


@app.post("/source/nodes/list/", response_model=DataSourceSerialized)
async def load_source_nodes(serialized: DataSourceSerialized):
    source = serialized.deserialize()
    await source.load_nodes(limit=50)
    return source.serialize()


def get_node_by_data_id(data_id: str) -> Node:
    """
    Reusable as dependency for taking a data_id path parameter and returning the Node instance.
    """
    for source in SOURCES.values():
        if data_id in source.nodes:
            return source.nodes[data_id]


@app.get("/node/view/{data_id}/", response_model=Node)
async def node_view_dtale_instance(node: Node = Depends(get_node_by_data_id)):
    await node.launch_dtale()
    return node


@app.get("/node/kill/{data_id}/", response_model=Node)
async def node_kill_dtale_instance(node: Node = Depends(get_node_by_data_id)):
    await node.shut_down()
    return node


@app.get("/node/clear-cache/{data_id}/", response_model=Node)
async def node_clear_cache(node: Node = Depends(get_node_by_data_id)):
    await node.clear_cache()
    return node


@app.get("/node/profile-report/{data_id}/", response_class=HTMLResponse)
async def noad_profile_report_loading_page(data_id: str):
    """
    This one is a bit weird because it is being opened in a new tab.
    We do this because building a profile report can take a LONG time, and we don't want to block the main app.

    We return a static loading page which, when the window is ready, will fetch /node/build-profile-report/{data_id}/.
    Once the report is built, the response will provide a url for viewing it.
    The promise resolves by redirecting the user to that URL (in the newly opened tab).
    """
    with open(os.path.join(TEMPLATES_DIR, "loading_profile_report.html")) as f:
        return f.read()


@app.get("/node/build-profile-report/{data_id}/")
async def node_build_profile_report(node: Node = Depends(get_node_by_data_id)):
    await node.build_profile_report()
    return {
        "ok": True,
        "url": f"http://{settings.HOST}:{settings.PORT}/node/view-profile-report/{node.data_id}/",
    }


@app.get("/node/watch-profile-report-builder/{data_id}/")
async def node_watch_profile_report_builder(data_id: str):
    """
    Allows the front-end to update the display information once a profile report builds successfully.
    Necessary because the profile report entails opening a separate tab.
    """
    time_waited = 0
    while time_waited < 600:
        if fs.profile_report_exists(data_id):
            return {"ok": True, "node": get_node_by_data_id(data_id)}
        await asyncio.sleep(5)
        time_waited += 5
    return {"ok": False}


@app.get("/node/view-profile-report/{data_id}/", response_class=HTMLResponse)
async def node_view_profile_report(data_id: str):
    return fs.read_profile_report(data_id)


def run():
    launch_browser_opener(f"http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT, debug=True)


if __name__ == "__main__":
    run()
