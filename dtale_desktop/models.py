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
from dtale_desktop.file_system import fs
from dtale_desktop.logger import get_logger
from dtale_desktop.pydantic_utils import BaseApiModel
from dtale_desktop.settings import settings
from dtale_desktop.source_code_tools import (
    get_source_file,
    create_package_name,
    create_data_source_package,
    move_data_source_package,
    load_data_source_package,
)
from dtale_desktop.subprocesses import execute_profile_report_builder

logger = get_logger()

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
    sort_value: int
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
        sort_value: Optional[int] = None,
    ):
        try:
            self.name = name
            self.package_name = package_name
            self.package_path = package_path
            self.visible = visible
            self.editable = False if settings.DISABLE_EDIT_DATA_SOURCES else editable
            self.sort_value = sort_value
            self.nodes = ordereddict()
            self.nodes_fully_loaded = False
            self.error = None
            self._list_paths = list_paths
            self._get_data = get_data
            self._save_data = save_data
            self._path_generator = None
            self._validate()
        except Exception as e:
            self.error = str(e)
            raise e

    @property
    def id(self) -> str:
        return md5(self.package_path.encode()).hexdigest()

    def _validate(self) -> None:
        """
        list_paths and get_data are typically user-provided code, so we run a few basic checks
        to make sure that they appear to have the correct function signature(s).
        """
        if not inspect.isfunction(self._list_paths):
            raise Exception("list_paths must be a function")
        if not len(inspect.signature(self._list_paths).parameters) == 0:
            raise Exception("list_paths must be a function that takes 0 arguments")
        if not inspect.isfunction(self._get_data):
            raise Exception("get_data must be a function")
        if not len(inspect.signature(self._get_data).parameters) == 1:
            raise Exception("get_data must be a function that takes 1 argument")

    def register(self) -> None:
        """
        Adds a source to the registry, so it shows up in the front-end views.
        If a sort_value has not already been specified, put it at the bottom of the list.
        """
        if self.sort_value is None:
            self.sort_value = max((0, *(x.sort_value for x in SOURCES.values()))) + 1
        SOURCES[self.id] = self

    def serialize(self) -> "DataSourceSerialized":
        """
        Generates a serialized version of this instance that can be sent to the front end as json.
        """
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
            sort_value=self.sort_value,
            list_paths=get_source_file(self._list_paths),
            get_data=get_source_file(self._get_data),
            save_data=""
            if self._save_data is None
            else get_source_file(self._save_data),
        )

    async def _build_path_generator(self):
        """
        Adapter that takes whatever code was provided for _list_paths and turns it into a
        generator so we can load nodes in chunks (rather than all at once).
        """
        if inspect.isgeneratorfunction(self._list_paths) or inspect.isasyncgen(
            self._list_paths
        ):
            self._path_generator = self._list_paths()
        elif inspect.iscoroutinefunction(self._list_paths):
            self._path_generator = (p for p in await self._list_paths())
        else:
            self._path_generator = (p for p in self._list_paths())

    async def load_nodes(self, limit: Optional[int] = None) -> None:
        """
        Load the next batch of nodes, adding them to self.nodes (or all the nodes, if limit=None)
        """
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
        except Exception as e:
            self.error = str(e)
            raise HTTPException(status_code=500, detail=str(e))

    def get_node(self, data_id: str) -> "Node":
        """
        Returns node by id. Not terribly useful.
        """
        return self.nodes[data_id]

    def kill_all_nodes(self):
        """
        Shut down any active dtale instances for this source.
        """
        try:
            for node in self.nodes.values():
                if node.dtale_url:
                    node.shut_down()
        except Exception as e:
            self.error = str(e)
            raise HTTPException(status_code=500, detail=str(e))


class DataSourceSerialized(BaseApiModel):
    id_: str = Field(default="", alias="id")
    name: str
    package_name: str = ""
    package_path: str = ""
    nodes: Dict[str, "Node"] = Field(default_factory=ordereddict)
    nodes_fully_loaded: bool = False
    error: Optional[str] = None
    visible: bool = True
    editable: bool = True
    sort_value: Optional[int] = None
    list_paths: str
    get_data: str
    save_data: str = ""

    @root_validator(pre=True)
    def validate_package_name(cls, values: dict) -> dict:
        """
        Defines package_name if not provided.
        """
        package_name = cls.get_by_name_or_alias(values, "package_name")
        if not package_name:
            display_name = cls.get_by_name_or_alias(values, "name")
            package_name = create_package_name(display_name)
            values["packageName"] = package_name
        return values

    def _create_source_from_package(self, package) -> DataSource:
        """
        Given a package, attempts to create a new DataSource from it.
        Note that the source won't be registered yet, that needs to be done explicitly.
        """
        return DataSource(
            name=package.metadata_module.display_name,
            package_name=self.package_name,
            package_path=package.path,
            list_paths=package.list_paths_module.main,
            get_data=package.get_data_module.main,
            visible=self.visible,
            editable=self.editable,
            sort_value=self.sort_value,
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
                test_package, to_directory=fs.LOADERS_DIR, remove_old=True
            )
            source = self._create_source_from_package(package)
            source.register()
            self.id_ = source.id
            return source
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    def deserialize(self, overwrite_existing: bool = False) -> DataSource:
        """
        Returns the corresponding DataSource.
        The back end is treated as the universal source of truth UNLESS overwrite_existing is set to True.
        """
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


