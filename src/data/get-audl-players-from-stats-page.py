import pandas as pd
import glob
import requests
from bs4 import BeautifulSoup

somelist = []
page_start=0
page_max=116
print(f'Getting {page_max} pages of players')
for page_num in range(page_start,page_max+1):
    
    if page_num % 10 == 0:
        print(f'{page_num} of {page_max}')
    result = requests.get(f"https://theaudl.com/league/players?page={page_num:d}")
    soup = BeautifulSoup(result.text,'lxml')
    
    player_tables = soup.find_all('tbody')[0].find_all('tr')
    
    
    for plr_i, player_table in enumerate(player_tables):
        player_url = player_table.find_all('a',href=True)[0]['href']
        player_name = player_table.find_all('a',href=True)[0].text
        result_player = requests.get(f"https://theaudl.com/{player_url:}")
        soup_player = BeautifulSoup(result_player.text,'lxml')
        playerstat_table = soup_player.find_all('tbody')[0]
        for year_table,team_table in zip(playerstat_table.find_all('td',{'class':'views-field views-field-year active'}),
                                     playerstat_table.find_all('td',{'class':'views-field views-field-aw-team-id'})):
            year = year_table.text.rstrip().lstrip()
            team_abbrev = team_table.text.rstrip().lstrip()
            somelist.append([player_name, year, team_abbrev])
        


team_abbrev_dict = {'CIN': 'Cincinnati Revolution',
                    'NY': 'New York Empire',
                    'PIT': 'Pittsburgh Thunderbirds',
                    'DET': 'Detroit Mechanix',
                    'DC': 'DC Breeze',
                    'SF': 'San Francisco FlameThrowers',
                    'PHI': 'Philadelphia Phoenix', 
                    'IND': 'Indianapolis AlleyCats',
                    'SJ':'San Jose Spiders', 
                    'LA':'Los Angeles Aviators',
                    'DAL':'Dallas Roughnecks', 
                    'MAD':'Madison Radicals', 
                    'CHA':'Charlotte Express', 
                    # 'SEA':'Seattle Cascades',
                    # 'SEA':'Seattle Raptors', 
                    'ATL':'Atlanta Hustle', 
                    'TB':'Tampa Bay Cannons', 
                    'RIR':'Rhone Island Rampage', 
                    'OTT':'Ottawa Outlaws', 
                    'NSH':'Nashville NightWatch',
                    'CHI':'Chicago Wildfire', 
                    'TOR':'Toronto Rush', 
                    'SD': 'San Diego Growlers', 
                    'NJ': 'New Jersey Hammerheads', 
                    'ROC':'Rochester Dragons', 
                    'MIN':'Minnesota Wind Chill', 
                    'AUS':'Austin Sol', 
                    'VAN':'Vancouver Riptide', 
                    'PHS':'Philadelphia Spinners', 
                    'RAL':'Raleigh Flyers',
                    'MTL':'Montreal Royal', 
                    'COL':'Columbus Cranes', 
                    'CON':'Connecticut Consitution'}


audlstats_players = pd.DataFrame(somelist,columns=['PlayerName','Tournament','TeamAbbrev'])

team_abbrev_dict = { (tourney,abbrev): fullname for abbrev,fullname in team_abbrev_dict.items() for tourney in audlstats_players.Tournament.unique()}
for tourney in ['2015','2016','2017']:
    team_abbrev_dict[ (tourney,'TB') ] = 'Jacksonville Cannons'
for tourney in ['2018']:
    team_abbrev_dict[ (tourney,'TB') ] = 'Tampa Bay Cannons'
for tourney in ['2012','2013','2014']:
    team_abbrev_dict[ (tourney,'SEA') ] = 'Seattle Raptors'
for tourney in ['2015','2016','2017','2018']:
    team_abbrev_dict[ (tourney,'SEA') ] = 'Seattle Cascades'
    
audlstats_players['Teamname'] = audlstats_players.apply(lambda x:team_abbrev_dict[(x.Tournament,x.TeamAbbrev)], 
                                                        axis=1)

out_file = '../../data/supplemental/audl/audl_players_from_stats_page.csv'
print('Writing to file:', outfile)
audlstats_players.to_csv(out_file)