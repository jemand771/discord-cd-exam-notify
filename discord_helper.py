import json
import os
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
    date_embed.add_embed_field(name="Semester", value=semester_format(mscore.year, mscore.period))
    date_embed.add_embed_field(name="Beurteilung", value=mscore.date_score)
    date_embed.add_embed_field(name="Bekanntgabe", value=mscore.date_publish)

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
        score_embed.add_embed_field(name="Gesamt", value=str(mscoredist.total))

    if not add_mark_distribution:
        if add_admission_stats:
            score_embed.description = "Campus dual stellt zu dieser Prüfung keine Notenverteilung bereit."
        else:
            score_embed.description = "Campus dual stellt zu dieser Prüfung keine Belegungsdaten bereit."
    else:
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


def semester_format(year, period):
    if period == "001":
        sw = "Winter"
    elif period == "002":
        sw = "Sommer"
    else:
        sw = "??"
        print(f"warning: failed to evaulate period '{period}'")
    try:
        year = int(year)
        year_str = f"{year - 1}/{year}"
    except ValueError:
        print(f"warning: failed to evaulate year '{year}'")
        year_str = f"??/{year}"
    return f"{sw} {year_str}"
