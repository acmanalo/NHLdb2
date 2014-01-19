from bs4 import BeautifulSoup
import urllib

GAME_BASE_URL = "http://www.nhl.com/gamecenter/en/boxscore?id="

def get(soup, class_name):
    return str(soup.find(class_=class_name).contents[0])

def get_team_stats(soup, home_or_away):
    team = get(soup, home_or_away + 't')
    powerplay = get(soup, home_or_away + 'PP')
    hits = get(soup, home_or_away  + 'Hits')
    faceoffs = get(soup, home_or_away + 'FOW')
    giveaways = get(soup, home_or_away + 'Give')
    takeaways = get(soup, home_or_away + 'Take')
    blocks = get(soup, home_or_away + 'Block')
    penmins = get(soup, home_or_away + 'PIM')

    return [team, powerplay, hits, faceoffs, giveaways,
            takeaways, blocks, penmins]

class game:
    def __init__(self, game_id):
        f = urllib.urlopen(GAME_BASE_URL + str(game_id))
        self.soup = BeautifulSoup(f)

    def get_game_stats(self):
        return [get_team_stats(self.soup, 'a'),
                get_team_stats(self.soup, 'h')]


first = game('2013020001')
print first.get_game_stats()
