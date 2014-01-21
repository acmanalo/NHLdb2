from bs4 import BeautifulSoup
from fractions import Fraction
from time import strptime

import sqlite3
import requests
import re

START_ID = 2013020001
SCHED_BASE_URL = 'http://www.nhl.com/ice/schedulebyseason.htm?season='
BOX_BASE_URL = 'http://www.nhl.com/gamecenter/en/boxscore?id='
RECAP_BASE_URL = 'http://www.nhl.com/gamecenter/en/recap?id='

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

def get_newest_id(season): #season in [beginning year][ending year] format
    '''
    Returns the gameid of the most recently  completed game
    '''
    completed_games = get_valid_table(season).find_all(class_='skedLinks')
    
    most_recent = completed_games[-1]
    most_recent_id = most_recent.find('a').get('href')[-10:] #id is final 10 characters

    return most_recent_id

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

    row = table.find(href=game_url)


    row_parent = row.find_parent('tr')

    date = row_parent.find(class_='skedStartDateSite').get_text()
    
    return date

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
        date_range.append(parse_date(str(date)))

    return date_range

def create_date_table():
    conn = sqlite3.connect('nhl.db')
    conn.execute('''CREATE TABLE Dates
                 (GameId int primary key, Year int not null, Month int not null,
                 Day int not null);''')

    conn.commit()
    conn.close()

def decompose_date(date):
    '''
    date is 8-digit date in form of yyyymmdd

    returns tuple [yyyy, mm, dd]
    '''

    return [str(date)[:4], str(date)[4:6], str(date)[6:8]]
    
                 
def store_dates(beginning_id, end_id = 0):
    try:             
        create_date_table()
    except:
        print 'Table already exists.'
        
    beg = int(beginning_id)
    if end_id == 0: end = beg
    else: end = int(end_id)
    
    ids = range(beg, end + 1)
    dates = get_date_range(beg, end)

    zipped = []

    for i in range(0, len(dates)):
        decomposed_date = decompose_date(dates[i])
        zipped.append((ids[i], int(decomposed_date[0]),
                       int(decomposed_date[1]), int(decomposed_date[2])))
    
    conn = sqlite3.connect('nhl.db')
    
    conn.executemany('INSERT INTO Dates VALUES (?, ?, ?, ?)', zipped)

    conn.commit()
    conn.close()

def print_dates():
    conn = sqlite3.connect('nhl.db')

    cursor = conn.execute('SELECT * from Dates')
    
    for row in cursor:
        print row

    conn.close()

def main():
    print_dates()
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
