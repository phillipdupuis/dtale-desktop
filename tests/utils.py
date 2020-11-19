import sys
from fastapi import FastAPI


def reload_app() -> FastAPI:
    """
    Imports the app as if from scratch.

    This allows settings to be refreshed in between tests, which is important because a lot of functionality
    varies depending on what the settings are at import time.
    """
    for module_name in list(sys.modules.keys()):
        if "dtale_desktop" in module_name and "dtale_desktop.tests" not in module_name:
            del sys.modules[module_name]

    # Clear the _FUNCS global in pydantic.class_validators, otherwise upon reimport it will raise a bunch of
    # "duplicate validator" exceptions.
    from pydantic.class_validators import _FUNCS

    _FUNCS.clear()

    # Now we can finally import the dtale_desktop web app. It will be rebuilt using the current setttings.
    from dtale_desktop.app import app

    return app
