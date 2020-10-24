import os
import re
import inspect
import shutil
from importlib.util import spec_from_file_location, module_from_spec
from typing import Callable, Optional
from types import ModuleType
from pydantic import BaseModel


ROOT = os.path.join(os.path.expanduser("~"), ".dtaledesktop")

LOADERS_DIR = os.path.join(ROOT, "loaders")


def create_python_file(path: str, code: str = "") -> None:
    file = open(path, "w")
    file.write(code)
    file.close()


def create_python_directory(path: str) -> None:
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        init_file = os.path.join(path, "__init__.py")
        if not os.path.exists(init_file):
            create_python_file(init_file)


# Make sure CUSTOM_ROOT and CUSTOM_LOADERS are set up, we need em
create_python_directory(ROOT)
create_python_directory(LOADERS_DIR)


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
    if not os.path.exists(os.path.join(LOADERS_DIR, base_name)):
        return base_name
    else:
        count = 1
        while os.path.exists(os.path.join(LOADERS_DIR, f"{base_name}{count}")):
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
    create_python_directory(path)
    create_python_file(os.path.join(path, "list_paths.py"), list_paths_code)
    create_python_file(os.path.join(path, "get_data.py"), get_data_code)
    create_python_file(os.path.join(path, "metadata.py"), metadata_code)
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
