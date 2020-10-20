import pandas as pd


def main(path: str) -> pd.DataFrame:
    return pd.read_excel(path)
