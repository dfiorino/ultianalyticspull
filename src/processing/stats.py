import pandas as pd
from .utils import list_players, count_points, count_possessions, count_games, subset_gameplay, initialize_stats


def define_action_types(df):
    goal = df['Action'].isin(['Goal', 'Callahan'])
    block = df['Action'].isin(['D', 'Callahan'])
    drop = df['Action'] == 'Drop'
    throwaway = df['Action'].isin(['Throwaway', 'Callahan'])
    catch = df['Action'].isin(['Catch', 'Goal'])
    callahan = df['Action'] == 'Callahan'
    stall = df['Action'] == 'Stall'

    return [goal, block, drop, throwaway, catch, callahan, stall]


def calculate_sum_stats(df, index_vars, entity='team'):
    # TODO - figure out where to put lists of stats
    cols = ['Assists', 'Hockey Assists', 'Throwaways', 'Completions', 'Catches', 'Goals', 'Drops', 'Blocks',
            'Callahans', 'Stalls', 'Callahans Thrown']
    initialize_stats(df, cols)

    # TODO - could do via a melt?
    df_t = df.rename(columns={'Passer': 'player'})
    df_t['type'] = 'Passer'
    df_r = df.rename(columns={'Receiver': 'player'})
    df_r['type'] = 'Receiver'
    df_d = df.rename(columns={'Defender': 'player'})
    df_d['type'] = 'Defender'

    df_long = pd.concat([df_t, df_r, df_d], sort=False)

    passer = df_long.type == 'Passer'
    receiver = df_long.type == 'Receiver'
    defender = df_long.type == 'Defender'

    goal, block, drop, throwaway, catch, callahan, stall = define_action_types(df_long)

    offense = df_long['Event Type'] == "Offense"
    defense = df_long['Event Type'] == "Defense"

    # Thrower
    df_long.loc[offense & passer & goal, 'Assists'] = 1
    df_long.loc[offense & passer & (catch | goal), 'Completions'] = 1
    df_long.loc[offense & passer & (df_long.Action.shift(-1) == 'Goal') & (
                df_long['Event Type'].shift(-1) == 'Offense'), 'Hockey Assists'] = 1
    df_long.loc[offense & passer & (throwaway | callahan), 'Throwaways'] = 1
    df_long.loc[offense & passer & callahan, 'Callahans Thrown'] = 1
    df_long.loc[offense & passer & stall, 'Stalls'] = 1

    # Receiver
    df_long.loc[offense & receiver & (catch | goal), 'Catches'] = 1
    df_long.loc[offense & receiver & drop, 'Drops'] = 1

    # Defender
    df_long.loc[defense & defender & block, 'Blocks'] = 1
    df_long.loc[defense & defender & callahan, 'Callahans'] = 1

    # Combined
    df_long.loc[(offense & receiver & goal) | (defense & defender & callahan), 'Goals'] = 1
    df_long['Turnovers'] = df_long['Drops'] + df_long['Throwaways'] + df_long['Stalls']

    if entity == 'player':
        df['Plus_Minus'] = df.Goals + df.Assists + df.Blocks - df.Turnovers

    return df_long.groupby(index_vars)[cols].sum().reset_index()


def calculate_gameplay_stats(df):
    df_o = subset_gameplay(df, line="O", remove_cessation=True)
    df_d = subset_gameplay(df, line="D", remove_cessation=True)

    return pd.DataFrame({'O Points Played': count_points(df_o),
                         'O Possessions Played': count_possessions(df_o),
                         'D Points Played': count_points(df_d),
                         'D Possessions Played': count_possessions(df_d),
                         'Holds': count_points(subset_gameplay(df_o, event_type='Offense', action='Goal')),
                         'Breaks': count_points(subset_gameplay(df_d, event_type='Offense', action='Goal')),
                         'Points Won': count_points(subset_gameplay(df, event_type='Offense', action='Goal')),
                         # TODO - could sum O and D points scored
                         'Games Played': count_games(df),
                         'Points Played': count_points(df),  # TODO - could sum O and D points
                         'Possessions Played': count_possessions(df),  # TODO - could sum O and D possessions
                         'Opponent Possessions Played (O-Line)': count_possessions(
                             subset_gameplay(df_o, event_type='Defense')),
                         'Opponent Possessions Played (D-Line)': count_possessions(
                             subset_gameplay(df_d, event_type='Defense')),
                         'O Points Lost': count_points(subset_gameplay(df_o, event_type='Defense', action='Goal')),
                         # TODO - could do O points - Holds
                         'D Points Lost': count_points(subset_gameplay(df_d, event_type='Defense', action='Goal')),
                         # TODO - could do D points - Breaks
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


def calculate_conversion_rates(df):
    df['Hold Rate'] = df['Holds'] / df['O Points Played']
    df['Break Rate'] = df['Breaks'] / df['D Points Played']
    df['Scoring Efficiency'] = df['Points Won'] / df['Possessions Played']
    df['O-line Scoring Efficiency'] = df['Holds'] / df['O Possessions Played']
    df['D-line Scoring Efficiency'] = df['Breaks'] / df['D Possessions Played']
    df['O-line Takeaway Efficiency'] = 1 - (df['O Points Lost'] / df['Opponent Possessions Played (O-Line)'])
    df['D-line Takeaway Efficiency'] = 1 - (df['D Points Lost'] / df['Opponent Possessions Played (D-Line)'])
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
