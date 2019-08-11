import pandas as pd
import numpy as np
# import glob
from functools import reduce


def safe_divide(x,y):
    if y!=0:
        return x/y
    else:
        return 0

def get_games_played(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID']).ngroups
def get_quarters_played(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','QuarterID']).ngroups
def get_points_played(df_in,plyr):
    return df_in[(df_in['Event Type']!='Cessation') & df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID']).ngroups
def get_possessions_played(df_in,plyr):
    return df_in[(df_in['Event Type']=='Offense')&df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID','PossessionID']).ngroups

def get_points_won(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)&(df_in['Event Type']=='Offense')&(df_in.Action=='Goal')].groupby(['GameID','PointID']).ngroups
def get_points_lost(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)&(df_in['Event Type']=='Defense')&(df_in.Action=='Goal')].groupby(['GameID','PointID']).ngroups

def get_o_points_won(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)
                 &(df_in['Event Type']=='Offense')
                 &(df_in.Action=='Goal')
                 &(df_in.Line=='O')].groupby(['GameID','PointID']).ngroups
def get_o_points_lost(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)
                 &(df_in['Event Type']=='Defense')
                 &(df_in.Action=='Goal')
                 &(df_in.Line=='O')].groupby(['GameID','PointID']).ngroups

def get_d_points_won(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)
                 &(df_in['Event Type']=='Offense')
                 &(df_in.Action=='Goal')
                 &(df_in.Line=='D')].groupby(['GameID','PointID']).ngroups
def get_d_points_lost(df_in,plyr):
    return df_in[df_in['Lineup'].str.contains(plyr,na=False)
                 &(df_in['Event Type']=='Defense')
                 &(df_in.Action=='Goal')
                 &(df_in.Line=='D')].groupby(['GameID','PointID']).ngroups

