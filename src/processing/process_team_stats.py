import pandas as pd
from .utils import load_data, team_index_vars, player_index_vars, list_players
from .stats import GetOPointsPlayed, GetOPossessionsPlayed, GetDPointsPlayed, GetDPossessionsPlayed, GetOPointsWon, GetDPointsWon
from .stats import calculate_conversion_rates, calculate_additive_stats


team_count_indicators = ['Goals', 'Goals Against', 'Holds', 'Breaks', 'Blocks', 'Drops', 'Throwaways', 'Turnovers']


def AggTeamStats(df):
    return pd.DataFrame({'O Points Played': GetOPointsPlayed(df),
                         'O Possessions Played': GetOPossessionsPlayed(df),
                         'D Points Played': GetDPointsPlayed(df),
                         'D Possessions Played': GetDPossessionsPlayed(df),
                         }, index=[0])


def make_team_indicators(df):

    df = initialize_stats(df, ['Throwaways', 'Drops'])

    # Conditions
    offense = df['Event Type'] == 'Offense'
    defense = df['Event Type'] == 'Defense'
    o_line = df['Line'] == 'O'
    d_line = df['Line'] == 'D'

    # Actions
    goal = df['Action'] == 'Goal'
    block = df['Action'] == 'D'
    drop = df['Action'] == 'Drop'
    throwaway = df['Action'] == 'Throwaway'

    # Make row-wise indicators
    df.loc[offense & goal, 'Goals'] = 1
    df.loc[defense & goal, 'Goals Against'] = 1
    df.loc[o_line & offense & goal, 'Holds'] = 1
    df.loc[d_line & offense & goal, 'Breaks'] = 1
    df.loc[defense & block, 'Blocks'] = 1
    df.loc[offense & drop, 'Drops'] = 1
    df.loc[offense & throwaway, 'Throwaways'] = 1
    df = calculate_additive_stats(df)
    df_wide1 = df.groupby(team_index_vars)[team_count_indicators].sum().reset_index()

    # Non row-wise indicators
    df_wide2 = df.groupby(team_index_vars).apply(AggTeamStats).reset_index().drop(columns='level_5')

    df_wide = pd.merge(df_wide1, df_wide2, on=team_index_vars)
    df_wide = calculate_conversion_rates(df_wide)

    # TODO - also sum and calculate_conversion_rates by Team/Year for EOY indicators

    return df_wide


def PlayStatsByPlayer(df_raw):
    plyrs = list_players(df_raw.Lineup)
    dfs = []
    for p in plyrs:
        df = df_raw[df_raw['Lineup'].str.contains(p,na=False)]
        df_p = pd.DataFrame({'player': p,
                             # 'Games Played': GetGamesPlayed(df),
                             # 'Quarters Played': GetQuartersPlayed(df),
                             # 'Points Played': GetPointsPlayed(df),
                             # 'Possessions Played': GetPossessionsPlayed(df),
                             'O Points Played': GetOPointsPlayed(df),
                             'Possessions Played (Offense)': GetOPossessionsPlayed(df),
                             # 'Opp Possessions Played (Offense)': GetOppOPossessionsPlayed(df),
                             'D Points Played': GetDPointsPlayed(df),
                             'Possessions Played (Defense)': GetOPossessionsPlayed(df),
                             # 'Opp Possessions Played (Defense)': GetOppDPossessionsPlayed(df),
                             # 'Points Won': GetPointsWon(df),
                             # 'Points Lost': GetPointsLost(df),
                             'Holds': GetOPointsWon(df),
                             # 'Points Lost (Offense)': GetOPointsLost(df),
                             'Breaks': GetDPointsWon(df),
                             # 'Points Lost (Defense)': GetDPointsLost(df),
                             }, index=[0])
        # print(len(df_p))
        dfs.append(df_p)

    return pd.concat(dfs, ignore_index=True)


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
    df_wide2 = df.groupby(player_index_vars[:-1]).apply(PlayStatsByPlayer).reset_index().drop('level_2', axis=1)

    df_wide = pd.merge(df_wide1, df_wide2, on=player_index_vars)
    df_wide = calculate_conversion_rates(df_wide)

    return df_wide
