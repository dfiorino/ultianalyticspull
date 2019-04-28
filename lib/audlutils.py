import pandas as pd
import glob
import csv
import os

__this_dir__ = os.path.basename(os.path.realpath(__file__))

def CSV2DataFrame(filename):
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


def AUDLData(years= [2014,2015,2016,2017,2018,2019] ):
    
    file_list = [file for yr in years for file in glob.glob(f'{__this_dir__}/../data/processed/{yr}/*csv')]
    return pd.concat([pd.read_csv(i) for i in file_list])