"""
Environment variables that can be used to configure settings:

- DTALEDESKTOP_ROOT_DIR:
    path, the location where all persistent data (loaders, cached data, etc.) will be stored.
    By default this is ~/.dtaledesktop
- DTALEDESKTOP_ADDITIONAL_LOADERS_DIRS:
    comma-separated list of directory paths that should be scanned for data sources upon startup.
- DTALEDESKTOP_EXCLUDE_DEFAULT_LOADERS:
    "true" if the default loaders should not be included in the list of data sources.
    These are the loaders which look for json, csv, and excel files in your home directory.

- DTALEDESKTOP_DISABLE_ADD_DATA_SOURCES:
    "true" if the "Add Data Source" button should not be shown.
- DTALEDESKTOP_DISABLE_EDIT_DATA_SOURCES:
    "true" if editing existing data sources should not be allowed.
- DTALEDESKTOP_DISABLE_EDIT_LAYOUT:
    "true" if users should not be allowed to edit what sources are/are not visible or what order they're in.
- DTALEDESKTOP_DISABLE_PROFILE_REPORTS:
    "true" if the "Profile" option (which builds a pandas_profiling report) should not be shown.
    This is resource-intensive and currently a bit buggy (it launches a subprocess).
- DTALEDESKTOP_DISABLE_OPEN_BROWSER
    "true" if browser should not open upon startup
- DTALEDESKTOP_DISABLE_DTALE_CELL_EDITS
    "true" if editing cells in dtale should be disabled.

- DTALEDESKTOP_ENABLE_WEBSOCKET_CONNECTIONS
    "true" if real-time updates should be pushed to clients via websocket connection.
    This is only useful/necessary if you are running it as a service and multiple users can access it simultaneously.

- DTALEDESKTOP_HOST
- DTALEDESKTOP_PORT
- DTALEDESKTOP_ROOT_URL
    allows you to override how urls are built, which can be useful if you're running it as a service (ie not locally).

- DTALEDESKTOP_DTALE_PORT
- DTALEDESKTOP_DTALE_ROOT_URL
    allows you to override how urls intended for dtale are built.
    Added in order to support running dtaledesktop in k8s - by using different domain names for the main app and the
    dtale app, the ingress controller can use that (domain name) to determine which port requests should be sent to.

"""
import os
import socket
from typing import List, Optional
from enum import Enum

from dtale_desktop.pydantic_utils import BaseApiModel

__all__ = ["settings"]

_SENTINEL = object()


class EnvVars(str, Enum):
    ROOT_DIR = "DTALEDESKTOP_ROOT_DIR"
    ADDITIONAL_LOADERS_DIRS = "DTALEDESKTOP_ADDITIONAL_LOADERS_DIRS"
    EXCLUDE_DEFAULT_LOADERS = "DTALEDESKTOP_EXCLUDE_DEFAULT_LOADERS"

    DISABLE_ADD_DATA_SOURCES = "DTALEDESKTOP_DISABLE_ADD_DATA_SOURCES"
    DISABLE_EDIT_DATA_SOURCES = "DTALEDESKTOP_DISABLE_EDIT_DATA_SOURCES"
    DISABLE_EDIT_LAYOUT = "DTALEDESKTOP_DISABLE_EDIT_LAYOUT"
    DISABLE_PROFILE_REPORTS = "DTALEDESKTOP_DISABLE_PROFILE_REPORTS"
    DISABLE_OPEN_BROWSER = "DTALEDESKTOP_DISABLE_OPEN_BROWSER"
    DISABLE_DTALE_CELL_EDITS = "DTALEDESKTOP_DISABLE_DTALE_CELL_EDITS"

    ENABLE_WEBSOCKET_CONNECTIONS = "DTALEDESKTOP_ENABLE_WEBSOCKET_CONNECTIONS"

    HOST = "DTALEDESKTOP_HOST"
    PORT = "DTALEDESKTOP_PORT"
    ROOT_URL = "DTALEDESKTOP_ROOT_URL"

    DTALE_PORT = "DTALEDESKTOP_DTALE_PORT"
    DTALE_ROOT_URL = "DTALEDESKTOP_DTALE_ROOT_URL"


def _env_bool(var_name: str, default: bool = False) -> bool:
    return os.getenv(var_name, "").lower() == ("true" if default is False else "false")


def _env_int(var_name: str, default: Optional[int] = None) -> Optional[int]:
    try:
        return int(os.getenv(var_name))
    except:
        return default


