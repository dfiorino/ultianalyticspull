import urllib.request
import time
import os 

teaminfo=pd.read_csv('../../data/supplemental/teams.csv')
abbrev2full = pd.Series(teaminfo[teaminfo.Active].Teamname.values,index=teaminfo[teaminfo.Active]['Team Abv'].values).to_dict()

for abbr in teaminfo[teaminfo.Active]['Team Abv']:
    url = f'https://theaudl.com/sites/default/files/logo-team-{abbr}.png'
    print(abbr)
    save_to = f'../../images/audl-logos/logo-team-{abbr}.png'
    if not os.path.isfile(save_to):
        urllib.request.urlretrieve(url,save_to)
