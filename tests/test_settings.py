from starlette.routing import NoMatchFound
from fastapi.routing import APIWebSocketRoute
from .utils import reload_app

import pytest


def get_url_path(name: str, **path_params: str) -> str:
    return reload_app().url_path_for(name, **path_params)


def test_disable_add_data_sources(monkeypatch):
    assert get_url_path("create_source") == "/source/create/"
    monkeypatch.setenv("DTALEDESKTOP_DISABLE_ADD_DATA_SOURCES", "true")
    with pytest.raises(NoMatchFound):
        get_url_path("create_source")


def test_disable_edit_data_sources(monkeypatch):
    assert get_url_path("update_source") == "/source/update/"
    monkeypatch.setenv("DTALEDESKTOP_DISABLE_EDIT_DATA_SOURCES", "true")
    with pytest.raises(NoMatchFound):
        get_url_path("update_source")


def test_disable_edit_layout(monkeypatch):
    assert get_url_path("update_source_layout") == "/source/update-layout/"
    monkeypatch.setenv("DTALEDESKTOP_DISABLE_EDIT_LAYOUT", "true")
    with pytest.raises(NoMatchFound):
        get_url_path("update_source_layout")


def test_disable_profile_reports(monkeypatch):
    app = reload_app()
    assert len([r for r in app.routes if "profile-report" in r.path]) == 4
    monkeypatch.setenv("DTALEDESKTOP_DISABLE_PROFILE_REPORTS", "true")
    app = reload_app()
    assert len([r for r in app.routes if "profile-report" in r.path]) == 0


def test_enable_websocket_connections(monkeypatch):
    app = reload_app()
    assert not any(isinstance(r, APIWebSocketRoute) for r in app.routes)
    monkeypatch.setenv("DTALEDESKTOP_ENABLE_WEBSOCKET_CONNECTIONS", "true")
    app = reload_app()
    assert any(isinstance(r, APIWebSocketRoute) for r in app.routes)
