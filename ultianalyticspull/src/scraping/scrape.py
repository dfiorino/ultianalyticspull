import requests
import pandas as pd
from bs4 import BeautifulSoup
import ultianalyticspull.src.getters.datagetters as getters

def get_soup(url):
    """Return BS Soup Object"""
    result = requests.get(url)
    return BeautifulSoup(result.text,'lxml')

def get_audl_weekly_active_rosters():

    # Create DataFrame
    somelist=[]
    for week_no in range(1,16):
        print(f'Getting Week {week_no}')

        soup = get_soup(f'https://theaudl.com/league/news/2019-audl-active-rosters-week-{week_no}')

        teams = [team.text for team in soup.find_all('h2')[:-1]]
        active_players = [players.text for players in soup.find_all('p') if len(players.text) > 250] # Hacky
        somelist+=[{'Year':2019,
                    'Week':week_no,
                    'Team':t,
                    'Actives':aps.replace('\n','; ')} for t,aps in zip(teams, active_players)]
    return pd.DataFrame(somelist)




def get_audl_rosters_from_stats_page(page_start = 0,
                                     page_max = 116):
    # Get Data/Paths
    team_info = getters.get_audl_teams_dataframe()

    # Create DataFrame
    somelist = []
    print(f'Getting {page_max-page_start} pages of players')
    for page_num in range(page_start,page_max+1):

        if page_num % 10 == 0:
            print(f'{page_num} of {page_max}')

        soup = get_soup(f"https://theaudl.com/league/players?page={page_num:d}")
        player_tables = soup.find_all('tbody')[0].find_all('tr')

        for plr_i, player_table in enumerate(player_tables):
            player_url = player_table.find_all('a',href=True)[0]['href']
            player_name = player_table.find_all('a',href=True)[0].text
            soup_player = get_soup(f"https://theaudl.com/{player_url}")

            playerstat_table = soup_player.find_all('tbody')[0]
            for year_table,team_table in zip(playerstat_table.find_all('td',{'class':'views-field views-field-php'}),
                                         playerstat_table.find_all('td',{'class':'views-field views-field-aw-team-id'})):
                year = year_table.text.rstrip().lstrip()
                if year=='Career':
                    continue
                team_abbrev = team_table.text.rstrip().lstrip()
                somelist.append([player_name, year, team_abbrev])
    audlstats_players = pd.DataFrame(somelist,columns=['PlayerName','Year','TeamAbbrev'])
    # Fix abbreviation change from teams moving
    jax_cannons = (audlstats_players['Year'].isin(['2015','2016','2017'])) &(audlstats_players['TeamAbbrev']=='TB')
    audlstats_players.loc[jax_cannons,'TeamAbbrev'] = 'JAX'
    lex_bgrass = (audlstats_players['Year'].isin(['2012'])) &(audlstats_players['TeamAbbrev']=='CIN')
    audlstats_players.loc[lex_bgrass,'TeamAbbrev'] = 'LEX'

    team_info['Year'] = team_info.apply(lambda x : range(x['Inaugurated'], x['Last Active']+1),axis=1)
    team_abbrev_dict = team_info.explode('Year').astype(str).groupby(['Year','Team Abv']).apply(lambda x : x['Teamname'].values[0]).to_dict()

    audlstats_players['Teamname'] = audlstats_players.apply(lambda x:team_abbrev_dict[(x['Year'],x['TeamAbbrev'])],
                                                            axis=1)

    return audlstats_players


def get_game_page_urls(year):
    """Get URLs for all games of given year"""
    latest_year = 2019
    if year == latest_year:
        return [f'https://theaudl.com/league/schedule/week-{week_no}' for week_no in range(1,16)]

    max_pages_by_year = {2018:9,2017:9,2016:10,2015:10,2014:7,2013:6,2012:4}
    max_pages = max_pages_by_year.get(year)
    year_id = latest_year - year
    return [f'https://theaudl.com/league/game?page={page_num}&year={year_id}'
                                                                    for page_num in range(0,max_pages)]



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


