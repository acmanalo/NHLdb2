from bs4 import BeautifulSoup
from fractions import Fraction
from time import strptime

import requests
import re

GAME_BASE_URL = "http://www.nhl.com/gamecenter/en/boxscore?id="

def get_stats(game_id):
    '''
    Takes game id and parses corresponding box score html

    
    Returns array in order specified by output_order
    '''

    def parse_fraction(fraction):
        return str(fraction).split('/')
    
    try:
        url = requests.get(GAME_BASE_URL + str(game_id))
        soup = BeautifulSoup(url.content)

        stats_to_find = ['score', 'at', 'aPP', 'aHits', 'aFOW', 'aGive',
                         'aTake', 'aBlock', 'aPIM', 'aShots',
                         'ht', 'hPP','hHits','hFOW', 'hGive', 'hTake', 'hBlock',
                         'hShots', 'hPIM']
        
        game = soup.find_all(True, {'class' : stats_to_find })
        stats = {}
        
        aPeriod = hPeriod = 1
        
        for stat in game:
            if len(stat['class'])<2:
                c = stat['class'][0]
            else:
                c = '_'.join(stat['class'])

            if stat['class'][0] == 'aShots':
                c = 'aShots' + `aPeriod`
                aPeriod+=1
            elif stat['class'][0] == 'hShots':
                c = 'hShots' + `hPeriod`
                hPeriod+=1

            stats[str(c)] = str(stat.get_text())

        [aPPg, oPPo] = parse_fraction(stats['aPP'])
        [hPPg, hPPo] = parse_fraction(stats['hPP'])

        stats['aPPg'] = aPPg
        stats['aPPo'] = oPPo
        stats['hPPg'] = hPPg
        stats['hPPo'] = hPPo

        del stats['aPP']
        del stats['hPP']

        # Convert values in dictionary to int if possible
        for val in stats:
            try:
                stats[val] = int(stats[val])
            except:
                continue
            
        output_order = ['t', 'Shots1', 'Shots2', 'Shots3', 'PPg', 'PPo', 'Hits',
                        'FOW', 'Give', 'Take', 'Block', 'PIM']
        
        stats_out = []
        for site in ['a', 'h']:         #append away stats then home
            for i in output_order:      #append stats in order of output_order
                stats_out.append(stats[site + i])

        stats_out.insert(len(stats_out)/2 + 1, stats['score_hm'])
        stats_out.insert(1, stats['score_aw'])
        
            
        return stats_out
    except:
        return "Failed. :("

def parse_date(date_string):
    '''
    Parse the date from NHL.com's format of dates

    Return int in the form of [year][month][day]
    '''
    date = strptime(date_string, "%a %b %d, %Y")
    return int(`date.tm_year` + str(date.tm_mon).zfill(2) + `date.tm_mday`)

start = 2013020001

for i in range(start, start + 100):
    print get_stats(i)


##def get_game(
##        


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
