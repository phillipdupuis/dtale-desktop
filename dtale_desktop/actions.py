from typing import Optional, List

from pydantic.fields import Field
from typing_extensions import Literal

from dtale_desktop.models import DataSourceSerialized, Node
from dtale_desktop.pydantic_utils import BaseApiModel
from dtale_desktop.settings import settings
from dtale_desktop.websocket_connections import websocket_connection_manager


class _Action(BaseApiModel):
    async def broadcast(self, exclude: Optional[List[int]] = None) -> None:
        await websocket_connection_manager.broadcast(
            _Message(payload=self).json(), exclude=exclude
        )


class _Message(BaseApiModel):
    type_: str = Field(default="action", alias="type")
    payload: _Action


class UpdateSettings(_Action):
    type_: Literal["UPDATE_SETTINGS"] = Field("UPDATE_SETTINGS", alias="type")
    settings: settings.Serialized


class AddSources(_Action):
    type_: Literal["ADD_SOURCES"] = Field("ADD_SOURCES", alias="type")
    sources: List[DataSourceSerialized]


class UpdateSource(_Action):
    type_: Literal["UPDATE_SOURCE"] = Field("UPDATE_SOURCE", alias="type")
    source: DataSourceSerialized


class SetSourceUpdating(_Action):
    type_: Literal["SET_SOURCE_UPDATING"] = Field("SET_SOURCE_UPDATING", alias="type")
    source_id: str
    updating: bool = True


class UpdateNode(_Action):
    type_: Literal["UPDATE_NODE"] = Field("UPDATE_NODE", alias="type")
    node: Node


class SetNodeUpdating(_Action):
    type_: Literal["SET_NODE_UPDATING"] = Field("SET_NODE_UPDATING", alias="type")
    data_id: str
    updating: bool = True
