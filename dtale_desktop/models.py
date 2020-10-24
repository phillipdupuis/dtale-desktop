import asyncio
import inspect
import os
from collections import OrderedDict as ordereddict
from hashlib import md5
from tempfile import mkdtemp
from typing import (
    List,
    Callable,
    Awaitable,
    Optional,
    Union,
    Dict,
)

import pandas as pd
from fastapi.exceptions import HTTPException
from pydantic.class_validators import root_validator
from pydantic.fields import Field

from dtale_desktop import dtale_app
from dtale_desktop.pydantic_utils import BaseApiModel
from dtale_desktop.source_code_tools import (
    LOADERS_DIR,
    get_source_file,
    create_package_name,
    create_data_source_package,
    move_data_source_package,
    load_data_source_package,
)

_ListPaths = Callable[..., Union[List[str], Awaitable[List[str]]]]
_GetData = Callable[[str], Union[pd.DataFrame, Awaitable[pd.DataFrame]]]
_SaveData = Callable[[str, pd.DataFrame], None]

SOURCES: Dict[str, "DataSource"] = ordereddict()


class DataSource:
    name: str
    package_name: str
    package_path: str
    visible: bool
    editable: bool
    nodes: Dict[str, "Node"]
    nodes_fully_loaded: bool
    error: Optional[str]
    _list_paths: _ListPaths
    _get_data: _GetData
    _save_data: Optional[_SaveData]

    def __init__(
        self,
        name: str,
        package_name: str,
        package_path: str,
        list_paths: _ListPaths,
        get_data: _GetData,
        save_data: Optional[_SaveData] = None,
        visible: Optional[bool] = True,
        editable: Optional[bool] = True,
    ):
        try:
            self.name = name
            self.package_name = package_name
            self.package_path = package_path
            self.visible = visible
            self.editable = editable
            self.nodes = ordereddict()
            self.nodes_fully_loaded = False
            self.error = None
            self._list_paths = list_paths
            self._get_data = get_data
            self._save_data = save_data
            self._path_generator = None
            self._validate()
        except BaseException as e:
            self.error = str(e)
            raise e

    @property
    def id(self) -> str:
        return self.package_name

    def _validate(self) -> None:
        if not inspect.isfunction(self._list_paths):
            raise Exception("list_paths must be a function")
        if not len(inspect.signature(self._list_paths).parameters) == 0:
            raise Exception("list_paths must be a function that takes 0 arguments")
        if not inspect.isfunction(self._get_data):
            raise Exception("get_data must be a function")
        if not len(inspect.signature(self._get_data).parameters) == 1:
            raise Exception("get_data must be a function that takes 1 argument")

    def register(self) -> None:
        SOURCES[self.id] = self

    def serialize(self) -> "DataSourceSerialized":
        return DataSourceSerialized(
            id=self.id,
            name=self.name,
            package_name=self.package_name,
            package_path=self.package_path,
            nodes=self.nodes,
            nodes_fully_loaded=self.nodes_fully_loaded,
            error=self.error,
            visible=self.visible,
            editable=self.editable,
            list_paths=get_source_file(self._list_paths),
            get_data=get_source_file(self._get_data),
            save_data=""
            if self._save_data is None
            else get_source_file(self._save_data),
        )

    async def _build_path_generator(self):
        if inspect.isgeneratorfunction(self._list_paths) or inspect.isasyncgen(
            self._list_paths
        ):
            self._path_generator = self._list_paths()
        elif inspect.iscoroutinefunction(self._list_paths):
            self._path_generator = (p for p in await self._list_paths())
        else:
            self._path_generator = (p for p in self._list_paths())

    async def load_nodes(self, limit: Optional[int] = None) -> None:
        try:
            if self._path_generator is None:
                await self._build_path_generator()
            count = 0
            if inspect.isasyncgen(self._path_generator):
                async for path in self._path_generator:
                    node = Node(source_id=self.id, path=path)
                    self.nodes[node.data_id] = node
                    count += 1
                    if count == limit:
                        return
            else:
                for path in self._path_generator:
                    node = Node(source_id=self.id, path=path)
                    self.nodes[node.data_id] = node
                    count += 1
                    if count == limit:
                        return
            self.nodes_fully_loaded = True
        except BaseException as e:
            self.error = str(e)
            raise HTTPException(status_code=400, detail=str(e))

    async def launch_node(self, data_id: str):
        node = self.nodes[data_id]
        try:
            instance = dtale_app.get_instance(data_id)
            if instance is None:
                if inspect.iscoroutinefunction(self._get_data):
                    data = await self._get_data(node.path)
                else:
                    data = self._get_data(node.path)
                instance = dtale_app.launch_instance(data=data, data_id=data_id)
                node.dtale_url = instance.main_url()
                node.dtale_charts_url = dtale_app.get_charts_url(data_id)
                # Wait for it to be running before we send a response
                while not instance.is_up():
                    await asyncio.sleep(1)
            return instance
        except BaseException as e:
            node.error = str(e)
            raise HTTPException(status_code=400, detail=str(e))

    def get_node(self, data_id: str) -> "Node":
        return self.nodes[data_id]

    def kill_node(self, data_id: str):
        node = self.nodes[data_id]
        try:
            dtale_app.kill_instance(data_id)
            node.dtale_url = None
            node.dtale_charts_url = None
        except BaseException as e:
            node.error = str(e)
            raise HTTPException(status_code=400, detail=str(e))

    def kill_all_nodes(self):
        try:
            for node in self.nodes.values():
                if node.dtale_url:
                    self.kill_node(node.data_id)
        except BaseException as e:
            self.error = str(e)
            raise HTTPException(status_code=400, detail=str(e))

    # async def save_data(self, path: str, data: pd.DataFrame):
    #     if self._save_data is not None:
    #         if asyncio.iscoroutine(self._save_data):
    #             return await self._save_data(path, data)
    #         return self._save_data(path, data)


