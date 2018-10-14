import urllib
import pandas as pd
from glob import glob
import argparse
import csv

def ParseArgs():
    """Setup command-line interface"""
    parser = argparse.ArgumentParser(description='Get all available AUDL data with minor enhancements and regularization from UltiAnalytics.')
    parser.add_argument('--updatecurrent', dest='updatecurrent', action='store_true',
                        default=False,
                        help='Only get latest year.')
    return  parser.parse_args()

def CSV2DataFrame(filename):
    """Read CSV but deal with inconsistent use of commas in CSV"""
    teamlog = []
    with open(filename, 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='|')
        header = next(reader)
        teamlog = list(reader)
    # Deal with sticky situation of rows with more or less CSV's than the header
    ncols = len(header)
    teamlog = [e[:ncols] if len(e) > ncols else e+['']*(ncols-len(e)) for e in teamlog]


    return pd.DataFrame(teamlog,columns=header)

def main():

    args = ParseArgs()
    
    allfiles = sorted(glob('data/teams*.csv'))
    filestoget = allfiles if not args.updatecurrent else [allfiles[-1]]
    
    for f in filestoget:
        
        df_filepaths =pd.read_csv(f).sort_values(['year','teams'])
        
        for i,row in df_filepaths.iterrows():
            
            teamno = row['teams-href'].split("/")[5]
            year = row['year']
            teamname = row['teams']
            print(year,teamname)
          
            url = 'http://www.ultianalytics.com/rest/view/team/{}/stats/export'.format(teamno)
            outfn = "output/{}_{}.csv".format(year,teamname).replace(' ','')
            urllib.request.urlretrieve(url, outfn)
            
            df_teamdata = CSV2DataFrame(outfn)
            df_teamdata['Teamname'] = teamname
            df_teamdata['Tournament'] = year
            df_teamdata= df_teamdata.drop('Tournamemnt',axis=1)
            df_teamdata[df_teamdata.columns].to_csv(outfn,sep=',')
main()

