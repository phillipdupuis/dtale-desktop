import os
import typing


def stringify(value: typing.Any) -> str:
    """
    Helper function for converting python types into values that can be stored as environment variables.
    """
    if isinstance(value, list):
        return ",".join(item for item in value)
    else:
        return str(value)


def run(
    *,
    host: str = None,
    port: int = None,
    dtale_port: int = None,
    root_dir: str = None,
    additional_loaders_dirs: typing.List[str] = None,
    exclude_default_loaders: bool = None,
    disable_add_data_sources: bool = None,
    disable_edit_data_sources: bool = None,
    disable_edit_layout: bool = None,
    disable_profile_reports: bool = None,
    disable_open_browser: bool = None,
    disable_dtale_cell_edits: bool = None,
    enable_websocket_connections: bool = None,
) -> None:
    """
    Alternative entrypoint for starting it up
    """
    for env_var_name, value in [
        ("HOST", host),
        ("PORT", port),
        ("DTALE_PORT", dtale_port),
        ("ROOT_DIR", root_dir),
        ("ADDITIONAL_LOADERS_DIRS", additional_loaders_dirs),
        ("EXCLUDE_DEFAULT_LOADERS", exclude_default_loaders),
        ("DISABLE_ADD_DATA_SOURCES", disable_add_data_sources),
        ("DISABLE_EDIT_DATA_SOURCES", disable_edit_data_sources),
        ("DISABLE_EDIT_LAYOUT", disable_edit_layout),
        ("DISABLE_PROFILE_REPORTS", disable_profile_reports),
        ("DISABLE_OPEN_BROWSER", disable_open_browser),
        ("DISABLE_DTALE_CELL_EDITS", disable_dtale_cell_edits),
        ("ENABLE_WEBSOCKET_CONNECTIONS", enable_websocket_connections),
    ]:
        if value is not None:
            os.environ[f"DTALEDESKTOP_{env_var_name}"] = stringify(value)

    from dtale_desktop import app

    app.run()
