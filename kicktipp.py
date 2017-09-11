#!/usr/bin/env python3

import urllib.request
from bs4 import BeautifulSoup

####################
# HELPER FUNCTIONS #
####################

def load_soup(url):
    return BeautifulSoup(urllib.request.urlopen(url).read().decode(), 'html.parser')

#####################################################################################

MAIN_PAGE = "https://sports.bwin.com/de/sports/4/43/wetten/bundesliga"

if __name__ == "__main__":
    print("kicktipp predictor, Copyright (c) 2017 Marcel Kleinfeller")

    # PART 1: Finding next games
    print("[1] Searching for bundesliga games ...")
    soup = load_soup(MAIN_PAGE)
    raw_matches = soup.select("a.mb-event-details-buttons__button-link")
    matches = []
    for raw_match in raw_matches:
        href = raw_match["href"]
        if href[:11] == "/de/sports/":
            matches.append(href)
    print("[2] Found {} upcoming matches ...".format(len(matches)))
    # PART 2: Modifying match urls
    for i in range(0, len(matches)):
        match = matches[i]
        match = match.replace("/wetten/", "/35/wetten/")
        match = match.replace("/de/sports/events/4/43/", "https://sports.bwin.com/de/sports/events/4/43/")
        matches[i] = match

    # PART 3: Parsing odds
    odds = []
    cnt = 3
    for match in matches:
        m_odds = [] # Odds, just for this match
        print("[{}] Parsing odds for match {}".format(cnt, match))
        soup = load_soup(match)
        soup = soup.select("table.marketboard-event-with-header__markets-list")[0]
        buttons = soup.select("button.mb-option-button__button")
        for button in buttons:
            divs = button.select("div")
            score = divs[0].string.strip()
            odd   = divs[1].string.strip()
            if len(score) == 3:
                m_odds.append(((int(score[0]), int(score[2])), float(odd)))
            else:
                m_odds.append(((-1, -1), float(odd)))
        odds.append((match, m_odds))
        cnt = cnt + 1

    # PART 4: Calculating best odds for each game
    for match in odds:
        print("[{}] Predicting results for match: {}".format(cnt, match[0]))
        odds = match[1]
        corr_factor = 0
        # 4.1 Normalizing propabilities
        for odd in odds:
            corr_factor = corr_factor + 1/odd[1]
        best_tip = "n/a"
        best_odd = 0

        for l in range(0, 5):
            for r in range(0, 5):
                rating = 0
                for odd in odds:
                    if odd[0] == (-1, -1):
                        continue
                    prop = 1/(odd[1] * corr_factor)
                    ll = odd[0][0]
                    rr = odd[0][1]
                    
                    if ll == l and rr == r:
                        rating = rating + 4 * prop
                    elif ll - rr == l - r:
                        rating = rating + 3 * prop
                    elif (ll > rr and l > r) or (ll == rr and l == r) or (ll < rr and l < r):
                        rating = rating + 2 * prop
                if rating > best_odd:
                    best_tip = "{}:{}".format(l, r)
                    best_odd = rating
        print("----> {}".format(best_tip), best_odd)
        cnt = cnt + 1
