import _thread
from typing import Union
from urllib.parse import urljoin

import dtale
import pandas as pd
import requests
from dtale import utils as _utils

from dtale_desktop.settings import settings

dtale.app.initialize_process_props(host=settings.HOST, port=settings.DTALE_PORT)

DTALE_HOST = dtale.app.ACTIVE_HOST

DTALE_PORT = dtale.app.ACTIVE_PORT

DTALE_INTERNAL_ROOT_URL = _utils.build_url(DTALE_PORT, DTALE_HOST)

DTALE_EXTERNAL_ROOT_URL = settings.DTALE_ROOT_URL or DTALE_INTERNAL_ROOT_URL

app = dtale.app.build_app(DTALE_INTERNAL_ROOT_URL, host=DTALE_HOST, reaper_on=False)


def run():
    _thread.start_new_thread(
        app.run, (), dict(host=DTALE_HOST, port=DTALE_PORT, threaded=True)
    )


def get_instance(data_id: Union[str, int]) -> Union[dtale.app.DtaleData, None]:
    return dtale.app.get_instance(data_id)


def launch_instance(data: pd.DataFrame, data_id: str) -> dtale.app.DtaleData:
    return dtale.app.startup(
        DTALE_INTERNAL_ROOT_URL,
        data=data,
        data_id=data_id,
        ignore_duplicate=True,
        allow_cell_edits=not settings.DISABLE_DTALE_CELL_EDITS,
        hide_shutdown=True,
    )


def get_main_url(data_id: str) -> str:
    return urljoin(DTALE_EXTERNAL_ROOT_URL, f"/dtale/main/{data_id}")


def get_charts_url(data_id: str) -> str:
    return urljoin(DTALE_EXTERNAL_ROOT_URL, f"/charts/{data_id}")


def get_describe_url(data_id: str) -> str:
    return urljoin(DTALE_EXTERNAL_ROOT_URL, f"/dtale/popup/describe/{data_id}")


def get_correlations_url(data_id: str) -> str:
    return urljoin(DTALE_EXTERNAL_ROOT_URL, f"/dtale/popup/correlations/{data_id}")


def kill_instance(data_id: str) -> None:
    requests.get(urljoin(DTALE_EXTERNAL_ROOT_URL, f"/dtale/cleanup/{data_id}"))
