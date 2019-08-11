import urllib
import pandas as pd
import numpy as np
import os
from lib import opponents
from lib import utils

class LeaguePuller:
    def __init__(self, league : str):
        self.league = league.lower()
        if self.league not in ['audl','pul']:
            raise ValueError("Requested league not one of ['audl','pul']."+\
                            "\nFor custom league, do not specify `league` argument")
        league_data = f'data/supplemental/{self.league}/'
        self.team_page_links = f'{league_data}/{self.league}_ultianalytics.csv'
        self.username_playername_relation_file = f'{league_data}/{self.league}_username_playername_relation.csv'
        self.update_current = None

    def set_years(self,years : list):
        self.years=years
        self._get_team_links_dataframe()

    def set_current_year(self):
        self.set_years([2019])

    def _get_team_links_dataframe(self):
        df = pd.read_csv(self.team_page_links)
        self.get_team_links_dataframe = df[df.year.isin(self.years)].sort_values(['year','team'])

    def pull(self):
        for i,row in self.get_team_links_dataframe.iterrows():
            team_number = row['url'].split('/')[5]
            year = row['year']
            teamname = row['team']
            print(year,teamname)
            uap = UltiAnalyticsPuller(team_number,
                                      teamname,
                                      year,
                                      f'data/{self.league}',
                                      league=self.league,
                                      username_playername_relation_file=self.username_playername_relation_file)
            uap.pull()

class UltiAnalyticsPuller:
    def __init__(self,
                team_number,
                teamname,
                year,
                output_dir,
                username_playername_relation_file : str = None,
                league=None):
        self.team_number = team_number
        self.url = f'http://www.ultianalytics.com/rest/view/team/{team_number}/stats/export'
        self.teamname=teamname
        self.year=year
        self.output_dir=output_dir
        self.username_playername_relation_file=username_playername_relation_file
        self.league=league
        self.quarters=True if self.league in ['audl','pul'] else False
        self._setup_output()

    def _setup_output(self):
        output_dir_enhanced = f'{self.output_dir}/processed/{self.year}/'
        if not os.path.isdir(output_dir_enhanced):
            os.makedirs(output_dir_enhanced,exist_ok=True)

        output_dir_raw = f'{self.output_dir}/raw/{self.year}/'
        if not os.path.isdir(output_dir_raw):
            os.makedirs(output_dir_raw,exist_ok=True)

        self.raw_export_file = f"{output_dir_raw}/{self.year}_{self.teamname}.csv".replace(' ','')
        self.enhanced_export_file = f"{output_dir_enhanced}/{self.year}_{self.teamname}.csv".replace(' ','')

    def _export_raw_team_data(self):
        urllib.request.urlretrieve(self.url, self.raw_export_file)

    def _format_raw_team_data(self):
         return utils.csv2dataframe(self.raw_export_file)

    def _add_extra_columns(self):
        """Add extra useful columns"""
        self.enhanced_dataframe['Teamname'] = self.teamname
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
                dflist.append( make_game_over_line(self.enhanced_dataframe.iloc[i-1]) )

                previ=i
            dflist.append( self.enhanced_dataframe.iloc[i:] )

            self.enhanced_dataframe = pd.concat(dflist).reset_index(drop=True)

        # Add missing GameOver to last line
        if self.enhanced_dataframe.iloc[-1].Action!='GameOver':
            self.enhanced_dataframe = pd.concat( [self.enhanced_dataframe,
                                                  make_game_over_line(self.enhanced_dataframe.iloc[-1]) ] ).reset_index(drop=True)
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

    def _output_enhanced_data(self):
        self.enhanced_dataframe.to_csv(self.enhanced_export_file,sep=',')

    def pull(self):
        self._export_raw_team_data()
        self.enhanced_dataframe = self._format_raw_team_data()
        self._add_extra_columns()
        self._fix_game_overs()
        self._remove_test_games()
        if self.league:
            self._standardize_opponents()
        self._time_event_sort()
        self._insert_player_names()
        self._add_gameplay_ids(self.quarters)
        self._output_enhanced_data()

    def get_raw_dataframe(self):
        return pd.read_csv(self.raw_export_file)

    def get_enhanced_dataframe(self):
        return pd.read_csv(self.enhanced_export_file)

def make_game_over_line(df_in):
    gameoverline = df_in.copy()
    gameoverline['Action'] = 'GameOver'
    gameoverline['Event Type'] = 'Cessation'
    gameoverline['Passer'] = ''
    gameoverline['Receiver'] = ''
    gameoverline['Defender'] = ''
    gameoverline['Hang Time (secs)'] = np.nan
    gameoverline['Begin Area']              =np.nan
    gameoverline['Begin X']                 =np.nan
    gameoverline['Begin Y']                 =np.nan
    gameoverline['End Area']                =np.nan
    gameoverline['End X']                   =np.nan
    gameoverline['End Y']                   =np.nan
    gameoverline['Distance Unit of Measure']=np.nan
    gameoverline['Absolute Distance']       =np.nan
    gameoverline['Lateral Distance']        =np.nan
    gameoverline['Toward Our Goal Distance']=np.nan
    return gameoverline.to_frame().T
