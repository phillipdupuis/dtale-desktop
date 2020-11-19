from typing import List, Optional

from fastapi import APIRouter, Header

from dtale_desktop.actions import AddSources, UpdateSource
from dtale_desktop.models import DataSourceSerialized, DataSourceLayoutChange, SOURCES
from dtale_desktop.settings import settings

router = APIRouter()


@router.get("/source/list/", response_model=AddSources)
async def get_source_list():
    return AddSources(sources=[source.serialize() for source in SOURCES.values()])


@router.get("/source/{source_id}/load-nodes/", response_model=UpdateSource)
async def get_source_nodes(source_id: str, limit: Optional[int] = None):
    source = SOURCES[source_id]
    await source.load_nodes(limit=limit)
    response = UpdateSource(source=source.serialize())
    return response


if not settings.DISABLE_ADD_DATA_SOURCES:

    @router.post("/source/create/", response_model=AddSources)
    async def create_source(
        serialized: DataSourceSerialized, client_id: int = Header(None)
    ):
        source = serialized.deserialize()
        response = AddSources(sources=[source.serialize()])
        if settings.ENABLE_WEBSOCKET_CONNECTIONS:
            await response.broadcast(exclude=[client_id])
        return response


if not settings.DISABLE_EDIT_DATA_SOURCES:

    @router.post("/source/update/", response_model=UpdateSource)
    async def update_source(
        serialized: DataSourceSerialized, client_id: int = Header(None)
    ):
        source = serialized.deserialize(overwrite_existing=True)
        response = UpdateSource(source=source.serialize())
        if settings.ENABLE_WEBSOCKET_CONNECTIONS:
            await response.broadcast(exclude=[client_id])
        return response


if not settings.DISABLE_EDIT_LAYOUT:

    @router.post("/source/update-layout/", response_model=List[UpdateSource])
    async def update_source_layout(changes: List[DataSourceLayoutChange]):
        return [UpdateSource(source=change.apply()) for change in changes]
