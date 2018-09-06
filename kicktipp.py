#!/usr/bin/env python3

import urllib.request
import threading
import numpy
from bs4 import BeautifulSoup

class AsyncSoupLoader(threading.Thread):    
    def run(self):
        soup = load_soup(self.__url)
        table = soup.find(class_="marketboard-event-with-header__markets-list")

        # Match name
        match_name = soup.find(class_="event-block__event-name").get_text().strip()

        # Extract data
        scores = []
        probs = []
        for button in table.select("tr.marketboard-options-row > td.mb-option-button > button.mb-option-button__button"):
            score = button.find(class_="mb-option-button__option-name").get_text().strip()
            payout = button.find(class_="mb-option-button__option-odds").get_text().strip()
            scores.append(score)
            probs.append(1/float(payout))

        # Normalize data
        s = sum(probs)
        for i in range(0, len(probs)):
            probs[i] = probs[i]/s

        # Structure data
        data = numpy.zeros((5, 5))
        for i in range(0, len(scores)):
            if len(scores[i]) == 3 and scores[i][1] == ":":
                l_score = int(scores[i][0])
                r_score = int(scores[i][2])
                if l_score < 5 and r_score < 5:
                    data.itemset((l_score, r_score), probs[i])

        self.__data = {
            "match_name" : match_name,
            "match_data" : data,
            "best_tips" : get_best_tips(data)
        }
    
    def set(self, url):
        self.__url = url

    def get(self):
        return self.__data

def load_soup(url):
    return BeautifulSoup(urllib.request.urlopen(url).read().decode(), "html.parser")

def get_matches(soup):
    matches = []
    for match in soup.select("a.mb-event-details-buttons__button-link"):
        href = match["href"]
        if(href[0] == "/"):
            href = href.replace("/wetten/", "/35/wetten/")
            href = href.replace("/de/sports/events/4/43/", "https://sports.bwin.com/de/sports/events/4/43/")
            matches.append(href)
    return matches

def get_match_data(url_list):
    threads = []
    match_data = []
    for url in url_list:
        th = AsyncSoupLoader()
        th.set(url)
        threads.append(th)
        th.start()
    
    for th in threads:
        th.join()
        match_data.append(th.get())
    
    return match_data

def get_reward_matrix(lhs, rhs):
    rewards = numpy.zeros((5, 5))
    for i in range(0, 5):
        for j in range(0, 5):
            rew = 0
            if lhs == i and rhs == j:
                rew = 4
            elif (lhs != rhs) and (lhs - rhs == i - j):
                rew = 3
            elif (lhs - rhs) * (i - j) > 0 or (lhs == rhs and i == j):
                rew = 2
            rewards.itemset((i, j), rew)
    return rewards

def get_expected_rewards(match_data):
    expected_rewards = numpy.zeros((5, 5))
    for left_score in range(0, 5):
        for right_score in range(0, 5):
            rewards = get_reward_matrix(left_score, right_score)
            expected_rewards = expected_rewards + match_data.item((left_score, right_score)) * rewards
    return expected_rewards

def get_best_tips(match_data):
    exp_rewards = get_expected_rewards(match_data)
    arr = numpy.ravel(exp_rewards)
    best_tips = numpy.argsort(arr).tolist()[::-1]
    for i in range(0, len(best_tips)):
        best_tips[i] = numpy.unravel_index(best_tips[i], exp_rewards.shape)
    return (best_tips, exp_rewards.item(best_tips[0]))

print("kick-predict 18.09")

print("[1] Getting list of upcoming matches.")

main_page = load_soup("https://sports.bwin.com/de/sports/4/43/wetten/bundesliga")
match_urls = get_matches(main_page)

print("[2] Scraping data...")
match_data = get_match_data(match_urls)
print()

print("{}\033[1mBest tip\t2nd tip\tExp. reward\033[0m".format(" "*50))
print()

total_reward = 0
for match in match_data:
    exp_reward = match["best_tips"][1]
    total_reward = total_reward + exp_reward
    print("{}{}{}\t{}\t{:1.3f}".format(match["match_name"], " "*(max(0, 50-len(match["match_name"]))), match["best_tips"][0][0], match["best_tips"][0][1], exp_reward))
print("{}\t\t\033[1mTotal: {:2.3f}\033[0m".format(" "*50, total_reward))