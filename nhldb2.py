from bs4 import BeautifulSoup
import urllib
import re

GAME_BASE_URL = "http://www.nhl.com/gamecenter/en/boxscore?id="

def get_game_stats(game_id):
    stat_out = []
    temp = []
    f = urllib.urlopen(GAME_BASE_URL + str(game_id))
    soup = BeautifulSoup(f)

    
    game = soup.find_all(True, {'class' : ['score', 'at', 'aPP', 'aHits', 'aFOW', 'aGive',
                                           'aTake', 'aBlock', 'aPIM', 'ht', 'hPP',
                                           'hHits', 'hFOW', 'hGive', 'hTake',
                                           'hBlock', 'hPIM']})
    
    stat_out.append(str(game[2].contents[0]))
    stat_out.append(str(game[0].contents[0]))
    
    for i in range(6, 17, 2):
        stat_out.append(str(game[i].contents[0]))

    stat_out.append(str(game[3].contents[0]))
    stat_out.append(str(game[1].contents[0]))
    
    for i in range(7, 18, 2):
        stat_out.append(str(game[i].contents[0]))
    
    return stat_out

for i in range(2013020001,2013020050):
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
