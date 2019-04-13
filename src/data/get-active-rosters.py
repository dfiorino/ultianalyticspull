import pandas as pd
import glob
import requests
from bs4 import BeautifulSoup
import os

somelist=[]
for week_no in range(1,3): # only for weeks 1&2 of 2019 so far
    
    url = f'https://theaudl.com/league/news/2019-audl-active-rosters-week-{week_no}'
    result = requests.get(url)
    
    soup = BeautifulSoup(result.text,'lxml')
    
    teams = [team.text for team in soup.find_all('h2')[:-1]]
    active_players = [players.text for players in soup.find_all('p') if len(players.text) > 250] # Hacky 
    somelist+=[{'Year':2019,'Week':week_no, 'Team':t,'Actives':aps.replace('\n','; ')} for t,aps in zip(teams, active_players)]
        
audlactive = pd.DataFrame(somelist)
audlactive.to_csv('../../data/teams/active_rosters.csv')