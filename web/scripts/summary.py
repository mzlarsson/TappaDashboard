import os
import json
from functools import reduce
from datetime import datetime, date, timezone, timedelta

# 15 March 00:00:00 GMT+1
START_TIME = 1615762800

def get_summary(data_folder, strategy=None):
    result = {
        "teams": [],
        "players": [],
        "stats": {
            "days": 0,
            "total_steps": 0,
            "total_dist": 0,
            "average_steps": 0
        }
    }

    data_path = "%s/result.json" % (data_folder)
    if os.path.exists(data_path):

        with open(data_path, "r") as data_file:
            data = json.load(data_file)

        yesterday_date = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
        yesterday_file = "%s/%s.json" % (data_folder, yesterday_date)
        if os.path.exists(yesterday_file):
            with open(yesterday_file, "r") as data_file:
                yesterday = json.load(data_file)
        else:
            yesterday = {}

        actual_days = (data["timestamp"] - START_TIME) / (24*60*60)
        full_days = int(actual_days)
        if strategy == "pessimistic":
            days = int(actual_days) + 1
            day_decimals = 0
        elif strategy == "exact":
            days = actual_days
            day_decimals = 2
        else:
            days = int(actual_days)
            day_decimals = 0

        for player in data["players"]:

            # Hack since Isabelle does not seem to be in the right team
            if player["team"] is None and player["name"].startswith("Isabelle"):
                player["team"] = "Let\u2019s walk"

            player_team = None
            for team in result["teams"]:
                if team["name"] == player["team"]:
                    player_team = team
                    break

            if not player_team:
                result["teams"].append({
                    "name": player["team"],
                    "players": []
                })
                player_team = result["teams"][-1]

            player_yesterday = {}
            player_search = list(filter(lambda p: p["name"] == player["name"], yesterday.get("players", [])))
            if player_search:
                player_yesterday = player_search[0]

            # Tappa gives us average value as of full days. E.g. On the third day we get -> 2 days
            all_time_steps = player["steps"] * full_days
            all_time_steps_midnight = player_yesterday.get("steps", 0) * full_days

            player["total_steps"] = all_time_steps
            player["diff_steps"] = all_time_steps - all_time_steps_midnight
            player["average_steps"] = round(all_time_steps / days)

            player_team["players"].append(player)
            result["players"].append(player)

        for team in result["teams"]:
            team["total_steps"] = reduce(lambda sum, el: sum + el["total_steps"], team["players"], 0)
            team["total_dist"] = reduce(lambda sum, el: sum + el["distance"], team["players"], 0)
            team["average_steps"] = round(team["total_steps"] / len(team["players"]) / days)
            team["average_dist"] = round(team["total_dist"] / len(team["players"]) / days, 1)

        result["stats"]["actual_days"] = actual_days
        result["stats"]["days"] = round(days, day_decimals)
        result["stats"]["total_steps"] = reduce(lambda sum, el: sum + el["total_steps"], result["teams"], 0)
        result["stats"]["total_dist"] = round(reduce(lambda sum, el: sum + el["total_dist"], result["teams"], 0), 1)
        result["stats"]["average_steps"] = round(result["stats"]["total_steps"] / days / len(result["players"]))
        result["stats"]["last_update"] = datetime.fromtimestamp(data["timestamp"], timezone(timedelta(hours=1))).strftime('%Y-%m-%d %H:%M:%S')

    result["teams"].sort(key=lambda t: t["average_steps"], reverse=True)

    return result
            
