import os

import cd_api
import discord_helper


def main():
    api = cd_api.CDApi(os.environ.get("CD_USERNAME"), os.environ.get("CD_PASSWORD"))
    results = api.get_exam_results()
    discord_helper.send_result_embed(results[1], api.get_result_dist(results[1]))


if __name__ == "__main__":
    main()