def pm_am(string):
    val = 0
    if string.lower()=='am':
        val = 0
    if string.lower()=='pm':
        val = 12
    return(val)

def time_to_float(string):
    try:
        hour = float(string.split(':')[0])
        minutes = float(string.split(':')[1])/60
    except:
        hour=19
        minutes=0
        print(string,'set to 7p')
    return hour+minutes

def get_audl_game_results(years=[2012,2013,2014,2015,2016,2017,2018,2019],
                          latest_year=2019):

    # Initialize List of Scraped Info
    game_info_dicts = []

    # Create DataFrame
    # Iterate Over Years To Scrape
    for year_id, year in enumerate(years):
        print(f'Getting {year}...')
        # Scrape Years of Games
        for url in get_game_page_urls(year):
            soup = get_soup(url)

            if year == latest_year:
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
    games = pd.DataFrame(game_info_dicts).drop_duplicates()

    # Enhance
    games['Matchup Link'] = games['Matchup Link'].str.split('/').apply(lambda x : x[-1])
    games['Date'] = games['Matchup Link'].apply(lambda x : '/'.join(x.split('-')[:3]) )
    games['Date'] = pd.to_datetime(games['Date'],format='%Y/%m/%d')
    games['date_iso'] = pd.to_datetime(games['Date']).apply(lambda x : x.isoformat())
    games['Time'] = games['Date Location'].apply(lambda x : ' '.join(x.split(' ')[2:5]) )
    games['Hour'] = games['Time'].apply(lambda x : time_to_float(x.split(' ')[0]) + pm_am(x.split(' ')[1]))
    games['Location'] = games['Date Location'].apply(lambda x : ' '.join(x.split(' ')[5:]) )
    games['Week'] = games['Date'].dt.strftime('%W').astype(int)
    games['Week'] = games.apply(lambda x : x.Week - games[games.Year==x.Year].Week.min() + 1,axis=1)
    games['UniversalGameID'] = games.index

    # Correct
    nsh_wrong = 'Nashville Nightwatch'
    nsh_correct = 'Nashville NightWatch'
    games = games.replace(nsh_wrong, nsh_correct)
    games.loc[games['Location']=='Jacksonville', 'Home Team'] = 'Jacksonville Cannons'
    games = games.replace('LA','Los Angeles').replace('Salt Lake','Salt Lake City')

    return games

def get_audl_current_rosters():

    # Get Data/Paths
    team_info = getters.get_audl_teams_dataframe()

    # Create DataFrame
    somelist=[]
    for i,row in team_info[team_info['Active']].iterrows():
        print(row['Teamname'])
        nickname = row['Nickname'].lower().replace(' ','')

        soup = get_soup(f'https://www.theaudl.com/{nickname}/players')

        for j in (soup.find_all('div', {'class':"views-field views-field-player-field-player-display-name"})):
            player_name = j.text.strip(' ').replace('  ',' ').replace('- ','-')
            somelist.append([row['Teamname'],player_name])
    audldotcom_rosters = pd.DataFrame(somelist,columns=['Teamname','Name'])

    # Correct Names
    aliases = {'Matthew Rehder':'Matt Rehder',
                'Matthew McDonnell':'Rowan McDonnell',
                'Jonathan Helton':'Goose Helton',
                'Nathan Bridges':'Nate Bridges',
                'Dominic Leggio':'Dom Leggio',
                'JD Hastings':'J.D. Hastings',
                'James Kittlesen':'Jimmy Kittlesen',
                'Jonathan Mast':'Jon Mast',
                'André Arsenault':'Andre Arsenault',
                'Estéban Ceballos':'Esteban Ceballos',
                'Stève Bonneau':'Steve Bonneau'}
    for no,yes in aliases.items():
        audldotcom_rosters['Name'] = audldotcom_rosters['Name'].replace(no,yes)

    # Add Columns
    audldotcom_rosters['FirstName'] = audldotcom_rosters['Name'].apply(lambda x : x.split(' ')[0])
    audldotcom_rosters['LastName'] = audldotcom_rosters['Name'].apply(lambda x : ' '.join(x.split(' ')[1:]))

    return audldotcom_rosters
