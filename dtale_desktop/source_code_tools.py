import inspect
import os
import re
import shutil
from importlib.util import spec_from_file_location, module_from_spec, find_spec
from types import ModuleType
from typing import Callable, Optional

from pydantic import BaseModel

from dtale_desktop.file_system import fs


def get_source_file(func: Callable) -> str:
    with open(inspect.getsourcefile(func)) as f:
        return f.read()
    # could also consider inspect.getsource(inspect.getmodule(func))


def load_module_from_path(path: str, *, name: str = None) -> ModuleType:
    name = name or re.sub(r"\W+", "", path.replace(" ", "_"))
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_package_name(display_name: str) -> str:
    base_name = re.sub(r"\W+", "", display_name.replace(" ", "_"))
    if find_spec(base_name) is None:
        return base_name
    else:
        count = 1
        while os.path.exists(os.path.join(fs.LOADERS_DIR, f"{base_name}{count}")):
            count += 1
        return f"{base_name}{count}"


class DataSourcePackage(BaseModel):
    path: str
    package_name: str
    list_paths_module: ModuleType
    get_data_module: ModuleType
    metadata_module: ModuleType

    class Config:
        arbitrary_types_allowed = True


def load_data_source_package(
    path: str, package_name: Optional[str] = None
) -> DataSourcePackage:
    package_name = package_name or os.path.split(path)[1]
    return DataSourcePackage(
        path=path,
        package_name=package_name,
        list_paths_module=load_module_from_path(os.path.join(path, "list_paths.py")),
        get_data_module=load_module_from_path(os.path.join(path, "get_data.py")),
        metadata_module=load_module_from_path(os.path.join(path, "metadata.py")),
    )


def create_data_source_package(
    directory: str,
    package_name: str,
    list_paths_code: str,
    get_data_code: str,
    metadata_code: str,
) -> DataSourcePackage:
    path = os.path.join(directory, package_name)
    fs.create_python_package(path)
    fs.create_file(os.path.join(path, "list_paths.py"), list_paths_code)
    fs.create_file(os.path.join(path, "get_data.py"), get_data_code)
    fs.create_file(os.path.join(path, "metadata.py"), metadata_code)
    return load_data_source_package(path, package_name)


def move_data_source_package(
    package: DataSourcePackage, to_directory: str, remove_old: bool = True
) -> DataSourcePackage:
    new_path = os.path.join(to_directory, package.package_name)
    if os.path.exists(new_path):
        shutil.rmtree(new_path)
    shutil.copytree(package.path, new_path)
    if remove_old:
        shutil.rmtree(package.path)
    return load_data_source_package(new_path, package.package_name)
