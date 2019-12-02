import urllib
import pandas as pd
import numpy as np
import os
import importlib.resources as import_resources
import ultianalyticspull.src.core.opponents as opponents
import ultianalyticspull.src.core.utils as utils

def get_leagues():
    return ['audl','pul']

class LeaguePuller:
    def __init__(self,
                league : str,
                years : list):
        self.league = league.lower()
        self._check_league()
        self._get_league_data()
        self.years=years
        self._get_team_links_dataframe()

    def _check_league(self):
        leagues_list = get_leagues()
        if self.league not in leagues_list:
            raise ValueError(f"Requested league not one of {leagues_list}."+\
                            "\nFor custom league, do not specify `league` argument")

    def _get_league_data(self):
        league_data = f'ultianalyticspull.data.{self.league}.supplemental'
        self.team_page_links = import_resources.path(league_data, f'{self.league}_ultianalytics.csv')
        self.username_playername_relation = import_resources.path(league_data, f'{self.league}_username_playername_relation.csv')
        with self.username_playername_relation as username_playername_relation_file:
            self.username_playername_relation_file = username_playername_relation_file

    def _get_team_links_dataframe(self):
        with self.team_page_links as path_team_page_links:
            df = pd.read_csv(path_team_page_links)
            self.team_links_dataframe = df[df.year.isin(self.years)].sort_values(['year','team'])

    def pull(self):

        for i,row in self.team_links_dataframe.iterrows():

            team_number = row['url'].split('/')[5]
            year = row['year']
            team_name = row['team']
            print(year,team_name)

            output_dir = f'{self.league}/{year}/'
            if not os.path.isdir(output_dir):
                os.makedirs(output_dir,exist_ok=True)

            uap = UltiAnalyticsPuller(team_number=team_number,
                                      team_name=team_name,
                                      year=year,
                                      output_dir=output_dir,
                                      league=self.league,
                                      username_playername_relation_file=self.username_playername_relation_file)
            uap.pull()

