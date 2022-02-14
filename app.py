import json
import os
import signal
import time

import cd_api
import discord_helper

import requests

DATA_FILE = "data.json"


class Killer:

    def __init__(self):
        self.stop = False
        signal.signal(signal.SIGINT, self.do_stop)
        signal.signal(signal.SIGTERM, self.do_stop)

    def do_stop(self, *_):
        self.stop = True


KILLER = Killer()


def main():
    # surpress insecure request warnings (campus dual needs verify=False for some reason)
    requests.packages.urllib3.disable_warnings(
        requests.packages.urllib3.exceptions.InsecureRequestWarning
    )
    while True:
        print("performing check")
        check_once()
        print(f"done, sleeping for {(sleep_duration := int(os.environ.get('CHECK_INTERVAL', '900')))}s.")
        for i in range(sleep_duration):
            time.sleep(1)
            if KILLER.stop:
                print("sleep interrupted")
                exit()


def check_once():
    try:
        with open(DATA_FILE) as f:
            known_modules = json.load(f)
            first_run = False
    except FileNotFoundError:
        known_modules = []
        first_run = True

    api = cd_api.CDApi(os.environ.get("CD_USERNAME"), os.environ.get("CD_PASSWORD"))
    results = api.get_exam_results()
    print(f"found {len(results)} results")
    for r in results:
        if r.module in known_modules:
            continue
        if KILLER.stop:
            exit()
        if not first_run:
            print("sending discord notification for", r.module)
            discord_helper.send_result_embed(r, api.get_result_dist(r))
        known_modules.append(r.module)

    with open(DATA_FILE, "w") as f:
        json.dump(known_modules, f, indent=2)


if __name__ == "__main__":
    main()
