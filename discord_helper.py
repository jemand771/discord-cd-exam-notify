import json
import os
import time
import urllib.parse

import discord_webhook

import model


def add_empty_field(embed: discord_webhook.DiscordEmbed, inline=True):
    embed.add_embed_field(name="­", value="­", inline=inline)


def send_result_embed(mscore: model.MScore, mscoredist: model.MScoreDist = None):
    hook = discord_webhook.DiscordWebhook(
        url=os.environ.get("DISCORD_HOOK"),
        rate_limit_retry=True,
        content=""
    )
    date_embed = discord_webhook.DiscordEmbed(
        title=f"Prüfung {mscore.module}",
        description="Ein neues Prüfungsergebnis wurde auf Campus Dual veröffentlicht.",
        color="0070A3"
    )
    date_embed.set_timestamp(int(time.time()))
    date_embed.add_embed_field(name="Semester", value=f"{mscore.year}.{mscore.period}")
    date_embed.add_embed_field(name="Bewertungsdatum", value=mscore.date_score)
    date_embed.add_embed_field(name="Veröffentlichungsdatum", value=mscore.date_publish)

    if mscoredist is None:
        score_embed = discord_webhook.DiscordEmbed(
            description="Campus dual stellt zu dieser Prüfung keine weiteren Daten bereit.",
            color="FCBE04"
        )
    else:
        score_embed = discord_webhook.DiscordEmbed(
            color="FCBE04"
        )
        score_embed.add_embed_field(name="Abgeschlossen", value=f"{mscoredist.done}")
        score_embed.add_embed_field(name="Offen", value=f"{mscoredist.open}")
        score_embed.add_embed_field(name="Gesamt", value=f"{mscoredist.total}\n­")
        for i in range(8):
            if i < 5:
                score_embed.add_embed_field(**mscoredist.get_embed_dict(i))
            if i % 2:
                add_empty_field(score_embed)

        bold_config = [{
            "ticks": {
                "beginAtZero": True,
                "fontFamily": "Uni sans",
                "fontStyle": "bold"
            }
        }]
        score_embed.set_image(
            url="https://quickchart.io/chart?c=" + urllib.parse.quote_plus(
                json.dumps({
                    "type": "bar",
                    "data": {
                        "labels": list(range(1, 6)),
                        "datasets": [
                            {
                                "label": "Prüfungsergebnis (Note 1-5)",
                                "data": mscoredist.results,
                                "backgroundColor": ["#0070A3"] * 4 + ["#FCBE04"]
                            }
                        ]
                    },
                    "options": {
                        "legend": {
                            "display": False
                        },
                        "scales": {
                            "yAxes": bold_config,
                            "xAxes": bold_config
                        }
                    }
                })
            ))

    hook.add_embed(date_embed)
    hook.add_embed(score_embed)
    hook.execute()
