import pandas as pd
import requests
from bs4 import BeautifulSoup
import importlib.resources as import_resources

# CONSTANTS (No Need to Change)
def get_max_pages_by_year():
    return {2018:9,2017:9,2016:10,2015:10,2014:7,2013:6,2012:4}
def get_latest_year():
    return 2019
def get_default_audl_games_file():
    with import_resources.path('ultianalyticspull.data.audl.supplemental', 'audl_games.csv') as audl_games:
        return audl_games

def get_game_page_urls(year):
    """Get URLs for all games of given year"""
    if year == get_latest_year():
        return [f'https://theaudl.com/league/schedule/week-{week_no}' for week_no in range(1,16)]

    max_pages = get_max_pages_by_year().get(year)
    year_id = get_latest_year() - year
    return [f'https://theaudl.com/league/game?page={page_num}&year={year_id}'
                                                                    for page_num in range(0,max_pages)]

def get_soup(url):
    """Return BS Soup Object"""
    result = requests.get(url)
    return BeautifulSoup(result.text,'lxml')

def format_games_dict(year, matchup_links, start_times_places, score_pairs, team_name_pairs):
    """Format Game Info into Dictionary for Pandas DataFrame"""
    return [{'Year':year,
             'Matchup Link':mul,'Date Location':stp,
             'Home Team':hm,'Away Team':aw,
             'Home Team Score':hms,'Away Team Score':aws
            } for mul,stp,(aws,hms),(aw,hm) in zip(matchup_links,
                                                    start_times_places,
                                                    score_pairs,
                                                    team_name_pairs)]

def get_audl_game_results(output_csv=get_default_audl_games_file(),
                          years=[2012,2013,2014,2015,2016,2017,2018,2019]):

    # Initialize List of Scraped Info
    game_info_dicts = []

    # Iterate Over Years To Scrape
    for year_id, year in enumerate(years):
        print(f'Getting {year}...')

    # Scrape Years of Games
        for url in get_game_page_urls(year):
            soup = get_soup(url)

            if year == get_latest_year():
                matchup_links = [i.find_all('a')[0].attrs['href'] for i in soup.find_all('span',attrs={'class':'audl-schedule-gc-link'})]
                start_times_places = [i.text for i in soup.find_all('span',attrs={'class':'audl-schedule-start-time-text'})]
            else:
                matchup_links = [i.find_all('a')[0].attrs['href'] for i in soup.find_all('td',attrs={'class':"audl-schedule-game-center",'colspan':"3"})]
                start_times_places = [i.text for i in soup.find_all('td',attrs={'class':"audl-schedule-start-time",'colspan':"2"})]

            scores = [i.text for i in soup.find_all('td',attrs={'class':"audl-schedule-team-score"})]
            team_names = [i.text for i in soup.find_all('td',attrs={'class':"audl-schedule-team-name"})]
            score_pairs = [(i,j) for i,j in zip(scores[::2],scores[1::2])]
            team_name_pairs = [(i,j) for i,j in zip(team_names[::2],team_names[1::2])]

            game_info_dicts +=format_games_dict(year, matchup_links, start_times_places,
                                              score_pairs, team_name_pairs)

    games = pd.DataFrame(game_info_dicts)

    # Enhance
    games['Date'] = games['Matchup Link'].apply(lambda x : '/'.join(x.split('/')[3].split('-')[:3]) )
    games['Date'] = pd.to_datetime(games['Date'],format='%Y/%m/%d')
    games['Time'] = games['Date Location'].apply(lambda x : ' '.join(x.split(' ')[2:5]) )
    games['City'] = games['Date Location'].apply(lambda x : ' '.join(x.split(' ')[5:]) )
    games['Week'] = games['Date'].dt.strftime('%W').astype(int)
    games['Week'] = games.apply(lambda x : x.Week - games[games.Year==x.Year].Week.min() + 1,axis=1)
    games['UniversalGameID'] = games.index

    games.sort_values('Date').reset_index(drop=True).to_csv(output_csv)
    print(f"Wrote {output_csv}")