class DataSourceLayoutChange(BaseApiModel):
    id_: str
    visible: bool
    sort_value: int

    def apply(self) -> DataSourceSerialized:
        source = SOURCES[self.id_]
        source.visible = self.visible
        source.sort_value = self.sort_value
        return source.serialize()


class Node(BaseApiModel):
    source_id: str
    path: str
    data_id: str
    dtale_url: Optional[str] = None
    dtale_charts_url: Optional[str] = None
    dtale_describe_url: Optional[str] = None
    dtale_correlations_url: Optional[str] = None
    error: Optional[str] = None
    visible: bool = True
    sort_value: int
    last_cached_at: Optional[int] = None  # unix timestamp in milliseconds

    @root_validator(pre=True)
    def set_computed_values(cls, values: dict) -> dict:
        """
        Compute values for data_id, last_cached_at, and sort_value if they are not already specified.
        """
        data_id = cls.get_by_name_or_alias(values, "data_id")
        source_id = cls.get_by_name_or_alias(values, "source_id")

        if not data_id:
            m = md5()
            m.update(source_id.encode())
            m.update(cls.get_by_name_or_alias(values, "path").encode())
            data_id = m.hexdigest()
            values["dataId"] = data_id

        if not cls.get_by_name_or_alias(values, "last_cached_at") and fs.data_exists(
            data_id
        ):
            values["lastCachedAt"] = fs.get_file_last_modified(
                fs.data_path(data_id), format="unix_milliseconds"
            )

        if not cls.get_by_name_or_alias(values, "sort_value"):
            existing_nodes = SOURCES[source_id].nodes.values()
            sort_value = max((0, *(x.sort_value for x in existing_nodes))) + 1
            values["sortValue"] = sort_value

        return values

    @property
    def source(self) -> DataSource:
        return SOURCES[self.source_id]

    async def get_data(self, ignore_cache=False) -> pd.DataFrame:
        """
        Load the data for this node, also adding it to the cache.
        """
        if fs.data_exists(self.data_id) and not ignore_cache:
            return fs.read_data(self.data_id)
        else:
            if inspect.iscoroutinefunction(self.source._get_data):
                data = await self.source._get_data(self.path)
            else:
                data = self.source._get_data(self.path)
            fs.save_data(self.data_id, data)
            self.last_cached_at = fs.get_file_last_modified(
                fs.data_path(self.data_id), format="unix_milliseconds"
            )
            return data

    async def launch_dtale(self):
        """
        Get or start up the dtale instance for this node's data
        """
        try:
            instance = dtale_app.get_instance(self.data_id)
            if instance is None:
                data = await self.get_data()
                instance = dtale_app.launch_instance(data=data, data_id=self.data_id)
                self.dtale_url = dtale_app.get_main_url(self.data_id)
                self.dtale_charts_url = dtale_app.get_charts_url(self.data_id)
                self.dtale_describe_url = dtale_app.get_describe_url(self.data_id)
                self.dtale_correlations_url = dtale_app.get_correlations_url(
                    self.data_id
                )
                # Wait for it to be running before we send a response
                while not instance.is_up():
                    await asyncio.sleep(1)
            return instance
        except Exception as e:
            # The 'error' attribute set here will be displayed in the front-end
            logger.exception(str(e))
            self.error = str(e)

    def shut_down(self):
        """
        Shut down the running dtale instance
        """
        try:
            dtale_app.kill_instance(self.data_id)
            self.dtale_url = None
            self.dtale_charts_url = None
            self.dtale_describe_url = None
            self.dtale_correlations_url = None
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def build_profile_report(self) -> None:
        """
        Build a pandas profile report. This is done in a separate process because it can be quite slow.
        """
        try:
            if not fs.profile_report_exists(self.data_id):
                await self.get_data()
                await execute_profile_report_builder(
                    data_path=fs.data_path(self.data_id),
                    output_path=fs.profile_report_path(self.data_id),
                    title=f"{self.source.name} - {self.path}",
                )
                if not fs.profile_report_exists(self.data_id):
                    raise Exception(
                        "The profile report failed to build for some reason"
                    )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def clear_cache(self) -> None:
        """
        Clear this node's cached data.
        """
        try:
            fs.delete_all_cached_data(self.data_id)
            self.last_cached_at = None
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


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
    except Exception as e:
        logger.exception(str(e))


def get_node_by_data_id(data_id: str) -> Node:
    """
    Reusable as dependency for taking a data_id path parameter and returning the Node instance.
    """
    for source in SOURCES.values():
        if data_id in source.nodes:
            return source.nodes[data_id]


DataSourceSerialized.update_forward_refs()
Node.update_forward_refs()
