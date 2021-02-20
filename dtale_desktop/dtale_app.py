import _thread
from typing import Union
from urllib.parse import urljoin

import dtale
import pandas as pd
from dtale import global_state, utils as _utils

from dtale_desktop.settings import settings

dtale.app.initialize_process_props(host=settings.HOST, port=settings.DTALE_PORT)

DTALE_HOST = dtale.app.ACTIVE_HOST

DTALE_PORT = dtale.app.ACTIVE_PORT

DTALE_INTERNAL_ROOT_URL = _utils.build_url(DTALE_PORT, DTALE_HOST)

DTALE_EXTERNAL_ROOT_URL = settings.DTALE_ROOT_URL or DTALE_INTERNAL_ROOT_URL

app = dtale.app.build_app(DTALE_INTERNAL_ROOT_URL, host=DTALE_HOST, reaper_on=False)

global_state.set_app_settings({"hide_shutdown": True})


def run():
    _thread.start_new_thread(
        app.run, (), dict(host=DTALE_HOST, port=DTALE_PORT, threaded=True)
    )


def _format_data_id(data_id: Union[str, int]) -> int:
    """
    Dtale-desktop was previously using hexadecimal strings as data IDs, but new versions of dtale (>1.35)
    now only support integers as data IDs.

    This function will serve as a temporary adapter, ensuring that all communication with the dtale app
    uses integers.
    """
    if isinstance(data_id, str):
        return int(data_id, 16)
    return data_id


def get_instance(data_id: Union[str, int]) -> Union[dtale.app.DtaleData, None]:
    data_id = _format_data_id(data_id)
    return dtale.app.get_instance(data_id)


def launch_instance(data: pd.DataFrame, data_id: str) -> dtale.app.DtaleData:
    return dtale.app.startup(
        DTALE_INTERNAL_ROOT_URL,
        data=data,
        data_id=_format_data_id(data_id),
        ignore_duplicate=True,
        allow_cell_edits=not settings.DISABLE_DTALE_CELL_EDITS,
    )


def get_main_url(data_id: str) -> str:
    data_id = _format_data_id(data_id)
    return urljoin(DTALE_EXTERNAL_ROOT_URL, f"/dtale/main/{data_id}")


def get_charts_url(data_id: str) -> str:
    data_id = _format_data_id(data_id)
    return urljoin(DTALE_EXTERNAL_ROOT_URL, f"/dtale/charts/{data_id}")


def get_describe_url(data_id: str) -> str:
    data_id = _format_data_id(data_id)
    return urljoin(DTALE_EXTERNAL_ROOT_URL, f"/dtale/popup/describe/{data_id}")


def get_correlations_url(data_id: str) -> str:
    data_id = _format_data_id(data_id)
    return urljoin(DTALE_EXTERNAL_ROOT_URL, f"/dtale/popup/correlations/{data_id}")


def kill_instance(data_id: str) -> None:
    data_id = _format_data_id(data_id)
    global_state.cleanup(data_id)
