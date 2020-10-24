import os
import subprocess
import socket
from typing import List

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles

from dtale_desktop import default_sources
from dtale_desktop.models import (
    SOURCES,
    DataSourceSerialized,
    Node,
    register_existing_source,
    LOADERS_DIR,
    get_node_by_data_id,
)
from dtale_desktop.pydantic_utils import BaseApiModel


def _get_host() -> str:
    try:
        return socket.gethostbyname("localhost")
    except BaseException:
        return socket.gethostbyname(socket.gethostname())


def _get_port() -> int:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("", 0))
    port = sock.getsockname()[1]
    sock.close()
    return port


HOST = _get_host()

PORT = _get_port()

REACT_APP_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "frontend", "build"
)

app = FastAPI()

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

    for path in (os.path.join(LOADERS_DIR, p) for p in os.listdir(LOADERS_DIR)):
        register_existing_source(path)


@app.get("/", response_class=HTMLResponse)
async def frontend_view():
    with open(os.path.join(REACT_APP_DIR, "index.html")) as f:
        return f.read()


@app.get("/health/")
async def health_check():
    return Response(status_code=204)


@app.get("/manifest.json")
async def manifest():
    with open(os.path.join(REACT_APP_DIR, "manifest.json")) as f:
        return Response(content=f.read(), media_type="application/json")


@app.get("/favicon.ico")
async def favicon():
    with open(os.path.join(REACT_APP_DIR, "favicon.ico"), "rb") as f:
        return Response(content=f.read(), media_type="image/x-icon")


@app.get("/logo192.png")
async def logo192():
    with open(os.path.join(REACT_APP_DIR, "logo192.png"), "rb") as f:
        return Response(content=f.read(), media_type="image/png")


@app.get("/logo512.png")
async def logo512():
    with open(os.path.join(REACT_APP_DIR, "logo512.png"), "rb") as f:
        return Response(content=f.read(), media_type="image/png")


@app.get("/source/list/", response_model=List[DataSourceSerialized])
async def get_source_list():
    return [source.serialize() for source in SOURCES.values()]


@app.post("/source/create/", response_model=DataSourceSerialized)
async def create(serialized: DataSourceSerialized):
    source = serialized.deserialize()
    return source.serialize()


@app.post("/source/update/", response_model=DataSourceSerialized)
async def update(serialized: DataSourceSerialized):
    source = serialized.deserialize(overwrite_existing=True)
    return source.serialize()


@app.post("/source/toggle-visible/", response_model=DataSourceSerialized)
async def toggle_visible(serialized: DataSourceSerialized):
    source = serialized.deserialize()
    source.visible = not source.visible
    return source.serialize()


@app.post("/source/nodes/list/", response_model=DataSourceSerialized)
async def load_nodes(serialized: DataSourceSerialized):
    source = serialized.deserialize()
    await source.load_nodes(limit=50)
    return source.serialize()


@app.post("/node/view/", response_model=Node)
async def view_data_instance(node: Node):
    source = SOURCES[node.source_id]
    await source.launch_node(node.data_id)
    return source.get_node(node.data_id)


@app.post("/node/kill/", response_model=Node)
async def kill_data_instance(node: Node):
    source = SOURCES[node.source_id]
    source.kill_node(node.data_id)
    return source.get_node(node.data_id)


class VisibilityChanges(BaseApiModel):
    show_sources: List[str]
    hide_sources: List[str]
    show_nodes: List[str]
    hide_nodes: List[str]


@app.post("/update-filters/", response_model=List[DataSourceSerialized])
async def update_filters(changes: VisibilityChanges):
    updated_source_ids = set(changes.show_sources + changes.hide_sources)
    for source_id in changes.show_sources:
        SOURCES[source_id].visible = True
    for source_id in changes.hide_sources:
        SOURCES[source_id].visible = False
    for data_id in changes.show_nodes:
        node = get_node_by_data_id(data_id)
        node.visible = True
        updated_source_ids.add(node.source_id)
    for data_id in changes.hide_nodes:
        node = get_node_by_data_id(data_id)
        node.visible = False
        updated_source_ids.add(node.source_id)
    return [SOURCES[source_id].serialize() for source_id in updated_source_ids]


def run():
    subprocess.Popen(["dtaledesktop_open_browser", f"http://{HOST}:{PORT}"])
    uvicorn.run(app, host=HOST, port=PORT, debug=True)


if __name__ == "__main__":
    run()
