import pandas as pd
import glob
import requests
from bs4 import BeautifulSoup
import os
import difflib

webscraped_players = pd.read_csv('/Users/fiorino/Desktop/audl-pull/player-names/01_webscraped_audlplayers2019.csv')
team_info = pd.read_csv('/Users/fiorino/Desktop/audl-pull/data/teams/audlteaminfo.csv')


somelist=[]
for i in webscraped_players['team-href'].values:
    result = requests.get("{}/players".format(i))
    soup = BeautifulSoup(result.text,'lxml')
    for j in (soup.find_all('div', {'class':"views-field views-field-player-field-player-display-name"})):
        team_lower = os.path.basename(i)
        teamname = difflib.get_close_matches(team_lower.title(),team_info[team_info.Active].Teamname.unique(),cutoff=.01)[0]
        player_name = j.text.strip(' ').replace('  ',' ').replace('- ','-')
        somelist.append([teamname,player_name])
        
audldotcom_rosters = pd.DataFrame(somelist,columns=['Teamname','Name'])

audldotcom_rosters.to_csv('../../data/players/current_rosters.csv')
