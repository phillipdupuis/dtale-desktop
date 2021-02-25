from hashlib import md5
import pandas as pd
import pytest


@pytest.fixture
def dtale_app(monkeypatch, tmpdir):
    """
    Sets environment variables before importing the app.
    """
    monkeypatch.setenv("DTALEDESKTOP_ROOT_DIR", tmpdir.strpath)
    monkeypatch.setenv("DTALEDESKTOP_HOST", "localhost")
    monkeypatch.setenv("DTALEDESKTOP_DTALE_PORT", "54321")

    from dtale_desktop import dtale_app as _dtale_app

    return _dtale_app


@pytest.fixture
def data():
    return pd.DataFrame([{"a": 1, "b": 2, "c": 3}])


@pytest.fixture
def data_id():
    return md5("abc123".encode("utf8")).hexdigest()


def test_launch_instance(dtale_app, data, data_id):
    instance = dtale_app.launch_instance(data=data, data_id=data_id)
    assert (
        instance.main_url()
        == f"{dtale_app.DTALE_EXTERNAL_ROOT_URL}/dtale/main/{dtale_app._format_data_id(data_id)}"
    )
    pd.testing.assert_frame_equal(data, instance.data)


def test_get_instance(dtale_app, data, data_id):
    _ = dtale_app.launch_instance(data=data, data_id=data_id)
    instance = dtale_app.get_instance(data_id)
    pd.testing.assert_frame_equal(data, instance.data)


def test_urls_valid(dtale_app, data, data_id):
    instance = dtale_app.launch_instance(data=data, data_id=data_id)
    main_url = dtale_app.get_main_url(data_id)
    charts_url = dtale_app.get_charts_url(data_id)
    describe_url = dtale_app.get_describe_url(data_id)
    correlations_url = dtale_app.get_correlations_url(data_id)

    assert main_url == instance.main_url()

    with dtale_app.app.test_client(port=54321) as c:
        for url in (main_url, charts_url, describe_url, correlations_url):
            assert c.get(url).status_code == 200


def test_kill_instance(dtale_app, data, data_id):
    with dtale_app.app.test_client(port=54321) as c:
        dtale_app.launch_instance(data=data, data_id=data_id)
        main_url = dtale_app.get_main_url(data_id)
        assert c.get(main_url).status_code == 200

        dtale_app.kill_instance(data_id)
        assert c.get(main_url).status_code != 200