class DataSourceSerialized(BaseApiModel):
    id_: str = Field(alias="id")
    name: str
    package_name: str = ""
    package_path: str = ""
    nodes: Dict[str, "Node"] = Field(default_factory=ordereddict)
    nodes_fully_loaded: bool = False
    error: Optional[str] = None
    visible: bool = True
    editable: bool = True
    list_paths: str
    get_data: str
    save_data: str

    @root_validator(pre=True)
    def validate_package_name(cls, values: dict):
        package_name = cls.get_by_name_or_alias(values, "package_name")
        if not package_name:
            display_name = cls.get_by_name_or_alias(values, "name")
            package_name = create_package_name(display_name)
            values["packageName"] = package_name
            values["id"] = package_name
        return values

    def _create_source_from_package(self, package) -> DataSource:
        return DataSource(
            name=package.metadata_module.display_name,
            package_name=self.package_name,
            package_path=package.path,
            list_paths=package.list_paths_module.main,
            get_data=package.get_data_module.main,
            visible=self.visible,
            editable=self.editable,
        )

    def _register_as_new_custom_source(self) -> DataSource:
        """
        Given a name and raw code for list_paths and get_data, attempt to convert it into functioning python
        code and then register it as a data source.

        This is first performed in a temporary directory, so we can validate the code before moving it into
        the actual loaders directory and potentially overwriting existing code that works.
        """
        try:
            temp_dir = os.path.join(mkdtemp(), self.package_name)
            test_package = create_data_source_package(
                temp_dir,
                self.package_name,
                list_paths_code=self.list_paths,
                get_data_code=self.get_data,
                metadata_code=f'display_name = """{self.name}"""',
            )
            # If the test package works without exceptions, assume that we are good to go - now do it for real.
            self._create_source_from_package(test_package)
            package = move_data_source_package(
                test_package, to_directory=LOADERS_DIR, remove_old=True
            )
            source = self._create_source_from_package(package)
            source.register()
            return source
        except BaseException as e:
            raise HTTPException(status_code=400, detail=str(e))

    def deserialize(self, overwrite_existing: bool = False) -> DataSource:
        if self.id_ not in SOURCES:
            self._register_as_new_custom_source()
        elif overwrite_existing:
            if not self.editable:
                raise HTTPException(
                    status_code=400, detail="This source can not be edited"
                )
            existing = SOURCES[self.id_].serialize()
            if (self.list_paths != existing.list_paths) or (
                self.get_data != existing.get_data
            ):
                SOURCES[self.id_].kill_all_nodes()
                self.nodes = ordereddict()
                self.nodes_fully_loaded = False
            self._register_as_new_custom_source()

        return SOURCES[self.id_]


class Node(BaseApiModel):
    source_id: str
    path: str
    data_id: str
    dtale_url: Optional[str] = None
    dtale_charts_url: Optional[str] = None
    error: Optional[str] = None
    visible: bool = True

    @root_validator(pre=True)
    def set_data_id_and_urls(cls, values):
        data_id = cls.get_by_name_or_alias(values, "data_id")
        if not data_id:
            m = md5()
            m.update(cls.get_by_name_or_alias(values, "source_id").encode("utf-8"))
            m.update(cls.get_by_name_or_alias(values, "path").encode("utf-8"))
            data_id = m.hexdigest()
            values["dataId"] = data_id
        return values


def register_existing_source(
    package_path: str, visible: bool = True, editable: bool = True
) -> None:
    """
    Given the path to a package containing files for list_paths.py, get_data.py, and metadata.py,
    attempt to register it as a data source.
    """
    try:
        package = load_data_source_package(package_path)
        source = DataSource(
            name=package.metadata_module.display_name,
            package_name=package.package_name,
            package_path=package_path,
            list_paths=package.list_paths_module.main,
            get_data=package.get_data_module.main,
            visible=visible,
            editable=editable,
        )
        source.register()
    except BaseException:
        pass


def get_node_by_data_id(data_id: str) -> Node:
    """
    Probably wouldn't need to do this if I was better organized, ah well
    """
    for source in SOURCES.values():
        if data_id in source.nodes:
            return source.nodes[data_id]


DataSourceSerialized.update_forward_refs()
Node.update_forward_refs()
