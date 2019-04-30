def GetOPointsPlayed(df):
    return df[(df['Event Type'] != 'Cessation') & (df.Line == 'O')].groupby(['GameID', 'PointID']).ngroups


def GetOPossessionsPlayed(df):
    return df[(df.Line == 'O') & (df['Event Type'] == 'Offense')].groupby(['GameID', 'PointID', 'PossessionID']).ngroups


def GetDPointsPlayed(df):
    return df[(df['Event Type'] != 'Cessation') & (df.Line == 'D')].groupby(['GameID', 'PointID']).ngroups


def GetDPossessionsPlayed(df):
    return df[(df.Line == 'D') & (df['Event Type'] == 'Offense')].groupby(['GameID', 'PointID', 'PossessionID']).ngroups


def GetOPointsWon(df):
    return df[(df['Event Type']=='Offense')
              &(df.Action=='Goal')
              &(df.Line=='O')].groupby(['GameID','PointID']).ngroups


def GetDPointsWon(df):
    return df[(df['Event Type']=='Offense')
              &(df.Action=='Goal')
              &(df.Line=='D')].groupby(['GameID','PointID']).ngroups


def calculate_additive_stats(df, entity='team'):
    df['Turnovers'] = df['Drops'] + df['Throwaways']
    if entity == 'player':
        df['Plus_Minus'] = df.Goals + df.Assists + df.Blocks - df.Turnovers
    return df


def calculate_conversion_rates(df):
    df['Hold Rate'] = df['Holds'] / df['O Points Played']
    df['Break Rate'] = df['Breaks'] / df['D Points Played']
    return df
