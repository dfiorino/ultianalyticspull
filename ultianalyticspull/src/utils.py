import pandas as pd
import numpy as np
import glob
import csv
import os

__this_dir__ = os.path.dirname(os.path.realpath(__file__))

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

def audl_data(years : list = [2014,2015,2016,2017,2018,2019], processed : bool = True):
    """Get throw-by-throw data for each team. Raw data from Ultianalytics has been processed by AUDL Pull"""
    file_type = 'processed' if processed else 'raw'
    file_list = [file for yr in years for file in glob.glob(f'{__this_dir__}/../data/{file_type}/audl/{yr}/*csv')]
    return pd.concat([pd.read_csv(i) for i in file_list])

def pul_data(years : list = [2019], processed : bool = True):
    """Get throw-by-throw data for each team. Raw data from Ultianalytics has been processed by PUL Pull"""
    file_type = 'processed' if processed else 'raw'
    file_list = [file for yr in years for file in glob.glob(f'{__this_dir__}/../data/{file_type}/pul/{yr}/*csv')]
    return pd.concat([pd.read_csv(i) for i in file_list])

def get_audl_games():
    """Get DataFrame of all AUDL games"""
    return pd.read_csv(f'{__this_dir__}/../data/supplemental/audl/audl_games.csv')

# def get_pul_games():
#     """Get DataFrame of all PUL games"""
#     return pd.read_csv(f'{__this_dir__}/../data/supplemental/pul/pul_games.csv')

def get_audl_teams():
    """Get DataFrame of AUDL Team information."""
    return pd.read_csv(f'{__this_dir__}/../data/supplemental/audl/audl_teams.csv')

def get_pul_teams():
    """Get DataFrame of PUL Team information."""
    return pd.read_csv(f'{__this_dir__}/../data/supplemental/pul/pul_teams.csv')

def get_audl_weekly_rosters():
    """Get DataFrame of weekly AUDL active rosters."""
    return pd.read_csv(f'{__this_dir__}/../data/supplemental/audl/audl_weekly_active_rosters.csv')
