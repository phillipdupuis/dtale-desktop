import os
from pathlib import Path
from typing import Iterable


def main() -> Iterable[str]:
    root = os.path.expanduser("~")
    for extension in ["xls", "xlsx", "xlsm", "xlsb", "odf", "ods", "odt"]:
        for p in Path(root).glob(f"*/*.{extension}"):
            yield p.as_posix()
