import asyncio
import os

from fastapi import Depends, APIRouter, Header
from fastapi.exceptions import HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from dtale_desktop.actions import UpdateNode, SetNodeUpdating
from dtale_desktop.file_system import fs
from dtale_desktop.models import Node, get_node_by_data_id
from dtale_desktop.settings import settings

router = APIRouter()


@router.get("/node/profile-report/{data_id}/", response_class=HTMLResponse)
async def noad_profile_report_loading_page(data_id: str):
    """
    This one is a bit weird because it is being opened in a new tab.
    We do this because building a profile report can take a LONG time, and we don't want to block the main app.

    We return a static loading page which, when the window is ready, will fetch /node/build-profile-report/{data_id}/.
    Once the report is built, the response will provide a url for viewing it.
    The promise resolves by redirecting the user to that URL.
    """
    with open(os.path.join(settings.TEMPLATES_DIR, "loading_profile_report.html")) as f:
        return f.read()


@router.get("/node/build-profile-report/{data_id}/", response_class=RedirectResponse)
async def node_build_profile_report(
    node: Node = Depends(get_node_by_data_id), client_id: int = Header(None)
):
    """
    Build a profile report in the backend.
    Once it's finally ready (which may take a while) the user will be redirected to a page for viewing the report.
    """
    if settings.ENABLE_WEBSOCKET_CONNECTIONS:
        await SetNodeUpdating(data_id=node.data_id).broadcast(exclude=[client_id])
        await node.build_profile_report()
        await UpdateNode(node=node).broadcast(exclude=[client_id])
    else:
        await node.build_profile_report()
    return RedirectResponse(url=f"/node/view-profile-report/{node.data_id}/")


@router.get("/node/watch-profile-report-builder/{data_id}/", response_model=UpdateNode)
async def node_watch_profile_report_builder(data_id: str):
    """
    Allows the front-end to update the display information once a profile report builds successfully.
    Necessary because the profile report entails opening a separate tab.
    """
    time_waited = 0
    while time_waited < 600:
        if fs.profile_report_exists(data_id):
            return UpdateNode(node=get_node_by_data_id(data_id))
        await asyncio.sleep(5)
        time_waited += 5
    raise HTTPException(
        status_code=400, detail="The report either failed to generate or took too long"
    )


@router.get("/node/view-profile-report/{data_id}/", response_class=HTMLResponse)
async def node_view_profile_report(data_id: str):
    """
    Displays the profile report. These pages can be pretty big, so it can be a bit clunky sometimes.
    """
    return fs.read_profile_report(data_id)
