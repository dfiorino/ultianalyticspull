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
                        [(audl.Action=='MiscPenalty'),'Passer','Fouls Against'],
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


other_stat_list = [
                        [audl.Action.isin(['Goal','Catch'])&~pd.isnull(audl['Absolute Distance']),
                         'Passer',
                         'Throwing Yards',
                         lambda x : sum(x['Absolute Distance'])],
                        [audl.Action.isin(['Goal','Catch'])&~pd.isnull(audl['Lateral Distance']),
                         'Passer',
                         'Lateral Throwing Yards',
                         lambda x : sum(x['Lateral Distance'])],
                        [audl.Action.isin(['Goal','Catch'])&~pd.isnull(audl['Toward Our Goal Distance']),
                         'Passer',
                         'Forward Throwing Yards',
                         lambda x : sum(x['Toward Our Goal Distance'])],

                        [audl.Action.isin(['Pull','PullOb'])&~pd.isnull(audl['Absolute Distance']),
                         'Defender',
                         'Pull Yards',
                         lambda x : sum(x['Absolute Distance'])],

                        [(audl.Action=='Pull')&~pd.isnull(audl['Absolute Distance']),
                         'Defender',
                         'Pull Yards (Inbounds)',
                         lambda x : sum(x['Absolute Distance'])]

                       ]

df_stat_list = [GetCountStat(i,j,k) for i,j,k in count_stat_list] + \
                [GetStat(i,j,k,l) for i,j,k,l in other_stat_list]


stats_out = reduce(lambda  left,right: pd.merge(left,right,on=['Year','Teamname','Name'],
                                                how='outer'), 
                                                df_stat_list).fillna(0)

    
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
        
stats_out.to_csv('output/IndividualStats.csv',sep=',')