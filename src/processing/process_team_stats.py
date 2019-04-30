import pandas as pd
from .utils import load_data, team_index_vars
from .stats import GetOPointsPlayed, GetOPossessionsPlayed, GetDPointsPlayed, GetDPossessionsPlayed
from .stats import calculate_conversion_rates


team_count_indicators = ['Goals', 'Goals Against', 'Holds', 'Breaks', 'Blocks', 'Drops', 'Throwaways', 'Turnovers']


def AggTeamStats(df):
    return pd.DataFrame({'O Points Played': GetOPointsPlayed(df),
                         'O Possessions Played': GetOPossessionsPlayed(df),
                         'D Points Played': GetDPointsPlayed(df),
                         'D Possessions Played': GetDPossessionsPlayed(df),
                         }, index=[0])


def make_team_indicators(df):

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
    df.loc[offense & throwaway, 'Throwaways'] = 1  # TODO - BUGFIX - currently Na + 1 = Na
    df['Turnovers'] = df['Drops'] + df['Throwaways']
    df_wide1 = df.groupby(team_index_vars)[team_count_indicators].sum().reset_index()

    # Non row-wise indicators
    df_wide2 = df.groupby(team_index_vars).apply(AggTeamStats).reset_index().drop(columns='level_5')

    df_wide = pd.merge(df_wide1, df_wide2, on=team_index_vars)
    df_wide = calculate_conversion_rates(df_wide)

    # TODO - also sum and calculate_conversion_rates by Team/Year for EOY indicators

    return df_wide
