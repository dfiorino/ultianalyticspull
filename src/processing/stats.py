def GetOPointsPlayed(df):
    return df[(df['Event Type'] != 'Cessation') & (df.Line == 'O')].groupby(['GameID', 'PointID']).ngroups


def GetOPossessionsPlayed(df):
    return df[(df.Line == 'O') & (df['Event Type'] == 'Offense')].groupby(['GameID', 'PointID', 'PossessionID']).ngroups


def GetDPointsPlayed(df):
    return df[(df['Event Type'] != 'Cessation') & (df.Line == 'D')].groupby(['GameID', 'PointID']).ngroups


def GetDPossessionsPlayed(df):
    return df[(df.Line == 'D') & (df['Event Type'] == 'Offense')].groupby(['GameID', 'PointID', 'PossessionID']).ngroups


def calculate_conversion_rates(df):
    df['Hold Rate'] = df['Holds'] / df['O Points Played']
    df['Break Rate'] = df['Breaks'] / df['D Points Played']
    return df
