import os
import pandas as pd
from pathlib import Path

DATA_DIR = str(Path(__file__).parent.parent.parent/'data')
YEARS = [2014]  # [2014, 2015, 2016, 2017, 2018]  # [2014]

team_index_vars = ['year', 'team', 'opponent', 'date', 'game']
# NOTE - the current player functions get prohibitively slow if indexed on game
player_index_vars = ['year', 'team', 'player']
team_indicators = ['Goals', 'Catches', 'Ds', 'Turnovers', 'Drops', 'Throwaways', 'Goals_against',
                   'Hold_pct', 'Break_pct']
team_eoy_indicators = team_indicators + ['Win_pct'] # ['Win_pct', 'Hold_pct', 'Break_pct']
player_sum_indicators = ['Completions', 'Assists', 'Throwaways', 'Receptions', 'Goals', 'Drops', 'Ds']


def extract_datetime(df, colname):
    df['datetime'] = pd.to_datetime(df[colname])
    df['date'] = df.datetime.dt.date
    df['year'] = df.datetime.dt.year
    return df


def load_data():
    all_dfs = []
    for year in YEARS:
        files = os.listdir(f'{DATA_DIR}/processed/{year}')
        all_dfs += [pd.read_csv(f'{DATA_DIR}/processed/{year}/{f}', index_col=0) for f in files]
    df = pd.concat(all_dfs)

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
