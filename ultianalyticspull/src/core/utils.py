import pandas as pd
import numpy as np
import requests
import glob
import csv

def get_leagues():
    """
    :return: list of leagues that are setup for ultianalyticspull
    """
    return ['audl','pul']

def team_data(team_number,
              password = None):
    base_url = 'http://www.ultianalytics.com/'
    team_url = f'{base_url}/rest/view/team/{team_number}/'
    teamdata_url =  f'{team_url}/stats/export'

    if password is not None:
        # Grab cookies after submitting password if private account
        teamauth_url = f'{team_url}/authenticate/{password}'
        cookies = requests.post(teamauth_url).cookies
    else:
        cookies = []

    response = requests.get(teamdata_url, cookies=cookies)
    return response.content.decode("utf-8")

def team_dataframe(team_number,
                   password = None):

    data = team_data(team_number=team_number, password=password )
    arr = [row.split(',') for row in data.split('\n')]

    header = arr[0]
    teamlog = arr[1:len(arr)-1]

    ncols = len(header)
    teamlog = [row[:ncols] if len(row) > ncols else row+['']*(ncols-len(row)) for row in teamlog]

    return pd.DataFrame(teamlog,columns=header).replace('',np.nan)

def csv2dataframe(filename : str):
    """Read CSV as Pandas DataFrame but deal with inconsistent use of commas in CSV"""
    teamlog = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        header = next(reader)
        teamlog = list(reader)
    # Deal with sticky situation of rows with more or less CSV's than the header
    ncols = len(header)
    teamlog = [e[:ncols] if len(e) > ncols else e+['']*(ncols-len(e)) for e in teamlog]

    return pd.DataFrame(teamlog,columns=header)

def make_game_over_line(df_in):
    gameoverline = df_in.copy()
    gameoverline['Action'] = 'GameOver'
    gameoverline['Event Type'] = 'Cessation'
    gameoverline['Passer'] = ''
    gameoverline['Receiver'] = ''
    gameoverline['Defender'] = ''
    gameoverline['Hang Time (secs)'] = np.nan
    gameoverline['Begin Area']              =np.nan
    gameoverline['Begin X']                 =np.nan
    gameoverline['Begin Y']                 =np.nan
    gameoverline['End Area']                =np.nan
    gameoverline['End X']                   =np.nan
    gameoverline['End Y']                   =np.nan
    gameoverline['Distance Unit of Measure']=np.nan
    gameoverline['Absolute Distance']       =np.nan
    gameoverline['Lateral Distance']        =np.nan
    gameoverline['Toward Our Goal Distance']=np.nan
    return gameoverline.to_frame().T
