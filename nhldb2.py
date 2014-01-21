from bs4 import BeautifulSoup
from fractions import Fraction
from time import strptime

import requests
import re

SCHED_URL = 'http://www.nhl.com/ice/schedulebyseason.htm?season=20132014'
GAME_BASE_URL = 'http://www.nhl.com/gamecenter/en/boxscore?id='

def soupify(url_to_soup):
    url = requests.get(url_to_soup)
    soup = BeautifulSoup(url.content)

    return soup

def get_stats(game_id):
    '''
    Takes game id and parses corresponding box score html

    
    Returns array in order specified by output_order
    '''

    def parse_fraction(fraction):
        return str(fraction).split('/')
    
    try:
        soup = soupify(GAME_BASE_URL + str(game_id))

        stats_to_find = ['score',
                         'at',
                         'aPP',
                         'aHits',
                         'aFOW',
                         'aGive',
                         'aTake',
                         'aBlock',
                         'aPIM',
                         'aShots',
                         'ht',
                         'hPP',
                         'hHits',
                         'hFOW',
                         'hGive',
                         'hTake',
                         'hBlock',
                         'hShots',
                         'hPIM']
        
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
            
        output_order = ['t',
                        'Shots1',
                        'Shots2',
                        'Shots3',
                        'PPg',
                        'PPo',
                        'Hits',
                        'FOW',
                        'Give',
                        'Take',
                        'Block',
                        'PIM']
        
        stats_out = []
        for site in ['a', 'h']:         #append away stats then home
            for i in output_order:      #append stats in order of output_order
                stats_out.append(stats[site + i])

        stats_out.insert(len(stats_out)/2 + 1, stats['score_hm'])
        stats_out.insert(1, stats['score_aw'])
        
            
        return stats_out
    except:
        return "Failed. :("

def get_newest():
    '''
    Returns the gameid of the most recently  completed game
    '''
    
    soup = soupify(SCHED_URL)

    tables = soup.find_all('tbody')

    try:
        '''
        Second table in tables exists only in most recent season.

        Use the first table (all games completed) for previous seasons.
        '''
        S = tables[1].find_all(class_='skedLinks')
    except:
        S = tables[0].find_all(class_='skedLinks')
        
    for s in S:
        game_link = s.find('a').get('href')
        newest = str(game_link)[-10:]       #game id is the final 10 characters

    return newest


def parse_date(date_string):
    '''
    Parse the date from NHL.com's format of dates

    Return int in the form of [year][month][day]
    '''
    
    date = strptime(date_string, "%a %b %d, %Y")
    return int(`date.tm_year` + str(date.tm_mon).zfill(2) + `date.tm_mday`)



def main():
    print get_newest()

    start = 2013020001
    for i in range(start, start + 10):
        print get_stats(i)
        
if __name__ == "__main__":
    main()
