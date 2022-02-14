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

    # error cases:
    # * dist is none -> ?
    # * not 5 results -> it's not a grade, don't bother displaying
    # * sum is 0: "nobody took part" or: data is hidden
    score_embed = discord_webhook.DiscordEmbed(
        color="FCBE04"
    )
    add_mark_distribution = mscoredist is not None and len(mscoredist.results) == 5 and sum(mscoredist.results) > 0
    add_admission_stats = mscoredist is not None and mscoredist.done + mscoredist.open > 0

    if add_admission_stats:
        score_embed.add_embed_field(name="Abgeschlossen", value=f"{mscoredist.done}")
        score_embed.add_embed_field(name="Offen", value=f"{mscoredist.open}")
        score_embed.add_embed_field(
            name="Gesamt",
            # fancy trick: only add a new line if something follows after this
            value=f"{mscoredist.total}" + ("\n­" if add_mark_distribution else "")
        )

    if not add_mark_distribution:
        if add_admission_stats:
            score_embed.description = "Campus dual stellt zu dieser Prüfung keine Notenverteilung bereit."
        else:
            score_embed.description = "Campus dual stellt zu dieser Prüfung keine Belegungsdaten bereit."
    else:
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
                json.dumps(
                    {
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
                    }
                )
            )
        )

    hook.add_embed(date_embed)
    hook.add_embed(score_embed)
    hook.execute()
