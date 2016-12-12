#!/usr/bin/env python3

import oddschecker, sys

class bcolor:
    TEAM1 = '\033[92m'
    TEAM2 = '\033[93m'
    ENDC  = '\033[0m'

def run_app():
    color_team1, color_team2, color_endc = bcolor.TEAM1, bcolor.TEAM2, bcolor.ENDC
    if "--no-color" in sys.argv:
        color_team1 = ""
        color_team2 = ""
        color_endc = ""
    print("kicktipp oddschecker")
    odds = oddschecker.Odds()
    matches = odds.get_matches()
    total_points = 0
    for match in matches:
        score_propabilities = odds.get_score_propabilities(match)
        best_tipps = odds.find_best_tipp(score_propabilities)
        total_points = total_points + best_tipps[0][1]
        team0_name = match['teams'][0]
        team0_name = " "*(37-len(team0_name)) + team0_name

        score_left, score_right = best_tipps[0][0][0], best_tipps[0][0][1]
        if best_tipps[0][0][0] >= 4 and best_tipps[0][0][1] >= 4:
            score_left = "-"
            score_right = "-"
        print("{}{}{} {}:{} {}{}{}".format(color_team1, team0_name, color_endc, score_left, score_right, color_team2, match['teams'][1], color_endc))
    print(" "*36 + "--------")
    print(" "*17 + "Expected Point Gain: +" + str(total_points))

if __name__ == "__main__":
    run_app()
