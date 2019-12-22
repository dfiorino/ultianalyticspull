import os
import pandas as pd
import importlib.resources as import_resources


def get_default_data_directory():
    with import_resources.path('ultianalyticspull.data','') as data_dir:
        return data_dir

def get_default_years():
    return [2014, 2015, 2016, 2017, 2018, 2019]

def extract_datetime(df, colname):
    df['datetime'] = pd.to_datetime(df[colname])
    df['date'] = df.datetime.dt.date
    df['year'] = df.datetime.dt.year
    return df


def load_league_data(years=get_default_years(),league='audl',data_dir=get_default_data_directory()):

    all_dfs = []
    league = league.lower()
    for year in years:
        files = [file for file in os.listdir(f'{data_dir}/{league}/{year}') if file.endswith('.csv')]
        all_dfs += [pd.read_csv(f'{data_dir}/{league}/{year}/{file}', index_col=0) for file in files]
    df = pd.concat(all_dfs,sort=False)

    df = extract_datetime(df, 'Date/Time')
    df.rename(columns={'Teamname': 'team', 'Opponent': 'opponent'}, inplace=True)
    df['game'] = df.team + "_" + df.opponent + "_" + df.date.map(str)

    return df

def load_team_data(filename:str=None):

    if filename.endswith('.csv'):
        df = pd.read_csv(filename)
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(filename)
    else:
        raise ValueError('`filename` is not CSV or XLSX')

    df = extract_datetime(df, 'Date/Time')
    df.rename(columns={'Teamname': 'team', 'Opponent': 'opponent'}, inplace=True)
    df['game'] = df.team + "_" + df.opponent + "_" + df.date.map(str)

    return df


def list_players(lineup: pd.Series):
    """
    Extract list of unique players appearing in lineups
    :param lineup: pd.Series of string values of comma-separated list of player names
    :return: np.array of unique players
    """
    return lineup.str.split(', ').apply(pd.Series).stack().unique()


def initialize_stats(df, stats: list):
    for s in stats:
        df[s] = 0
    return df


def count_possessions(df):
    return df.groupby(['GameID', 'PointID', 'PossessionID']).ngroups


def count_points(df):
    return df.groupby(['GameID', 'PointID']).ngroups


def count_games(df):
    return df.groupby(['GameID']).ngroups


def subset_gameplay(df_in, line=None, event_type=None, action=None, remove_cessation=False):

    df = df_in.copy()

    if line:
        assert line in ['O', 'D'], f'line {line} not supported'
        df = df.loc[df['Line'] == line]
    if event_type:
        assert event_type in ['Offense', 'Defense'], f'event_type {event_type} not supported'
        df = df.loc[df['Event Type'] == event_type]
    if action:
        assert action in ['Goal'], f'action {action} not supported'
        df = df.loc[df['Action'] == 'Goal']
    if remove_cessation:
        df = df.loc[df['Event Type'] != 'Cessation']
    return df
