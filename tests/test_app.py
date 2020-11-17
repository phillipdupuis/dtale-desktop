import asyncio
import os

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def execute_async_task():
    loop = asyncio.new_event_loop()
    return lambda task: loop.run_until_complete(task)


@pytest.fixture
def read_file():
    def _reader(path: str, mode="r"):
        with open(path, mode) as f:
            return f.read()

    return _reader


@pytest.fixture
def app(monkeypatch, tmpdir):
    """
    Sets environment variables before importing the app.
    """
    monkeypatch.setenv("DTALEDESKTOP_ROOT_DIR", tmpdir.strpath)

    from dtale_desktop import app

    return app


@pytest.fixture
def client(app):
    return TestClient(app.app)


def test_root_dir(app, tmpdir):
    assert app.settings.ROOT_DIR == tmpdir.strpath


def test_frontend_view(app, client):
    response = client.get("/")
    with open(os.path.join(app.settings.REACT_APP_DIR, "index.html")) as f:
        assert response.text == f.read()


def test_health(client):
    response = client.get("/health/")
    assert response.status_code == 204


_list_paths_sample = """
def main():
    yield from (str(x) for x in range(99))
"""

_get_data_sample = """
import pandas as pd

def main(path: str):
    return pd.DataFrame({"foo": [1, 2], "bar": [3, 4]})
"""

_mock_source_json = {
    "name": "mock_name",
    "listPaths": _list_paths_sample,
    "getData": _get_data_sample,
}


def test_create_source_success(app, client, read_file):
    from dtale_desktop.models import SOURCES
    from dtale_desktop.file_system import fs

    response = client.post("/source/create/", json=_mock_source_json)
    assert response.status_code == 200

    data = response.json()
    source = data["sources"][0]
    assert source["name"] == _mock_source_json["name"]
    assert source["listPaths"] == _mock_source_json["listPaths"]
    assert source["getData"] == _mock_source_json["getData"]
    assert source["id"] in SOURCES

    # Check if the package was built appropriately
    assert source["packagePath"] == os.path.join(fs.LOADERS_DIR, source["packageName"])
    assert _list_paths_sample == read_file(
        os.path.join(source["packagePath"], "list_paths.py")
    )
    assert _get_data_sample == read_file(
        os.path.join(source["packagePath"], "get_data.py")
    )


def test_load_source_nodes(app, client):
    from dtale_desktop.models import SOURCES

    initial = client.post("/source/create/", json=_mock_source_json).json()["sources"][
        0
    ]
    source = SOURCES[initial["id"]]
    assert len(initial["nodes"]) == 0
    assert len(source.nodes) == 0
    assert len(initial["nodes"]) == len(source.nodes)
    assert initial["nodesFullyLoaded"] is False

    after_one = client.get(f"/source/{source.id}/load-nodes/?limit=30").json()["source"]
    assert len(after_one["nodes"]) == 30
    assert len(source.nodes) == 30
    assert after_one["nodesFullyLoaded"] is False

    after_two = client.get(f"/source/{source.id}/load-nodes/").json()["source"]
    assert len(after_two["nodes"]) == len(source.nodes)
    assert len(after_two["nodes"]) > len(after_one["nodes"])
    assert after_two["nodesFullyLoaded"] is True

    after_three = client.get(f"/source/{source.id}/load-nodes/").json()["source"]
    assert after_three == after_two
