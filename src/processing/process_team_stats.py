import pandas as pd
from .utils import load_data, team_index_vars, player_index_vars
from .stats import calculate_conversion_rates, calculate_additive_stats
from .stats import calculate_gameplay_stats, calculate_gameplay_stats_by_player

team_count_indicators = ['Goals', 'Goals Against', 'Blocks', 'Drops', 'Throwaways', 'Turnovers']


def make_team_indicators(df):
    df = initialize_stats(df, ['Throwaways', 'Drops'])

    # Conditions
    offense = df['Event Type'] == 'Offense'
    defense = df['Event Type'] == 'Defense'
    goal = df['Action'] == 'Goal'
    block = df['Action'] == 'D'
    drop = df['Action'] == 'Drop'
    throwaway = df['Action'] == 'Throwaway'

    # Make row-wise indicators
    df.loc[offense & goal, 'Goals'] = 1
    df.loc[defense & goal, 'Goals Against'] = 1
    df.loc[defense & block, 'Blocks'] = 1
    df.loc[offense & drop, 'Drops'] = 1
    df.loc[offense & throwaway, 'Throwaways'] = 1
    df = calculate_additive_stats(df)
    df_wide1 = df.groupby(team_index_vars)[team_count_indicators].sum().reset_index()

    # Non row-wise indicators
    df_wide2 = df.groupby(team_index_vars).apply(calculate_gameplay_stats).reset_index().drop(columns='level_5')

    df_wide = pd.merge(df_wide1, df_wide2, on=team_index_vars)
    df_wide = calculate_conversion_rates(df_wide)

    # TODO - also sum and calculate_conversion_rates by Team/Year for EOY indicators

    return df_wide


# TODO - clean up all lists of stat names
PLAYER_SUM_INDICATORS = ['Completions', 'Assists', 'Throwaways', 'Receptions', 'Goals', 'Drops', 'Blocks']


# TODO - move and clean up
def initialize_stats(df, stats: list):
    for s in stats:
        df[s] = 0
    return df


def make_player_indicators(df):
    df = initialize_stats(df, PLAYER_SUM_INDICATORS)

    # Actions
    goal = df['Action'] == 'Goal'
    block = df['Action'] == 'D'
    drop = df['Action'] == 'Drop'
    throwaway = df['Action'] == 'Throwaway'
    completion = df['Action'] == 'Catch'

    # Make passing row-wise indicators
    df_p = df.copy()
    df_p['player'] = df['Passer']
    df_p.loc[completion, 'Completions'] = 1
    df_p.loc[goal, 'Assists'] = 1
    df_p.loc[throwaway, 'Throwaways'] = 1

    # Make receiving row-wise indicators
    df_r = df.copy()
    df_r['player'] = df['Receiver']
    df_r.loc[completion, 'Receptions'] = 1
    df_r.loc[goal, 'Goals'] = 1
    df_r.loc[drop, 'Drops'] = 1

    # Make defensive row-wise indicators
    df_d = df.copy()
    df_d['player'] = df['Defender']
    df_d.loc[block, 'Blocks'] = 1

    df_all = pd.concat([df_p, df_r, df_d], sort=False)
    df_wide1 = df_all.groupby(player_index_vars)[PLAYER_SUM_INDICATORS].sum().reset_index()
    df_wide1 = calculate_additive_stats(df_wide1, entity='player')

    # Non row-wise indicators
    df_wide2 = df.groupby(player_index_vars[:-1]).apply(calculate_gameplay_stats_by_player).reset_index().drop(
        'level_2', axis=1)

    df_wide = pd.merge(df_wide1, df_wide2, on=player_index_vars)
    df_wide = calculate_conversion_rates(df_wide)

    return df_wide
