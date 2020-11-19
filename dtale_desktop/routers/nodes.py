from fastapi import APIRouter, Header, Depends

from dtale_desktop.actions import UpdateNode, SetNodeUpdating
from dtale_desktop.models import Node, get_node_by_data_id
from dtale_desktop.settings import settings

router = APIRouter()


@router.get("/node/view/{data_id}/", response_model=UpdateNode)
async def node_view_dtale_instance(
    node: Node = Depends(get_node_by_data_id), client_id: int = Header(None)
):
    if settings.ENABLE_WEBSOCKET_CONNECTIONS:
        await SetNodeUpdating(data_id=node.data_id).broadcast(exclude=[client_id])
        await node.launch_dtale()
        response = UpdateNode(node=node)
        await response.broadcast(exclude=[client_id])
    else:
        await node.launch_dtale()
        response = UpdateNode(node=node)
    return response


@router.delete("/node/kill/{data_id}/", response_model=UpdateNode)
async def node_kill_dtale_instance(
    node: Node = Depends(get_node_by_data_id), client_id: int = Header(None)
):
    node.shut_down()
    response = UpdateNode(node=node)
    if settings.ENABLE_WEBSOCKET_CONNECTIONS:
        await response.broadcast(exclude=[client_id])
    return response


@router.delete("/node/clear-cache/{data_id}/", response_model=UpdateNode)
async def node_clear_cache(
    node: Node = Depends(get_node_by_data_id), client_id: int = Header(None)
):
    await node.clear_cache()
    response = UpdateNode(node=node)
    if settings.ENABLE_WEBSOCKET_CONNECTIONS:
        await response.broadcast(exclude=[client_id])
    return response
