import pandas as pd
import numpy as np
import glob
import csv

def csv2dataframe(filename : str):
    """Read CSV as Pandas DataFrame but deal with inconsistent use of commas in CSV"""
    teamlog = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        header = next(reader)
        teamlog = list(reader)
    # Deal with sticky situation of rows with more or less CSV's than the header
    ncols = len(header)
    teamlog = [e[:ncols] if len(e) > ncols else e+['']*(ncols-len(e)) for e in teamlog]

    return pd.DataFrame(teamlog,columns=header)

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
