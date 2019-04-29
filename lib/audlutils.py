import pandas as pd
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


def audl_data(years : list = [2014,2015,2016,2017,2018,2019], processed : bool = True):
    """Get throw-by-throw data for each team. Raw data from Ultianalytics has been processed by AUDL Pull"""
    file_type = 'processed' if processed else 'raw'
    file_list = [file for yr in years for file in glob.glob(f'{__this_dir__}/../data/{file_type}/{yr}/*csv')]
    return pd.concat([pd.read_csv(i) for i in file_list])

def get_games():
    """Get DataFrame of all AUDL games"""
    return pd.read_csv(f'{__this_dir__}/../data/supplemental/games.csv')

def get_teams():
    """Get DataFrame of AUDL Team information."""
    return pd.read_csv(f'{__this_dir__}/../data/supplemental/teams.csv')

def get_weekly_rosters():
    """Get DataFrame of weekly active rosters."""
    return pd.read_csv(f'{__this_dir__}/../data/supplemental/weekly_active_rosters.csv')