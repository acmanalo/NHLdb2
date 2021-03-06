from bs4 import BeautifulSoup
from fractions import Fraction
from time import strptime

import sqlite3
import requests
import re

START_ID = 2013020001
DATABASE = 'nhl2013.db'
SCHED_BASE_URL = 'http://www.nhl.com/ice/schedulebyseason.htm?season='
BOX_BASE_URL = 'http://www.nhl.com/gamecenter/en/boxscore?id='
RECAP_BASE_URL = 'http://www.nhl.com/gamecenter/en/recap?id='

def soupify(url_to_soup):
    url = requests.get(url_to_soup)
    soup = BeautifulSoup(url.content)

    return soup

def id_to_stats(game_id):
    '''
    Takes game id and parses corresponding box score html

    
    Returns array in order specified by output_order
    '''

    def parse_fraction(fraction):
        return str(fraction).split('/')
    
    try:
        soup = soupify(BOX_BASE_URL + str(game_id))

        stats_to_find = ['score',
                         'at',
                         'aPP',
                         'aHits',
                         'aFOW',
                         'aGive',
                         'aTake',
                         'aBlock',
                         'aPIM',
                         'ht',
                         'hPP',
                         'hHits',
                         'hFOW',
                         'hGive',
                         'hTake',
                         'hBlock',
                         'hPIM']
        
        game = soup.find_all(True, {'class' : stats_to_find })
        stats = {}
        
        for stat in game:
            if len(stat['class'])<2:
                key = stat['class'][0]
            else:
                key = '_'.join(stat['class'])

            stats[str(key)] = str(stat.get_text())

        [aPPg, oPPo] = parse_fraction(stats['aPP'])
        [hPPg, hPPo] = parse_fraction(stats['hPP'])

        stats['aPPg'] = aPPg
        stats['aPPo'] = oPPo
        stats['hPPg'] = hPPg
        stats['hPPo'] = hPPo

        del stats['aPP']
        del stats['hPP']

        period_shots = soup.find_all(True, {'class' : ['aShots', 'hShots']})

        for period_shot in period_shots:
            shots = period_shot.get_text()
            period = period_shot.find_parent('tr').find('td').get_text()

            if period == '1st': period_append = '1'
            elif period == '2nd' : period_append = '2'
            elif period == '3rd' : period_append = '3'
            elif period == 'OT' : period_append = '4'

            key = period_shot['class'][0] + 'P' + period_append

            stats[key] = shots

            
        # Convert values in dictionary to int if possible
        for val in stats:
            try:
                stats[val] = int(stats[val])
            except:
                stats[val] = str(stats[val])
        
        return stats
    except Exception:
        pass
    
def get_valid_table(season): #season in [beginning year][ending year] format
    soup = soupify(SCHED_BASE_URL + str(season))

    tables = soup.find_all('tbody')

    try:
        '''
        Second table in tables exists only in most recent season.

        Use the first table (all games completed) for previous seasons.
        '''
        valid_table = tables[1]
    except:
        valid_table = tables[0]

    return valid_table

def get_last_id(season): #season in [beginning year][ending year] format
    '''
    Returns the gameid of the most recently  completed game
    '''
    completed_games = get_valid_table(season).find_all(class_='skedLinks')
    
    last = completed_games[-1]
    last_id = last.find('a').get('href')[-10:] #id is final 10 characters

    return last_id

def parse_date(nhl_date_string):
    '''
    Parse the date from NHL.com's format of dates

    Return str in the form of yyyymmdd
    '''
    date = strptime(nhl_date_string, "%a %b %d, %Y")
    return `date.tm_year` + str(date.tm_mon).zfill(2) + str(date.tm_mday).zfill(2)

def id_to_date(game_id, table):
    '''
    Takes 10 digit game id and table in which to search.
    
    Returns date in NHL date format
    '''
    game_id_str = str(game_id)
    game_url = RECAP_BASE_URL + game_id_str
    try:
        row = table.find(href=game_url)

        row_parent = row.find_parent('tr')

        date = row_parent.find(class_='skedStartDateSite').get_text()

        return date
    except Exception:
        pass
    
def get_stats_range(beginning_id, end_id):
    beg = int(beginning_id)
    end = int(end_id)
    
    id_range = range(beg, end + 1)

    stats_range_out = []
    
    stat_order = ['t', 'ShotsP1', 'ShotsP2', 'ShotsP3', 'PPg', 'PPo', 'Hits',
                      'FOW', 'Give', 'Take', 'Block', 'PIM']
    
    for i in id_range:
        s = id_to_stats(i)
        try:
            ordered = []
            for site in ['a', 'h']:
                for cat in stat_order:
                    key = str(site + cat)
                    ordered.append(s.get(key))
            print i
            ordered.insert(len(ordered)/2 + 1, s['score_hm'])
            ordered.insert(1, s['score_aw'])

            ordered.append(s.get('aShotsP4', None))
            ordered.append(s.get('hShotsP4', None))

            ordered.insert(0, i)
            
            stats_range_out.append(ordered)
        except Exception:
            print 'Failed on', i
            pass
    return stats_range_out

