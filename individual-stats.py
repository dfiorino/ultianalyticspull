import pandas as pd
import glob
from functools import reduce

audl = pd.concat([pd.read_csv(dfteam, index_col=0) for dfteam in glob.glob('output/*.csv')])


def GetStat(df_slice, player_field,stat_name,aggfunc):
    stat = audl[df_slice].groupby(['Tournament',player_field,'Teamname']).apply(aggfunc)
    stat = stat.reset_index().rename(columns={'Tournament':'Year',player_field:'Name',0:stat_name})
    return stat

def GetCountStat(df_slice, player_field,stat_name):
    return GetStat(df_slice, player_field,stat_name,lambda x : len(x))

def GetSumStat(df_slice, player_field,stat_name,sum_stat):
    return GetStat(df_slice, player_field,stat_name,lambda x : sum(x[sum_stat]))


def SafeDivide(x,y):
    if y!=0:
        return x/y
    else:
        return 0
    
count_stat_list= [
                        # Catching
                        [(audl.Action=='Goal'), 'Receiver','Goals'],
                        [(audl.Action.isin(['Goal','Catch'])), 'Receiver','Catches'],
                        [(audl.Action=='Drop'), 'Receiver','Drops'],
                        # Throwing
                        [(audl.Action=='Goal'), 'Passer','Assists'],
                        [([True]*len(audl)), 'Passer','Throws'],
                        [(audl.Action.isin(['Goal','Catch'])), 'Passer','Completions'],
                        [(audl.Action.isin(['Throwaway','Callahan'])),'Passer','Throwaways'],
                        [(audl.Action=='Drop'), 'Passer','Throws Dropped'],
                        [(audl.Action.isin(['Goal','Catch'])&~pd.isnull(audl['Absolute Distance'])), 'Passer',
                            'Throws Recorded with Yardage'],
                        [(audl.Action=='MiscPenalty'),'Passer','Fouls Drawn'],
                        [(audl.Action=='Stall'),'Passer','Stalls'],
                        # Defense
                        [(audl.Action.isin(['D','Callahan'])), 'Defender', 'Blocks'],
                        [(audl.Action=='Callahan'), 'Defender','Callahans'],
                        [audl.Action.isin(['Pull','PullOb']), 'Defender', 'Pulls'],
                        [(audl.Action=='PullOb'), 'Defender', 'Pulls (Out-of-bounds)'],
                        [audl.Action.isin(['Pull','PullOb'])&~pd.isnull(audl['Absolute Distance']), 'Defender',
                             'Pulls Recorded with Yardage'],
                        [(audl.Action=='Pull')&~pd.isnull(audl['Absolute Distance']), 'Defender',
                             'Pulls (Inbounds) Recorded with Yardage'],

    ]




sum_stat_list = [
                        [audl.Action.isin(['Goal','Catch'])&~pd.isnull(audl['Absolute Distance']),
                         'Passer','Throwing Yards','Absolute Distance'],
    
                        [audl.Action.isin(['Goal','Catch'])&~pd.isnull(audl['Lateral Distance']),
                         'Passer','Lateral Throwing Yards','Lateral Distance'],
    
                        [audl.Action.isin(['Goal','Catch'])&~pd.isnull(audl['Toward Our Goal Distance']),
                         'Passer','Forward Throwing Yards','Toward Our Goal Distance'],

                        [audl.Action.isin(['Pull','PullOb'])&~pd.isnull(audl['Absolute Distance']),
                         'Defender','Pull Yards','Absolute Distance'],

                        [(audl.Action=='Pull')&~pd.isnull(audl['Absolute Distance']),
                         'Defender','Pull Yards (Inbounds)','Absolute Distance']
                       ]


df_stat_list = [GetCountStat(i,j,k) for i,j,k in count_stat_list] + \
                [GetSumStat(i,j,k,l) for i,j,k,l in sum_stat_list] 

stats_out = reduce(lambda  left,right: pd.merge(left,right,on=['Year','Teamname','Name'],
                                                how='outer'), 
                                                df_stat_list).fillna(0)

def GetPlayers(df_in):
    return df_in['Lineup'].str.split(', ').apply(pd.Series).stack().unique()

