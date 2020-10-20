import os
from pathlib import Path
from typing import Iterable


def main() -> Iterable[str]:
    root = os.path.expanduser("~")
    for p in Path(root).glob("*/*.json"):
        yield p.as_posix()
