import urllib
import pandas as pd
import numpy as np
from glob import glob
import argparse
import os
from lib import opponents
from lib import utils

def parse_args():
    """Setup command-line interface"""
    parser = argparse.ArgumentParser(description='Get all available AUDL data with minor enhancements and regularization from UltiAnalytics.')
    parser.add_argument('--years','-y', nargs='+',dest='years', default=list(range(2014,2020)),
                        help='Year(s) to pull')

    parser.add_argument('--league','-L',default='audl',
                       choices=['audl','custom','pul'],
                       help='League of Ultianalytics pull to do.' +\
                            'Custom requires specifying team_page_links and username_playername_relation_file')

    parser.add_argument('--team_page_links','-t',default=None,
                       help='file of page links from analytics')
    parser.add_argument('--username_playername_relation_file','-u',default=None,
                       help='username playername relation')

    parser.add_argument('--updatecurrent', dest='updatecurrent', action='store_true',
                        default=False,
                        help='Only get latest year.')

    args = parser.parse_args()

    # Set team page links and username/playername relation file for AUDL or PUL choice
    if args.league.lower() in ['audl','pul']:
        if not args.team_page_links:
            args.team_page_links = f'data/supplemental/{args.league}/{args.league}_ultianalytics.csv'
        if not args.username_playername_relation_file:
            args.username_playername_relation_file = f'data/supplemental/{args.league}/{args.league}_username_playername_relation.csv'

    return  args

def add_extra_cols(df_in, teamname, year):
    """Add extra useful columns"""
    df_in['Teamname'] = teamname
    df_in['Year'] = year
    df_in = df_in.drop('Tournamemnt',axis=1) # Remove misspelled, useless column

    return df_in

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

def fix_game_overs(df_in):
    """Fix missed and redundant GameOver entries"""

    # Remove double GameOvers: Consecutive Action's can't both be GameOver
    df_in = df_in[ (~df_in.Action.eq(df_in.Action.shift(-1))) | (df_in.Action!='GameOver') ].reset_index(drop=True)

    # Add missing GameOvers: Date/Time changes require GameOver, Get indicies where previous Action should be GameOver but isn't
    idx = df_in[ ~(df_in['Date/Time'].eq(df_in['Date/Time'].shift())) & (df_in.Action.shift()!='GameOver') & (df_in.index>0)].index.values

    if len(idx)>0:
        dflist = []
        previ=0
        #iterate through indicies, create gameover instance using previous row as template, append previous rows then gameover row to a list
        for i in idx:
            dflist.append( df_in.iloc[previ:i] )
            dflist.append( make_game_over_line(df_in.iloc[i-1]) )

            previ=i
        dflist.append( df_in.iloc[i:] )

        df_in = pd.concat(dflist).reset_index(drop=True)

    # Add missing GameOver to last line
    if df_in.iloc[-1].Action!='GameOver':
        df_in = pd.concat( [df_in, make_game_over_line(df_in.iloc[-1]) ] ).reset_index(drop=True)

    return df_in

def remove_test_games(df_in):
    """Remove test games from log"""
    return df_in[~(df_in.Opponent=='Test')]

def time_event_sort(df_in):
    """Sort by Date/Time and orignal index"""
    df_in['OrigIndex'] = df_in.index
    df_in = df_in.sort_values(['Date/Time','OrigIndex'])
    return df_in.drop('OrigIndex',axis=1).reset_index(drop=True)

def insert_player_names(df_in, username_playername_relation_file):
    """Insert player names by replacing usernames,
       given the Year and Teamname"""
    upr = pd.read_csv(username_playername_relation_file,encoding = "ISO-8859-1")
    upr['PlayerName'] = upr['PlayerName'].fillna(upr.Username)

    numbered_player_fields = [f'Player {i}' for i in range(0,28)]
    player_fields = ['Passer', 'Receiver', 'Defender'] + numbered_player_fields

    for p_field in player_fields:
        df_in[p_field] = pd.merge(df_in[['Year','Teamname',p_field]],upr,
                                         left_on=['Year','Teamname',p_field],
                                         right_on=['Year','Teamname','Username'],
                                         how='left')['PlayerName'].fillna(df_in[p_field])


    df_in['Lineup'] = df_in.fillna('').apply( lambda x : ', '.join(sorted([ x[i] for i in numbered_player_fields if x[i] !=''])), axis=1).values

    return df_in

