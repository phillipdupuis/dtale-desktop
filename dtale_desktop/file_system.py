import os
import shutil
from tempfile import mkdtemp
from typing import List, Callable, Tuple, Union

import pandas as pd
from typing_extensions import Literal

from dtale_desktop.settings import settings

__all__ = ["fs"]

_SENTINEL = object()

_TimeStampFormat = Literal["pandas", "unix_seconds", "unix_milliseconds"]


class _FileSystem:
    ROOT_DIR: str
    LOADERS_DIR: str
    ADDITIONAL_LOADERS_DIRS: List[str]
    CACHE_DIR: str
    DATA_DIR: str
    PROFILE_REPORTS_DIR: str

    _instance = _SENTINEL

    def __init__(self):
        if self._instance is not _SENTINEL:
            raise Exception("_Files is a singleton")

        self._instance = self
        self.ROOT_DIR = settings.ROOT_DIR
        self.LOADERS_DIR = os.path.join(self.ROOT_DIR, "loaders")
        self.ADDITIONAL_LOADERS_DIRS = settings.ADDITIONAL_LOADERS_DIRS
        self.CACHE_DIR = os.path.join(self.ROOT_DIR, "cache")
        self.DATA_DIR = os.path.join(self.CACHE_DIR, "data")
        self.PROFILE_REPORTS_DIR = os.path.join(self.CACHE_DIR, "profile_reports")

        self.create_directory(self.ROOT_DIR)
        self.create_directory(self.CACHE_DIR)
        self.create_directory(self.DATA_DIR)
        self.create_directory(self.PROFILE_REPORTS_DIR)
        self.create_python_package(self.LOADERS_DIR)

    def create_directory(self, path: str) -> None:
        os.makedirs(path, exist_ok=True)

    def create_file(self, path: str, contents: str = "") -> None:
        file = open(path, "w")
        file.write(contents)
        file.close()

    def delete_file(self, path: str) -> None:
        if os.path.exists(path):
            os.remove(path)

    def get_file_last_modified(
        self, path: str, format: _TimeStampFormat = "pandas",
    ) -> Union[int, pd.Timestamp]:
        ts = os.path.getmtime(path)
        if format == "pandas":
            return pd.Timestamp.fromtimestamp(ts)
        elif format == "unix_seconds":
            return int(ts)
        else:
            return int(ts) * 1000

    @staticmethod
    def _format_data_file_name(name: str):
        return name if name.endswith(".pkl") else f"{name}.pkl"

    def data_path(self, data_id: str) -> str:
        return os.path.join(self.DATA_DIR, self._format_data_file_name(data_id))

    def save_data(self, data_id: str, data: pd.DataFrame) -> None:
        data.to_pickle(self.data_path(data_id))

    def data_exists(self, data_id: str) -> bool:
        return os.path.exists(self.data_path(data_id))

    def read_data(self, data_id: str) -> pd.DataFrame:
        return pd.read_pickle(self.data_path(data_id))

    def delete_data(self, data_id: str) -> None:
        self.delete_file(self.data_path(data_id))

    @staticmethod
    def _format_profile_report_name(name: str):
        return name if name.endswith(".html") else f"{name}.html"

    def profile_report_path(self, data_id: str):
        return os.path.join(
            self.PROFILE_REPORTS_DIR, self._format_profile_report_name(data_id)
        )

    def profile_report_exists(self, data_id: str) -> bool:
        return os.path.exists(self.profile_report_path(data_id))

    def read_profile_report(self, data_id: str) -> str:
        with open(self.profile_report_path(data_id)) as f:
            return f.read()

    def delete_profile_report(self, data_id: str) -> None:
        self.delete_file(self.profile_report_path(data_id))

    def delete_all_cached_data(self, data_id: str) -> None:
        self.delete_data(data_id)
        self.delete_profile_report(data_id)

    def create_temp_directory(
        self, folder_name: str = "temp"
    ) -> Tuple[str, Callable[[], None]]:
        temp_dir = os.path.join(mkdtemp(), folder_name)
        return temp_dir, lambda: shutil.rmtree(temp_dir)

    def create_python_package(self, path: str) -> None:
        if not os.path.exists(path):
            self.create_directory(path)
            init_file = os.path.join(path, "__init__.py")
            if not os.path.exists(init_file):
                self.create_file(init_file)


fs = _FileSystem()
