import pandas as pd
from .utils import list_players


def calculate_conversion_rates(df):
    df['Hold Rate'] = df['Holds'] / df['O Points Played']
    df['Break Rate'] = df['Breaks'] / df['D Points Played']
    df['Scoring Efficiency'] = df['Points Won'] / df['Possessions Played']
    df['O-line Scoring Efficiency'] = df['Holds'] / df['O Possessions Played']
    df['D-line Scoring Efficiency'] = df['Breaks'] / df['D Possessions Played']
    df['O-line Takeaway Efficiency'] = 1 - (df['O Points Lost'] / df['Opponent Possessions Played (O-Line)'])
    df['D-line Takeaway Efficiency'] = 1 - (df['D Points Lost'] / df['Opponent Possessions Played (D-Line)'])
    return df


def calculate_gameplay_stats(df):
    return pd.DataFrame({'O Points Played': count_o_points(df),
                         'O Possessions Played': count_o_possessions(df),
                         'D Points Played': count_d_points(df),
                         'D Possessions Played': count_d_possessions(df),
                         'Holds': count_holds(df),
                         'Breaks': count_breaks(df),
                         'Points Won': count_points_won(df),  # TODO - could sum O and D points scored
                         'Games Played': count_games(df),
                         'Points Played': count_points(df),  # TODO - could sum O and D points
                         'Possessions Played': count_possessions(df),  # TODO - could sum O and D possessions
                         'Opponent Possessions Played (O-Line)': count_opponent_o_possessions(df),
                         'Opponent Possessions Played (D-Line)': count_opponent_d_possessions(df),
                         'O Points Lost': count_o_points_lost(df),  # TODO - could do O points - Holds
                         'D Points Lost': count_d_points_lost(df),  # TODO - could do D points - Breaks
                         }, index=[0])


def calculate_gameplay_stats_by_player(df_raw):
    plyrs = list_players(df_raw.Lineup)
    dfs = []
    for p in plyrs:
        df = df_raw[df_raw['Lineup'].str.contains(p, na=False)]
        df_p = calculate_gameplay_stats(df)
        df_p['player'] = p
        dfs.append(df_p)

    return pd.concat(dfs, ignore_index=True)


def count_o_points(df):
    return df[(df['Event Type'] != 'Cessation') & (df.Line == 'O')].groupby(['GameID', 'PointID']).ngroups


def count_o_possessions(df):
    return df[(df.Line == 'O') & (df['Event Type'] == 'Offense')].groupby(['GameID', 'PointID', 'PossessionID']).ngroups


def count_d_points(df):
    return df[(df['Event Type'] != 'Cessation') & (df.Line == 'D')].groupby(['GameID', 'PointID']).ngroups


def count_d_possessions(df):
    return df[(df.Line == 'D') & (df['Event Type'] == 'Offense')].groupby(['GameID', 'PointID', 'PossessionID']).ngroups


def count_holds(df):
    return df[(df['Event Type'] == 'Offense')
              & (df.Action == 'Goal')
              & (df.Line == 'O')].groupby(['GameID', 'PointID']).ngroups


def count_breaks(df):
    return df[(df['Event Type'] == 'Offense')
              & (df.Action == 'Goal')
              & (df.Line == 'D')].groupby(['GameID', 'PointID']).ngroups


def count_points_won(df):
    return df[(df['Event Type'] == 'Offense') & (df.Action == 'Goal')].groupby(['GameID', 'PointID']).ngroups


def count_games(df):
    return df.groupby(['GameID']).ngroups


def count_points(df):
    return df[(df['Event Type'] != 'Cessation')].groupby(['GameID', 'PointID']).ngroups


def count_possessions(df):
    return df[(df['Event Type'] == 'Offense')].groupby(['GameID', 'PointID', 'PossessionID']).ngroups


def count_o_points_lost(df):
    return df[(df['Event Type'] == 'Defense')
              & (df.Action == 'Goal')
              & (df.Line == 'O')].groupby(['GameID', 'PointID']).ngroups


def count_d_points_lost(df):
    return df[(df['Event Type'] == 'Defense')
              & (df.Action == 'Goal')
              & (df.Line == 'D')].groupby(['GameID', 'PointID']).ngroups


def count_opponent_o_possessions(df):
    return df[(df.Line == 'O') & (df['Event Type'] == 'Defense')].groupby(['GameID', 'PointID', 'PossessionID']).ngroups


def count_opponent_d_possessions(df):
    return df[(df.Line == 'D') & (df['Event Type'] == 'Defense')].groupby(['GameID', 'PointID', 'PossessionID']).ngroups


def calculate_additive_stats(df, entity='team'):
    df['Turnovers'] = df['Drops'] + df['Throwaways']
    if entity == 'player':
        df['Plus_Minus'] = df.Goals + df.Assists + df.Blocks - df.Turnovers
    return df

# BELOW FUNCTIONS ARE NOT CURRENTLY USED
# def count_quarters(df):
#     return df.groupby(['GameID', 'QuarterID']).ngroups
#
#
# def count_points_lost(df):
#     return df[(df['Event Type'] == 'Defense') & (df.Action == 'Goal')].groupby(['GameID', 'PointID']).ngroups
#
#