class UltiAnalyticsPuller:
    def __init__(self,
                team_number,
                team_name,
                year,
                output_dir,
                username_playername_relation_file : str = None,
                league=None,
                team_password=None):
        self.team_number = team_number
        self.url = f'http://www.ultianalytics.com/rest/view/team/{team_number}/stats/export'
        self.team_name=team_name
        self.year=year
        self.output_dir=output_dir
        self.username_playername_relation_file=username_playername_relation_file
        self.league=league
        self.team_password=team_password
        self._setup_output()

    def _setup_output(self):
        output_dir = f'{self.output_dir}/{self.year}/'
        if not os.path.isdir(output_dir):
            os.makedirs(output_dir,exist_ok=True)

        self.enhanced_export_file = f"{output_dir}/{self.year}_{self.team_name}.csv".replace(' ','')

    def _get_raw_team_data(self):
        self.enhanced_dataframe  = utils.team_dataframe(self.team_number,
                                                       self.team_password)

    def _add_extra_columns(self):
        """Add extra useful columns"""
        self.enhanced_dataframe['Teamname'] = self.team_name
        self.enhanced_dataframe['Year'] = self.year
        self.enhanced_dataframe['Tournament'] = self.enhanced_dataframe['Tournamemnt']
        self.enhanced_dataframe = self.enhanced_dataframe.drop('Tournamemnt',axis=1)

    def _fix_game_overs(self):
        """Fix missed and redundant GameOver entries"""
        # Remove double GameOvers: Consecutive Action's can't both be GameOver
        self.enhanced_dataframe = self.enhanced_dataframe[ (~self.enhanced_dataframe.Action.eq(self.enhanced_dataframe.Action.shift(-1))) | (self.enhanced_dataframe.Action!='GameOver') ].reset_index(drop=True)

        # Add missing GameOvers: Date/Time changes require GameOver, Get indicies where previous Action should be GameOver but isn't
        idx = self.enhanced_dataframe[ ~(self.enhanced_dataframe['Date/Time'].eq(self.enhanced_dataframe['Date/Time'].shift())) & (self.enhanced_dataframe.Action.shift()!='GameOver') & (self.enhanced_dataframe.index>0)].index.values

        if len(idx)>0:
            dflist = []
            previ=0
            #iterate through indicies, create gameover instance using previous row as template, append previous rows then gameover row to a list
            for i in idx:
                dflist.append( self.enhanced_dataframe.iloc[previ:i] )
                dflist.append( utils.make_game_over_line(self.enhanced_dataframe.iloc[i-1]) )

                previ=i
            dflist.append( self.enhanced_dataframe.iloc[i:] )

            self.enhanced_dataframe = pd.concat(dflist).reset_index(drop=True)

        # Add missing GameOver to last line
        if self.enhanced_dataframe.iloc[-1].Action!='GameOver':
            self.enhanced_dataframe = pd.concat( [self.enhanced_dataframe,
                                                  utils.make_game_over_line(self.enhanced_dataframe.iloc[-1]) ] ).reset_index(drop=True)
        self._check_game_overs()

    def _check_game_overs(self):
        if len(self.enhanced_dataframe[~(self.enhanced_dataframe['Date/Time'].eq(self.enhanced_dataframe['Date/Time'].shift(-1))) &(self.enhanced_dataframe.Action!='GameOver')]) > 0:
            print('Missing GameOvers')
        if len(self.enhanced_dataframe[ (self.enhanced_dataframe.Action.eq(self.enhanced_dataframe.Action.shift())) & (self.enhanced_dataframe.Action.shift()=='GameOver') ]) > 0:
            print('Double GameOvers')

    def _remove_test_games(self):
        """Remove test games from log"""
        self.enhanced_dataframe = self.enhanced_dataframe[~(self.enhanced_dataframe.Opponent=='Test')]

    def _standardize_opponents(self):
        self.enhanced_dataframe = opponents.standardize(self.enhanced_dataframe,league=self.league)

    def _time_event_sort(self):
        """Sort by Date/Time and orignal index"""
        self.enhanced_dataframe['OrigIndex'] = self.enhanced_dataframe.index
        self.enhanced_dataframe = self.enhanced_dataframe.sort_values(['Date/Time','OrigIndex'])
        self.enhanced_dataframe = self.enhanced_dataframe.drop('OrigIndex',axis=1).reset_index(drop=True)

    def _insert_player_names(self):
        """
        Insert player names by replacing usernames, given the Year and Teamname
        """
        numbered_player_fields = [f'Player {i}' for i in range(0,28)]
        player_fields = ['Passer', 'Receiver', 'Defender'] + numbered_player_fields

        if self.username_playername_relation_file:
            upr = pd.read_csv(self.username_playername_relation_file,
                              encoding = "ISO-8859-1")
            upr['PlayerName'] = upr['PlayerName'].fillna(upr.Username)

            for p_field in player_fields:
                self.enhanced_dataframe[p_field] = pd.merge(self.enhanced_dataframe[['Year','Teamname',p_field]],upr,
                                                 left_on=['Year','Teamname',p_field],
                                                 right_on=['Year','Teamname','Username'],
                                                 how='left')['PlayerName'].fillna(self.enhanced_dataframe[p_field])

        self.enhanced_dataframe['Lineup'] = self.enhanced_dataframe.fillna('').apply( lambda x : ', '.join(sorted([ x[i] for i in numbered_player_fields if x[i] !=''])), axis=1).values

    def _add_gameplay_ids(self, quarters=True):
        """Add IDs for each Game and its Points and Possessions"""
        self.enhanced_dataframe['GameID'] = pd.factorize(self.enhanced_dataframe['Date/Time'].astype(str)
                                     +self.enhanced_dataframe['Opponent'].astype(str))[0] +1

        if quarters:
            self.enhanced_dataframe.loc[self.enhanced_dataframe.Action=='EndOfFirstQuarter','QuarterID'] = 1
            self.enhanced_dataframe.loc[self.enhanced_dataframe.Action=='Halftime','QuarterID'] = 2
            self.enhanced_dataframe.loc[self.enhanced_dataframe.Action=='EndOfThirdQuarter','QuarterID'] = 3
            self.enhanced_dataframe.loc[self.enhanced_dataframe.Action=='EndOfFourthQuarter','QuarterID'] = 4
            self.enhanced_dataframe.loc[self.enhanced_dataframe.Action=='GameOver','QuarterID'] = 4
            ot_games = self.enhanced_dataframe[self.enhanced_dataframe.Action.isin(['EndOfFourthQuarter','EndOfOvertime'])].GameID.unique()
            self.enhanced_dataframe.loc[(self.enhanced_dataframe.Action=='GameOver')&(self.enhanced_dataframe.GameID.isin(ot_games)),'QuarterID'] = 5
            self.enhanced_dataframe['QuarterID'] = self.enhanced_dataframe.QuarterID.bfill().astype(int)
        else:
            self.enhanced_dataframe['QuarterID'] = np.nan


        point_groups = self.enhanced_dataframe.groupby(['GameID']).apply(lambda x : pd.factorize( x['Our Score - End of Point'].astype(str)
                                                                                 +x['Their Score - End of Point'].astype(str)
                                                                                 +x['Line']
                                                                                 +x['Point Elapsed Seconds'].astype(str))[0] + 1).values
        self.enhanced_dataframe['PointID'] =  [j for i in point_groups for j in i]


        poss_change_list=['Goal',
                            'Throwaway',
                            'D',
                            'Drop',
                            'EndOfThirdQuarter',
                            'GameOver',
                            'EndOfFirstQuarter',
                            'Halftime',
                            'Stall',
                            'Callahan',
                            'EndOfFourthQuarter',
                            'EndOfOvertime']

        poss_groups =self.enhanced_dataframe.groupby(['GameID','PointID']).apply(lambda x : range(1,len(x[x.Action.isin(poss_change_list)])+1 ) )
        self.enhanced_dataframe.loc[self.enhanced_dataframe.Action.isin(poss_change_list),'PossessionID']= [j for i in poss_groups for j in i]
        self.enhanced_dataframe['PossessionID'] = self.enhanced_dataframe['PossessionID'].bfill()

    def _add_hockey_assist(self):
        hockey_assist_slice = (self.enhanced_dataframe.Action.shift(-1)=='Goal')&\
                              (self.enhanced_dataframe['Action']=='Catch')&\
                              (self.enhanced_dataframe['Event Type']=='Offense')&\
                              (self.enhanced_dataframe['Event Type'].shift(-1)=='Offense')
        self.enhanced_dataframe.loc[hockey_assist_slice,'Action']='HockeyAssist'

    def _output_enhanced_data(self):
        self.enhanced_dataframe.to_csv(self.enhanced_export_file,sep=',')

    def pull(self):
        self._get_raw_team_data()
        self._add_extra_columns()
        self._fix_game_overs()
        self._remove_test_games()
        if self.league:
            self._standardize_opponents()
        self._time_event_sort()
        self._insert_player_names()
        quarters = True if self.league in ['audl','pul'] else False
        self._add_gameplay_ids(quarters)
        self._add_hockey_assist()
        self._output_enhanced_data()