def GetGamesPlayed(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID']).ngroups
def GetQuartersPlayed(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','QuarterID']).ngroups
def GetPointsPlayed(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID']).ngroups
def GetPossessionsPlayed(df_in,plyr):
    return df_in[(df_in['Event Type']=='Offense')&df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID','PossessionID']).ngroups

def GetPointsWon(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)&(df_in['Event Type']=='Offense')&(df_in.Action=='Goal')].groupby(['GameID','PointID']).ngroups
def GetPointsLost(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)&(df_in['Event Type']=='Defense')&(df_in.Action=='Goal')].groupby(['GameID','PointID']).ngroups

def GetOPointsWon(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)
                 &(df_in['Event Type']=='Offense')
                 &(df_in.Action=='Goal')
                 &(df_in.Line=='O')].groupby(['GameID','PointID']).ngroups
def GetOPointsLost(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)
                 &(df_in['Event Type']=='Defense')
                 &(df_in.Action=='Goal')
                 &(df_in.Line=='O')].groupby(['GameID','PointID']).ngroups
def GetDPointsWon(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)
                 &(df_in['Event Type']=='Offense')
                 &(df_in.Action=='Goal')
                 &(df_in.Line=='D')].groupby(['GameID','PointID']).ngroups
def GetDPointsLost(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)
                 &(df_in['Event Type']=='Defense')
                 &(df_in.Action=='Goal')
                 &(df_in.Line=='D')].groupby(['GameID','PointID']).ngroups

def GetOPointsPlayed(df_in,plyr):
    return df_in[(df_in.Line=='O')&df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID']).ngroups
def GetOPossessionsPlayed(df_in,plyr):
    return df_in[(df_in.Line=='O')&(df_in['Event Type']=='Offense')&df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID','PossessionID']).ngroups
def GetDPointsPlayed(df_in,plyr):
    return df_in[(df_in.Line=='D')&df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID']).ngroups
def GetDPossessionsPlayed(df_in,plyr):
    return df_in[(df_in.Line=='D')&(df_in['Event Type']=='Offense')&df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID','PossessionID']).ngroups


def PlayStatsByPlayer(df_in):
    plyrs = GetPlayers(df_in)
    return pd.DataFrame([{'Name': p, 
                          'Games Played': GetGamesPlayed(df_in,p),
                          'Quarters Played': GetQuartersPlayed(df_in,p),
                          'Points Played': GetPointsPlayed(df_in,p),
                          'Possessions Played': GetPossessionsPlayed(df_in,p),
                          'Points Played (Offense)': GetOPointsPlayed(df_in,p),
                          'Possessions Played (Offense)': GetOPossessionsPlayed(df_in,p),
                          'Points Played (Defense)': GetDPointsPlayed(df_in,p),
                          'Possessions Played (Defense)': GetDPossessionsPlayed(df_in,p),
                          'Points Won': GetPointsWon(df_in,p),
                          'Points Lost': GetPointsLost(df_in,p),
                          'Points Won (Offense)': GetOPointsWon(df_in,p),
                          'Points Lost (Offense)': GetOPointsLost(df_in,p),
                          'Points Won (Defense)': GetDPointsWon(df_in,p),
                          'Points Lost (Defense)': GetDPointsLost(df_in,p),
                         } for p in plyrs])

gameplay_stats = audl.groupby(['Teamname','Tournament']).apply(PlayStatsByPlayer).reset_index().rename(columns={'Tournament':'Year'}).drop('level_2',axis=1)

stats_out = pd.merge(gameplay_stats,stats_out,on=['Teamname','Year','Name'],how='outer')

secondary_stats = [ 
                        ['Completion Percentage', lambda x : 100*SafeDivide(x.Completions,x.Throws)],
                        ['Catches Per Goals', lambda x : SafeDivide(x.Catches,x.Goals)],
                        ['Throws Per Assist', lambda x : SafeDivide(x.Throws,x.Assists)],
                        ['Throwaway Percentage', lambda x : SafeDivide(x.Throwaways,x.Throws)],
                        ['Drop Percentage', lambda x : SafeDivide(x.Drops,(x.Drops + x.Catches))],  
                        ['Yards Per Throw', lambda x : SafeDivide(x['Throwing Yards'],
                                                                  x['Throws Recorded with Yardage'])],    
                        ['Yards Per Pull', lambda x : SafeDivide(x['Pull Yards'],
                                                                 x['Pulls Recorded with Yardage'])],  
                        ['Yards Per Pull (Inbounds)', lambda x : SafeDivide(x['Pull Yards (Inbounds)'],
                                                                            x['Pulls (Inbounds) Recorded with Yardage'])],    
                     ]

for sec_stat,aggfunc in secondary_stats:
    stats_out[sec_stat] = stats_out.apply(aggfunc,axis=1)
        
stats_out.to_csv('output/IndividualStats.csv',sep=',',index=False)