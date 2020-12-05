import asyncio
import subprocess
import sys
from argparse import ArgumentParser


def open_browser():
    import requests
    import time
    import webbrowser

    parser = ArgumentParser()
    parser.add_argument("url", type=str)

    target_url = parser.parse_args().url
    health_check_url = f"{target_url}/health/"

    with requests.session() as session:
        running = False
        attempts = 0
        while True:
            try:
                if session.get(health_check_url).status_code == 204:
                    running = True
            except:
                pass

            if running:
                webbrowser.open(target_url)
                sys.exit(0)
            elif attempts == 60:
                sys.exit("Dtale Desktop did not seem to launch; shutting down.")
            else:
                attempts += 1
                time.sleep(3)


def build_profile_report():
    import pandas as pd
    from pandas_profiling import ProfileReport

    parser = ArgumentParser()
    parser.add_argument("data_path", type=str)
    parser.add_argument("output_path", type=str)
    parser.add_argument("title", type=str)
    args = parser.parse_args()

    data = pd.read_pickle(args.data_path)
    report = ProfileReport(data, title=args.title)
    report.to_file(args.output_path)
    sys.exit(0)


def launch_browser_opener(url: str) -> None:
    subprocess.Popen(["dtaledesktop_open_browser", url])


async def execute_profile_report_builder(
    data_path: str, output_path: str, title: str
) -> None:
    args = ["dtaledesktop_profile_report", data_path, output_path, title]
    builder = subprocess.Popen(args)
    while builder.poll() is None:
        await asyncio.sleep(1)
