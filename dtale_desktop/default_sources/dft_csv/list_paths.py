import os
from pathlib import Path
from typing import Iterable


def main() -> Iterable[str]:
    root = os.path.expanduser("~")
    for p in Path(root).glob("*/*.csv"):
        yield p.as_posix()
