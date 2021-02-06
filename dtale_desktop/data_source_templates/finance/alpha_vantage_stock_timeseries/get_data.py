import os
import re

import pandas as pd
from alpha_vantage.async_support.timeseries import TimeSeries

API_KEY = os.environ["ALPHA_VANTAGE_API_KEY"]


async def main(symbol: str) -> pd.DataFrame:
    """
    Given a symbol, retrieve that data and return it as a dataframe.
    """
    ts = TimeSeries(key=API_KEY, output_format="pandas")

    # Pick the option for your desired frequency (then delete the others)
    data, _ = await ts.get_intraday(symbol)
    data, _ = await ts.get_intraday_extended(symbol)
    data, _ = await ts.get_daily(symbol)
    data, _ = await ts.get_daily_adjusted(symbol)
    data, _ = await ts.get_weekly(symbol)
    data, _ = await ts.get_weekly_adjusted(symbol)
    data, _ = await ts.get_monthly(symbol)
    data, _ = await ts.get_monthly_adjusted(symbol)

    await ts.close()
    # Clean the column names, transforming ones like like "1. open" to "open"
    data.columns = [re.sub("^\d+\.\s", "", c) for c in data.columns]
    return data
