"""
Simple script that will open the browser once dtale desktop is up and running.
It's a separate script because it will run in a separate process.
"""
import sys
import time
import webbrowser

import requests


def main():
    url = sys.argv[1]
    health_check_url = f"{url}/health/"
    count = 0
    while True:
        time.sleep(1)
        response = requests.get(health_check_url)
        if response.status_code == 204:
            break
        count += 1
        if count == 60:
            print("Dtale Desktop did not seem to launch; shutting down.")
            return
    webbrowser.open(url)
