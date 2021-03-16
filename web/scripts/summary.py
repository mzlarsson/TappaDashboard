import os
import json
from functools import reduce

# 15 March 00:00:00 GMT+1
START_TIME = 1615762800

def get_summary(data_path):
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

    if os.path.exists(data_path):

        with open(data_path, "r") as data_file:
            data = json.load(data_file)

        days = (data["timestamp"] - START_TIME) / (24*60*60)

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

            player["average_steps"] = round(player["steps"] / days)
            player_team["players"].append(player)
            result["players"].append(player)

        for team in result["teams"]:
            team["total_steps"] = reduce(lambda sum, el: sum + el["steps"], team["players"], 0)
            team["total_dist"] = reduce(lambda sum, el: sum + el["distance"], team["players"], 0)
            team["average_steps"] = round(team["total_steps"] / len(team["players"]) / days)
            team["average_dist"] = round(team["total_dist"] / len(team["players"]) / days, 1)

        result["stats"]["days"] = round(days, 2)
        result["stats"]["total_steps"] = reduce(lambda sum, el: sum + el["total_steps"], result["teams"], 0)
        result["stats"]["total_dist"] = round(reduce(lambda sum, el: sum + el["total_dist"], result["teams"], 0), 1)
        result["stats"]["average_steps"] = round(result["stats"]["total_steps"] / days / len(result["players"]))
        

    result["teams"].sort(key=lambda t: t["average_steps"], reverse=True)

    return result
            