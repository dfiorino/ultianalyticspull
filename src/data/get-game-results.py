import pandas as pd
import requests
from bs4 import BeautifulSoup
import argparse

# CONSTANTS (No Need to Change)
MAX_PAGES_BY_YEAR = {2018:9,2017:9,2016:10,2015:10,2014:7,2013:6,2012:4}
CURRENT_YEAR = 2019

def parse_args():
    """Setup command-line interface"""
    parser = argparse.ArgumentParser(description='Get all AUDL games.')
    
    parser.add_argument('-y','--years',nargs='+', dest='years', type=int,
                        default=[2012,2013,2014,2015,2016,2017,2018,2019],
                        help='Years [list]')
    

    parser.add_argument('-o','--output', dest='output_csv', 
                        default='../../data/supplemental/games.csv',
                        help='Path and name of output CSV')
    return  parser.parse_args()

def get_game_page_urls(year):
    """Get URLs for all games of given year"""
    if year == CURRENT_YEAR:
        return [f'https://theaudl.com/league/schedule/week-{week_no}' for week_no in range(1,16)]
    
    max_pages = MAX_PAGES_BY_YEAR.get(year)
    year_id = CURRENT_YEAR - year
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
    
def main():
    # Parse Argumnets
    args = parse_args()
    output_csv = args.output_csv
    years = args.years
    
    # Initialize List of Scraped Info
    game_info_dicts = []
    
    # Iterate Over Years To Scrape
    for year_id, year in enumerate(years):
                    
    # Scrape Years of Games
        for url in get_game_page_urls(year):
            soup = get_soup(url) 
                
            if year == CURRENT_YEAR:
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
    
main()