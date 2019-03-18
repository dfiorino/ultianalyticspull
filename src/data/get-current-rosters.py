import pandas as pd
import glob
import requests
from bs4 import BeautifulSoup
import os

team_info = pd.read_csv('../../data/teams/audlteaminfo.csv')

somelist=[]
for i,row in team_info[team_info.Active].iterrows():
    print(row['Teamname'])
    mini_nickname = row['Nickname'].lower().replace(' ','')
    url  = f'https://www.theaudl.com/{mini_nickname}/players'
    result = requests.get(url)
    
    soup = BeautifulSoup(result.text,'lxml')
    for j in (soup.find_all('div', {'class':"views-field views-field-player-field-player-display-name"})):
        player_name = j.text.strip(' ').replace('  ',' ').replace('- ','-')
        somelist.append([row['Teamname'],player_name])
        
audldotcom_rosters = pd.DataFrame(somelist,columns=['Teamname','Name'])


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

audldotcom_rosters['FirstName'] = audldotcom_rosters.Name.apply(lambda x : x.split(' ')[0])
audldotcom_rosters['LastName'] = audldotcom_rosters.Name.apply(lambda x : ' '.join(x.split(' ')[1:]))

audldotcom_rosters.to_csv('../../data/players/current_rosters.csv')
