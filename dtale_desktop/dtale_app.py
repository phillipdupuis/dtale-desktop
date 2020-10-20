import _thread
from typing import Union
from urllib.parse import urljoin

import requests
import dtale
import pandas as pd
from dtale import utils as _utils
from dtale import views as _views

dtale.app.initialize_process_props()

DTALE_HOST = dtale.app.ACTIVE_HOST

DTALE_PORT = dtale.app.ACTIVE_PORT

DTALE_URL = _utils.build_url(DTALE_PORT, DTALE_HOST)

app = dtale.app.build_app(DTALE_URL, host=DTALE_HOST)


def _start_server():
    app.run(host=DTALE_HOST, port=DTALE_PORT, threaded=True)


def _start_server_if_needed():
    if not _views.is_up(DTALE_URL):
        _thread.start_new_thread(_start_server, ())


def get_instance(data_id: Union[str, int]) -> Union[dtale.app.DtaleData, None]:
    return dtale.app.get_instance(data_id)


def launch_instance(
    data: pd.DataFrame, data_id: Union[str, int]
) -> dtale.app.DtaleData:
    instance = dtale.app.startup(
        DTALE_URL, data=data, data_id=data_id, ignore_duplicate=True
    )
    _start_server_if_needed()
    return instance


def get_charts_url(data_id: Union[str, int]) -> str:
    return urljoin(DTALE_URL, f"/charts/{data_id}")


def kill_instance(data_id: Union[str, int]) -> None:
    requests.get(urljoin(DTALE_URL, f"/dtale/cleanup/{data_id}"))