def add_gameplay_ids(df_in):
    """Add IDs for each Game and its Points and Possessions"""
    df_in['GameID'] = pd.factorize(df_in['Date/Time'].astype(str)
                                 +df_in['Opponent'].astype(str))[0] +1

    df_in.loc[df_in.Action=='EndOfFirstQuarter','QuarterID'] = 1
    df_in.loc[df_in.Action=='Halftime','QuarterID'] = 2
    df_in.loc[df_in.Action=='EndOfThirdQuarter','QuarterID'] = 3
    df_in.loc[df_in.Action=='EndOfFourthQuarter','QuarterID'] = 4
    df_in.loc[df_in.Action=='GameOver','QuarterID'] = 4
    ot_games = df_in[df_in.Action.isin(['EndOfFourthQuarter','EndOfOvertime'])].GameID.unique()
    df_in.loc[(df_in.Action=='GameOver')&(df_in.GameID.isin(ot_games)),'QuarterID'] = 5
    df_in['QuarterID'] = df_in.QuarterID.bfill().astype(int)


    point_groups = df_in.groupby(['GameID']).apply(lambda x : pd.factorize( x['Our Score - End of Point'].astype(str)
                                                                             +x['Their Score - End of Point'].astype(str)
                                                                             +x['Line']
                                                                             +x['Point Elapsed Seconds'].astype(str))[0] + 1).values
    df_in['PointID'] =  [j for i in point_groups for j in i]


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

    poss_groups =df_in.groupby(['GameID','PointID']).apply(lambda x : range(1,len(x[x.Action.isin(poss_change_list)])+1 ) )
    df_in.loc[df_in.Action.isin(poss_change_list),'PossessionID']= [j for i in poss_groups for j in i]
    df_in['PossessionID'] = df_in['PossessionID'].bfill()

    return df_in

def main():

    args = parse_args()

    years = [2019] if args.updatecurrent else args.years

    df = pd.read_csv(args.team_page_links).sort_values(['year','team'])
    df = df[df.year.isin(years)]

    for i,row in df.iterrows():

            teamno = row['url'].split('/')[5]
            year = row['year']
            teamname = row['team']

            url = 'http://www.ultianalytics.com/rest/view/team/{}/stats/export'.format(teamno)

            out_dir = f'data/processed/{args.league}/{year}/'
            if not os.path.isdir(out_dir):
                os.mkdir(out_dir)

            out_dir_raw =  f'data/raw/{args.league}/{year}/'
            if not os.path.isdir(out_dir_raw):
                os.mkdir(out_dir_raw)

            outfn = f"{out_dir}/{year}_{teamname}.csv".replace(' ','')
            outfn_raw = f"{out_dir_raw}/{year}_{teamname}.csv".replace(' ','')
            urllib.request.urlretrieve(url, outfn_raw)

            print(year,teamname)
            df_teamdata = utils.csv2dataframe(outfn_raw)
            if len(df_teamdata)>0:
                df_teamdata = add_extra_cols(df_teamdata, teamname, year)
                df_teamdata = fix_game_overs(df_teamdata)
                if len(df_teamdata[~(df_teamdata['Date/Time'].eq(df_teamdata['Date/Time'].shift(-1))) &(df_teamdata.Action!='GameOver')]) > 0:
                    print('Missing GameOvers')
                if len(df_teamdata[ (df_teamdata.Action.eq(df_teamdata.Action.shift())) & (df_teamdata.Action.shift()=='GameOver') ]) > 0:
                    print('Double GameOvers')

                df_teamdata = remove_test_games(df_teamdata)
                df_teamdata = opponents.standardize(df_teamdata,league=args.league)
                df_teamdata = time_event_sort(df_teamdata)
                df_teamdata = insert_player_names(df_teamdata,args.username_playername_relation_file)
                df_teamdata = add_gameplay_ids(df_teamdata)

                df_teamdata.to_csv(outfn,sep=',')
            else:
                print('Skipped')

main()
