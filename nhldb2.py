from bs4 import BeautifulSoup
from fractions import Fraction

import requests
import re

GAME_BASE_URL = "http://www.nhl.com/gamecenter/en/boxscore?id="

def get_game_stats(game_id):
    '''
    Takes game id and parses corresponding box score html

    
    returns [aTeam, aGoals, aPP goal, aPP opp, aHits, aFOW, aGiveaways,
             aTakeaways, aBlocks, aPIM, hTeam, hGoals, hPP goals, hPP opp,
             hHits, hFOW, hGiveaways, hTakeaways, hBlocks, hPIM]
    '''
    stat_out = []
    
    url = requests.get(GAME_BASE_URL + str(game_id))
    soup = BeautifulSoup(url.content)

    stats_to_find = ['score', 'at', 'aPP', 'aHits', 'aFOW', 'aGive',
                     'aTake', 'aBlock', 'aPIM', 'ht', 'hPP','hHits',
                     'hFOW', 'hGive', 'hTake', 'hBlock', 'hPIM']
    
    game = soup.find_all(True, {'class' : stats_to_find })
    
    stat_out.append(str(game[2].contents[0]))
    stat_out.append(int(game[0].contents[0]))

    [pp_goal, pp_opp] = str(game[6].contents[0]).split('/')
    stat_out.append(int(pp_goal))
    stat_out.append(int(pp_opp))
    
    for i in range(8, 17, 2):
        stat_out.append(int(game[i].contents[0]))

    stat_out.append(str(game[3].contents[0]))
    stat_out.append(int(game[1].contents[0]))

    [pp_goal, pp_opp] = str(game[7].contents[0]).split('/')
    stat_out.append(int(pp_goal))
    stat_out.append(int(pp_opp))
    
    for i in range(9, 18, 2):
        stat_out.append(int(game[i].contents[0]))
    
    return stat_out

for i in range(2013020001,2013020101):
    print get_game_stats(i)

##def get(soup, class_name):
##    return str(soup.find(class_=class_name).contents[0])
##
##def get_team_stats(soup, home_or_away):
##    site = 'hm' if home_or_away == 'h' else 'aw'
##    goals = get(soup, 'score ' + site)
##    
##    team =      get(soup, home_or_away + 't')
##    powerplay = get(soup, home_or_away + 'PP')
##    hits =      get(soup, home_or_away + 'Hits')
##    faceoffs =  get(soup, home_or_away + 'FOW')
##    giveaways = get(soup, home_or_away + 'Give')
##    takeaways = get(soup, home_or_away + 'Take')
##    blocks =    get(soup, home_or_away + 'Block')
##    penmins =   get(soup, home_or_away + 'PIM')
##
##    return [team, goals, powerplay, hits, faceoffs, giveaways,
##            takeaways, blocks, penmins]
##
##class game:
##    def __init__(self, game_id):
##        
##
##    def get_game_stats(self):
##        return [get_team_stats(self.soup, 'a'),
##                get_team_stats(self.soup, 'h')]
##
##for i in range(2013020001, 2013020005):
##    print game(i).get_game_stats()