class _Settings:
    ROOT_DIR: str
    ADDITIONAL_LOADERS_DIRS: List[str]
    EXCLUDE_DEFAULT_LOADERS: bool

    REACT_APP_DIR: str
    TEMPLATES_DIR: str

    DISABLE_ADD_DATA_SOURCES: bool
    DISABLE_EDIT_DATA_SOURCES: bool
    DISABLE_EDIT_LAYOUT: bool
    DISABLE_PROFILE_REPORTS: bool
    DISABLE_OPEN_BROWSER: bool
    DISABLE_DTALE_CELL_EDITS: bool

    ENABLE_WEBSOCKET_CONNECTIONS: bool

    _HOST: str
    _PORT: int
    _ROOT_URL: str

    DTALE_PORT: Optional[int]
    DTALE_ROOT_URL: Optional[str]

    _instance = _SENTINEL

    def __init__(self):
        if self._instance is not _SENTINEL:
            raise Exception("_Settings is a singleton")
        self._setup()

    def refresh(self) -> None:
        self._setup()

    def _setup(self) -> None:
        """
        Set the value for each setting based on enviroment variables.
        Separate from __init__ so the settings can be refreshed programmatically (if desired).
        """
        self._instance = self

        self.ROOT_DIR = os.getenv(
            EnvVars.ROOT_DIR, os.path.join(os.path.expanduser("~"), ".dtaledesktop"),
        )
        self.ADDITIONAL_LOADERS_DIRS = [
            x
            for x in os.getenv(EnvVars.ADDITIONAL_LOADERS_DIRS, "").split(",")
            if x != ""
        ]
        self.EXCLUDE_DEFAULT_LOADERS = _env_bool(EnvVars.EXCLUDE_DEFAULT_LOADERS)

        self.REACT_APP_DIR = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "frontend", "build"
        )

        self.TEMPLATES_DIR = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "templates"
        )

        self.DISABLE_ADD_DATA_SOURCES = _env_bool(EnvVars.DISABLE_ADD_DATA_SOURCES)
        self.DISABLE_EDIT_DATA_SOURCES = _env_bool(EnvVars.DISABLE_EDIT_DATA_SOURCES)
        self.DISABLE_EDIT_LAYOUT = _env_bool(EnvVars.DISABLE_EDIT_LAYOUT)
        self.DISABLE_PROFILE_REPORTS = _env_bool(EnvVars.DISABLE_PROFILE_REPORTS)
        self.DISABLE_OPEN_BROWSER = _env_bool(EnvVars.DISABLE_OPEN_BROWSER)
        self.DISABLE_DTALE_CELL_EDITS = _env_bool(EnvVars.DISABLE_DTALE_CELL_EDITS)

        self.ENABLE_WEBSOCKET_CONNECTIONS = _env_bool(
            EnvVars.ENABLE_WEBSOCKET_CONNECTIONS
        )

        self._HOST = os.getenv(EnvVars.HOST, None)
        self._PORT = _env_int(EnvVars.PORT, None)
        self._ROOT_URL = os.getenv(EnvVars.ROOT_URL, None)

        self.DTALE_PORT = _env_int(EnvVars.DTALE_PORT, None)
        self.DTALE_ROOT_URL = os.getenv(EnvVars.DTALE_ROOT_URL, None)

    @property
    def HOST(self) -> str:
        if self._HOST is None:
            try:
                self._HOST = socket.gethostbyname("localhost")
            except BaseException:
                self._HOST = socket.gethostbyname(socket.gethostname())
        return self._HOST

    @property
    def PORT(self) -> int:
        if self._PORT is None:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(("", 0))
            self._PORT = sock.getsockname()[1]
            sock.close()
        return self._PORT

    @property
    def ROOT_URL(self) -> str:
        if self._ROOT_URL is None:
            self._ROOT_URL = f"http://{self.HOST}:{self.PORT}"
        return self._ROOT_URL

    class Serialized(BaseApiModel):
        disable_add_data_sources: bool
        disable_edit_data_sources: bool
        disable_edit_layout: bool
        disable_profile_reports: bool
        enable_websocket_connections: bool

    def serialize(self) -> Serialized:
        return self.Serialized(
            disable_add_data_sources=self.DISABLE_ADD_DATA_SOURCES,
            disable_edit_data_sources=self.DISABLE_EDIT_DATA_SOURCES,
            disable_edit_layout=self.DISABLE_EDIT_LAYOUT,
            disable_profile_reports=self.DISABLE_PROFILE_REPORTS,
            enable_websocket_connections=self.ENABLE_WEBSOCKET_CONNECTIONS,
        )


settings = _Settings()
