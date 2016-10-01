import urllib.request
import statistics
from bs4 import BeautifulSoup

ODDS_BASE_URL = "http://www.oddschecker.com/"

def load_page(url):
    return urllib.request.urlopen("{}{}".format(ODDS_BASE_URL, url)).read().decode()

# Stolen from Wikibooks or so
def levenshtein(s1, s2):
    if len(s1) < len(s2):
        return levenshtein(s2, s1)
    # len(s1) >= len(s2)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1 # j+1 instead of j since previous_row and current_row are one character longer
            deletions = current_row[j] + 1       # than s2
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

class Odds(object):
    def __init__(self):
        self.__event = "football/germany/bundesliga"

    def get_matches(self):
        html_doc = load_page(self.__event)
        soup = BeautifulSoup(html_doc, 'html.parser')
        matches = soup.select('tr.match-on')
        match_response = []

        for match in matches:
            teams = match.select('span.fixtures-bet-name')
            api_url = "{}correct-score".format(match.select('td.betting > a')[0]['href'][1:-6])
            m = {
                'teams' : (teams[0].string, teams[2].string),
                'match_url': api_url
            }
            match_response.append(m)
        return match_response

    def normalize_data_name(self, match, data_name):
        data_name = data_name.strip()
        split_index = data_name.rfind(" ")
        team_name = data_name[:split_index]
        score_split = data_name[split_index+1:].split("-")
        if not score_split[0].lower() == 'score':
            score = (int(score_split[0]), int(score_split[1]))

            team0_distance = levenshtein(match['teams'][0], team_name)
            team1_distance = levenshtein(match['teams'][1], team_name)
            if team1_distance < team0_distance:
                score = (score[1], score[0])
            return score
        else:
            return "_"

    def get_score_propabilities(self, match):
        html_doc = load_page(match['match_url'])
        soup = BeautifulSoup(html_doc, 'html.parser')
        rows = soup.select('tbody#t1 tr.eventTableRow')
        odds_matrix = []
        for row in rows:
            cols = row.select('td')
            matrix_row = []
            data_name = cols[0].select('span')[0]['data-name']
            score = self.normalize_data_name(match, data_name)
            for col in cols[1:]:
                if col.string and col.string.strip():
                    matrix_row.append(float(col['data-odig']))
                """ Uncomment this if you dont take median first!!!
                else:
                    matrix_row.append(None)
                """
            odds_matrix.append({
                'score' : score,
                'odds' : 1/statistics.median(matrix_row)
            })
        # summarizing the odds matrix
        corr = 0
        for odd in odds_matrix:
            if odd['score'] != '_':
                corr = corr + odd['odds']

        odds = []
        for odd in odds_matrix:
            if odd['score'] != '_':
                odds.append((odd['score'], odd['odds']/corr))
        return odds

    def find_best_tipp(self, odds):
        ratings = []
        for t1_i in range(0, 5):
            for t2_i in range(0, 5):
                p_2, p_3, p_4 = 0, 0, 0
                for odd in odds:
                    if odd[0][0] == t1_i and odd[0][1] == t2_i:
                        p_4 = p_4 + odd[1]
                    elif odd[0][0] - odd[0][1] == t1_i - t2_i and t1_i != t2_i:
                        p_3 = p_3 + odd[1]
                    elif (odd[0][0] < odd[0][1] and t1_i < t2_i) or (odd[0][0] == odd[0][1] and t1_i == t2_i) or (odd[0][0] > odd[0][1] and t1_i > t2_i):
                        p_2 = p_2 + odd[1]
                rating = 2*p_2 + 3*p_3 + 4*p_4
                ratings.append(((t1_i, t2_i), rating))
        return sorted(ratings, key=lambda tup: tup[1])[::-1]