def get_o_points_played(df_in,plyr):
    return df_in[(df_in['Event Type']!='Cessation') & (df_in.Line=='O')&df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID']).ngroups
def get_o_possessions_played(df_in,plyr):
    return df_in[(df_in.Line=='O')&(df_in['Event Type']=='Offense')&df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID','PossessionID']).ngroups
def get_opp_o_possessions_played(df_in,plyr):
    return df_in[(df_in.Line=='O')&(df_in['Event Type']=='Defense')&df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID','PossessionID']).ngroups

def get_d_points_played(df_in,plyr):
    return df_in[(df_in['Event Type']!='Cessation') & (df_in.Line=='D')&df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID']).ngroups
def get_d_possessions_played(df_in,plyr):
    return df_in[(df_in.Line=='D')&(df_in['Event Type']=='Offense')&df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID','PossessionID']).ngroups
def get_opp_d_possessions_played(df_in,plyr):
    return df_in[(df_in.Line=='D')&(df_in['Event Type']=='Defense')&df_in['Lineup'].str.contains(plyr,na=False)].groupby(['GameID','PointID','PossessionID']).ngroups

def get_players(df_in):
    return df_in['Lineup'].str.split(', ').apply(pd.Series).stack().unique()

def play_stats_by_player(df_in):
    plyrs = get_players(df_in)
    return pd.DataFrame([{'Name': p,
                          'Games Played': get_games_played(df_in,p),
                          'Quarters Played': get_quarters_played(df_in,p),
                          'Points Played': get_points_played(df_in,p),
                          'Possessions Played': get_possessions_played(df_in,p),
                          'Points Played (Offense)': get_o_points_played(df_in,p),
                          'Possessions Played (Offense)': get_o_possessions_played(df_in,p),
                          'Opp Possessions Played (Offense)': get_opp_o_possessions_played(df_in,p),
                          'Points Played (Defense)': get_d_points_played(df_in,p),
                          'Possessions Played (Defense)': get_d_possessions_played(df_in,p),
                          'Opp Possessions Played (Defense)': get_opp_d_possessions_played(df_in,p),
                          'Points Won': get_points_won(df_in,p),
                          'Points Lost': get_points_lost(df_in,p),
                          'Points Won (Offense)': get_o_points_won(df_in,p),
                          'Points Lost (Offense)': get_o_points_lost(df_in,p),
                          'Points Won (Defense)': get_d_points_won(df_in,p),
                          'Points Lost (Defense)': get_d_points_lost(df_in,p),
                         } for p in plyrs])
class Scoober:
    """
    Throw by throw data
    """
    def __init__(self, data_file : str):
        self.data_file = data_file
        self.dataframe = pd.read_csv(data_file, index_col=0)
        self._add_hockey_assist()

    def _add_hockey_assist(self):
        hockey_assist_slice = (self.dataframe.Action.shift(-1)=='Goal')&\
                              (self.dataframe['Action']=='Catch')&\
                              (self.dataframe['Event Type']=='Offense')&\
                              (self.dataframe['Event Type'].shift(-1)=='Offense')
        self.dataframe.loc[hockey_assist_slice,'Action']='HockeyAssist'


    def slice(self, actions=None, event_type=None, line=None, quarter_id=None):
        slice = np.array([True]*len(self.dataframe))
        if actions:
            slice = slice & self.dataframe['Action'].isin(actions)
        if event_type:
            slice = slice & (self.dataframe['Event Type']==event_type)
        if line:
            slice = slice & (self.dataframe['Line']==line)
        if quarter_id:
            slice = slice & (self.dataframe['QuarterID']==quarter_id)
        return slice

    def defense_slice(self, actions=None,line=None, quarter_id=None):
        return self.slice(actions=actions, event_type='Defense',line=line, quarter_id=quarter_id)

    def offense_slice(self, actions=None,line=None, quarter_id=None):
        return self.slice(actions=actions, event_type='Offense',line=line, quarter_id=quarter_id)

    def get_stat(self, df_slice, player_field,stat_name,aggfunc):
        stat = self.dataframe[df_slice].groupby(['Year',player_field,'Teamname']).apply(aggfunc)
        stat = stat.reset_index().rename(columns={player_field:'Name',0:stat_name})
        return stat

    def get_count_stat(self, df_slice, player_field,stat_name):
        return self.get_stat(df_slice, player_field,stat_name,len)

    def get_sum_stat(self, df_slice, player_field,stat_name,sum_stat):
        return self.get_stat(df_slice, player_field,stat_name,lambda x : sum(x[sum_stat]))



class Beau:
    """
    Player by player data
        - Game by game
        - Year by year
        - Career
    """
class Fury:
    """
    Team by team data
        - Game by game
        - Year by year
        - Franchise
    """

class Huddler:
    def __init__(self,data_file):
        self.data_file = data_file
        self.scoober = Scoober(data_file)
        self.dataframe = self.scoober.dataframe
        self._prepare_slices()

    def _prepare_slices(self):
        self.count_stat_list= [
            # Catching
            [self.scoober.offense_slice(actions=['Goal']), 'Receiver','Goals'],
            [self.scoober.offense_slice(actions=['Goal'],line='O'), 'Receiver','Goals (Offense)'],
            [self.scoober.offense_slice(actions=['Goal'],line='D'), 'Receiver','Goals (Defense)'],
            [self.scoober.offense_slice(actions=['Goal','Catch']), 'Receiver','Catches'],
            [self.scoober.offense_slice(actions=['Drop']), 'Receiver','Drops'],
            # Throwing
            [self.scoober.offense_slice(actions=['Goal']), 'Passer','Assists'],
            [self.scoober.offense_slice(actions=['Goal'],line='O'), 'Passer','Assists (Offense)'],
            [self.scoober.offense_slice(actions=['Goal'],line='D'), 'Passer','Assists (Defense)'],
            [self.scoober.offense_slice(actions=['HockeyAssist']),'Passer','Hockey Assists'],
            [self.scoober.offense_slice(actions=['HockeyAssist'],line='O'),'Passer','Hockey Assists (Offense)'],
            [self.scoober.offense_slice(actions=['HockeyAssist'],line='D'),'Passer','Hockey Assists (Defense)'],
            [self.scoober.offense_slice(), 'Passer','Throws'],
            [self.scoober.offense_slice(actions=['Catch','Goal']), 'Passer','Completions'],
            [self.scoober.offense_slice(actions=['Throwaway','Callahan']),'Passer','Throwaways'],
            [self.scoober.offense_slice(actions=['Callahan']), 'Passer','Callahans Thrown'],
            [self.scoober.offense_slice(actions=['Drop']), 'Passer','Throws Dropped'],
            [self.scoober.offense_slice(actions=['Catch','Goal'])&~pd.isnull(self.dataframe['Absolute Distance']), 'Passer',
                'Throws Recorded with Yardage'],
            [self.scoober.offense_slice(actions=['MiscPenalty']),'Passer','Fouls Drawn'],
            [self.scoober.offense_slice(actions=['Stall']),'Passer','Stalls'],
            # Defense
            [self.scoober.defense_slice(actions=['D','Callahan']), 'Defender', 'Blocks'],
            [self.scoober.defense_slice(actions=['D','Callahan'],line='O'), 'Defender', 'Blocks (Offense)'],
            [self.scoober.defense_slice(actions=['D','Callahan'],line='D'), 'Defender', 'Blocks (Defense)'],
            [self.scoober.defense_slice(actions=['Callahan']), 'Defender','Callahans'],
            [self.scoober.defense_slice(actions=['Pull','PullOb']), 'Defender', 'Pulls'],
            [self.scoober.defense_slice(actions=['PullOb']), 'Defender', 'Pulls (Out-of-bounds)'],
            [self.scoober.defense_slice(actions=['Pull','PullOb'])&~pd.isnull(self.dataframe['Absolute Distance']), 'Defender',
                 'Pulls Recorded with Yardage'],
            [self.scoober.defense_slice(actions=['Pull'])&~pd.isnull(self.dataframe['Absolute Distance']), 'Defender',
                 'Pulls (Inbounds) Recorded with Yardage'],

            ]

        self.sum_stat_list = [
            [self.scoober.offense_slice(actions=['Catch','Goal'])&~pd.isnull(self.dataframe['Absolute Distance']),
             'Passer','Throwing Yards','Absolute Distance'],

            [self.scoober.offense_slice(actions=['Catch','Goal'])&~pd.isnull(self.dataframe['Lateral Distance']),
             'Passer','Lateral Throwing Yards','Lateral Distance'],

            [self.scoober.offense_slice(actions=['Catch','Goal'])&~pd.isnull(self.dataframe['Toward Our Goal Distance']),
             'Passer','Forward Throwing Yards','Toward Our Goal Distance'],

            [self.scoober.defense_slice(actions=['Pull','PullOb'])&~pd.isnull(self.dataframe['Absolute Distance']),
             'Defender','Pull Yards','Absolute Distance'],

            [self.scoober.defense_slice(actions=['Pull'])&~pd.isnull(self.dataframe['Absolute Distance']),
             'Defender','Pull Yards (Inbounds)','Absolute Distance']
           ]


    def _add_event_stats(self):
       self.df_stat_list = [self.scoober.get_count_stat(i,j,k) for i,j,k in self.count_stat_list] + \
                           [self.scoober.get_sum_stat(i,j,k,l) for i,j,k,l in self.sum_stat_list]
       stat_list =  [k for i,j,k in self.count_stat_list] + \
                    [k for i,j,k,l in self.sum_stat_list]
       # Filter out stats with no results
       missing_columns =  [ stat for stat_df,stat in zip(self.df_stat_list,stat_list) if len(stat_df)==0 ]
       self.df_stat_list = [ stat_df for stat_df in self.df_stat_list if len(stat_df)>0 ]

       self.stats_out = reduce(lambda  left,right: pd.merge(left,right,on=['Year','Teamname','Name'],
                                                       how='outer'),
                                                       self.df_stat_list).fillna(0)
       for column in missing_columns:
           self.stats_out[column] = np.nan

    def _add_playtime_stats(self):
        self.playtime_stats = self.dataframe.groupby(['Teamname','Year']).apply(play_stats_by_player).reset_index().drop('level_2',axis=1)
        self.stats_out = pd.merge(self.playtime_stats,self.stats_out,on=['Teamname','Year','Name'],how='outer')

    def _add_secondary_stats(self):
        self.secondary_stats = [
                                ['Completion Percentage', lambda x : 100*safe_divide(x.Completions,x.Throws)],
                                ['Catches Per Goals', lambda x : safe_divide(x.Catches,x.Goals)],
                                ['Throws Per Assist', lambda x : safe_divide(x.Throws,x.Assists)],
                                ['Throwaway Percentage', lambda x : safe_divide(x.Throwaways,x.Throws)],
                                ['Drop Percentage', lambda x : safe_divide(x.Drops,(x.Drops + x.Catches))],
                                ['Yards Per Throw', lambda x : safe_divide(x['Throwing Yards'],
                                                                          x['Throws Recorded with Yardage'])],
                                ['Yards Per Pull', lambda x : safe_divide(x['Pull Yards'],
                                                                         x['Pulls Recorded with Yardage'])],
                                ['Yards Per Pull (Inbounds)', lambda x : safe_divide(x['Pull Yards (Inbounds)'],
                                                                                    x['Pulls (Inbounds) Recorded with Yardage'])],
                             ]
        for sec_stat,aggfunc in self.secondary_stats:
            self.stats_out[sec_stat] = self.stats_out.apply(aggfunc,axis=1)

    def huddle(self):
        self._add_event_stats()
        self._add_playtime_stats()
        self._add_secondary_stats()

    def write_player_stats_by_year(self):
        self.stats_out.to_csv('data/processed/IndividualStats.csv',sep=',',index=False)