def get_date_range(beginning_id, end_id):
    '''
    Takes beginning game id and option end game id
    
    '''
    beg = int(beginning_id)
    end = int(end_id)

    id_range = range(beg, end + 1)

    beg_year = str(beginning_id)[:4]
    end_year = str(int(beg_year) + 1)
    season = beg_year + end_year

    table = get_valid_table(season)
    
    date_range = []
    for i in id_range:
        date = id_to_date(i, table)
        try:
            date_range.append(parse_date(str(date)))
        except Exception:
            pass

    return date_range

def create_date_table():
    conn = sqlite3.connect(DATABASE)
    
    try:
        conn.execute('''CREATE TABLE Dates
                     (GameId    int     primary key,
                     Year       int     not null,
                     Month      int     not null,
                     Day        int     not null);''')

        conn.commit()
    except:
        pass
    
    conn.close()

def decompose_date(date):
    '''
    date is 8-digit date in form of yyyymmdd

    returns tuple [yyyy, mm, dd]
    '''
    return [str(date)[:4], str(date)[4:6], str(date)[6:8]]
    
def store_dates(beginning_id, end_id = 0):
    beg = int(beginning_id)
    if end_id == 0: end = beg
    else: end = int(end_id)
    
    ids = range(beg, end + 1)
    dates = get_date_range(beg, end)

    zipped = []

    for i in range(0, len(dates)):
        skipped = 0
        try:
            decomposed_date = decompose_date(dates[i])
            zipped.append((ids[i+skipped], int(decomposed_date[0]),
                           int(decomposed_date[1]), int(decomposed_date[2])))
        except Exception:
             skipped+=1
    
    conn = sqlite3.connect(DATABASE)
    
    conn.executemany('INSERT INTO Dates VALUES (?, ?, ?, ?)', zipped)

    conn.commit()
    conn.close()

def store_stats(beginning_id, end_id = 0):
    beg = int(beginning_id)
    if end_id==0 : end = beg
    else: end = int(end_id)
    
    ids = range(beg, end + 1)
    stats = get_stats_range(beg, end)
    
    zipped = []

    for i in range(0, len(stats)):
        zipped.append(stats[i])
        
        print 'GameID', ids[i], 'parsed.'

    conn = sqlite3.connect(DATABASE)
    conn.executemany('''INSERT INTO Games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?,
                     ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', zipped)

    conn.commit()
    conn.close()
        
def print_dates():
    conn = sqlite3.connect(DATABASE)

    cursor = conn.execute('SELECT * FROM Dates')
    
    for row in cursor:
        print row

    conn.close()

def print_stats():
    conn = sqlite3.connect(DATABASE)

    cursor = conn.execute('SELECT * FROM Games')
    
    for row in cursor:
        print row

    conn.close()

def create_stats_table():
    conn = sqlite3.connect(DATABASE)
    try:
        conn.execute('''CREATE TABLE Games
                     (GameId    int         primary key,
                     Away       text        not null,
                     AScore     int         not null,
                     AShots1P   int         not null,
                     AShots2p   int         not null,
                     AShots3p   int         not null,
                     APPGoals   int         not null,
                     APPOpps    int         not null,
                     AHits      int         not null,
                     AFaceOffWins int       not null,
                     AGiveaways int         not null,
                     ATakeAways int         not null,
                     ABlockedShots int      not null,
                     APenaltyMins int       not null,
                     Home       text        not null,
                     HScore     int         not null,
                     HShots1P   int         not null,
                     HShots2p   int         not null,
                     HShots3p   int         not null,
                     HPPGoals   int         not null,
                     HPPOpps    int         not null,
                     HHits      int         not null,
                     HFaceOffWins int       not null,
                     HGiveaways int         not null,
                     HTakeAways int         not null,
                     HBlockedShots int      not null,
                     HPenaltyMins int       not null,
                     AShotsP4  int,
                     HShotsP4  int);''')
        

        conn.commit()
    except:
        pass
    
    conn.close()

def print_joined():
    conn = sqlite3.connect(DATABASE)

    cursor = conn.execute('''SELECT * FROM Dates NATURAL JOIN Games WHERE Away = 'SJS' OR Home = 'SJS';''')
    
    for row in cursor:
        print row

    conn.close()

def create_updated_db(current_season):
    '''
    In:
        current_season: [beginning_year][ending_year] in yyyyyyyy format
    '''

    create_date_table()
    create_stats_table()

##    store_stats(2013020645, get_last_id(current_season))
##    store_dates(2013020645, get_last_id(current_season))
##
    store_stats(START_ID, get_last_id(current_season))
    store_dates(START_ID, get_last_id(current_season))

def main():
    create_updated_db(20132014)

    print_joined()
    
    
##    conn = sqlite3.connect('nhl_games.db')
####    conn.execute('''CREATE TABLE Games
####                    (GameID int primary key, A text not null, AwayScore int not null,
####                    H text not null, HScore int not null);''')
####
####    for i in range(START_ID, START_ID + 100):
####        print i
####        game = get_stats(i)
####        conn.execute('''INSERT INTO Games  VALUES (?, ?, ?, ?, ?)''', (i, game[0], game[1], game[13], game[14]))
####
####        conn.commit()
##
##    cursor = conn.execute('SELECT GameID, Away, AwayGoals, Home, HomeGoals from Games')
##
##    for row in cursor:
##        print row[0], '-', row[1], '-', row[2], ' @ ', row[3], '-', row[4]
##
##    conn.close()
    
if __name__ == "__main__":
    main()
