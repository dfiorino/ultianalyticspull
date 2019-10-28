import urllib.request
import time
import os
import importlib.resources as import_resources

def get_audl_team_logos():

    with import_resources.path('ultianalyticspull.data.supplemental.audl', 'audl_teams.csv') as audl_teams:
        teaminfo=pd.read_csv(audl_teams)
    abbrev2full = pd.Series(teaminfo[teaminfo.Active].Teamname.values,index=teaminfo[teaminfo.Active]['Team Abv'].values).to_dict()

    for abbr in teaminfo[teaminfo.Active]['Team Abv']:
        url = f'https://theaudl.com/sites/default/files/logo-team-{abbr}.png'
        print(abbr)
        with import_resources.path('ultianalyticspull.images.audl-logos', f'logo-team-{abbr}.png')as save_to
            urllib.request.urlretrieve(url,save_to)

if __name__=="__main__":
    get_audl_team_logosd()
