import os
import json
from functools import reduce
from datetime import datetime, date, timezone, timedelta

# 15 March 00:00:00 GMT+1
START_TIME = 1615762800

def get_summary(data_folder):
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

        days = int((data["timestamp"] - START_TIME) / (24*60*60))

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

            # ----------- REASONING REGARDING DIFF STEPS ----------------------------
            # AllTimeSteps[n] = sum(day.Steps) for n first days
            # This means for example AllTimeSteps[2] = (DailySteps[0] + DailySteps[1] + DailySteps[2]) / Days
            # The yesterday array contains AllTimeSteps[1] = (DailySteps[0] + DailySteps[1] + 0) / days
            # The today array contains AllTimeSteps[2] = (DailySteps[0] + DailySteps[1] + DailySteps[2]) / days
            # In order to retrieve DailySteps[2], we see that it must be that
            # AllTimeSteps[2] - AllTimeSteps[1] = DailySteps[2] / days
            # Hence it should be that
            # DailySteps[2] = (AllTimeSteps[2] - AllTimeSteps[1]) * days
            # This also means we will lose more and more precision the longer time goes (since the value is scaled down).
            # Day 2 the precision is every two steps. Day 27 we can only get as close as 27 steps. Sadface.
            # -----------------------------------------------------------------------
            player["diff_steps"] = (player["steps"] - player_yesterday.get("steps", 0)) * days
            player_team["players"].append(player)
            result["players"].append(player)

        for team in result["teams"]:
            team["total_steps"] = reduce(lambda sum, el: sum + el["steps"]*days, team["players"], 0)
            team["total_dist"] = reduce(lambda sum, el: sum + el["distance"], team["players"], 0)
            team["average_steps"] = round(team["total_steps"] / len(team["players"]) / days)
            team["average_dist"] = round(team["total_dist"] / len(team["players"]) / days, 1)

        result["stats"]["days"] = days
        result["stats"]["total_steps"] = reduce(lambda sum, el: sum + el["total_steps"], result["teams"], 0)
        result["stats"]["total_dist"] = round(reduce(lambda sum, el: sum + el["total_dist"], result["teams"], 0), 1)
        result["stats"]["average_steps"] = round(result["stats"]["total_steps"] / days / len(result["players"]))
        result["stats"]["last_update"] = datetime.fromtimestamp(data["timestamp"], timezone(timedelta(hours=1))).strftime('%Y-%m-%d %H:%M:%S')

    result["teams"].sort(key=lambda t: t["average_steps"], reverse=True)

    return result
            
