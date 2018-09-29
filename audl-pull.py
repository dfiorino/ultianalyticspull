import urllib
import pandas as pd
from glob import glob
import argparse


def ParseArgs():
    parser = argparse.ArgumentParser(description='Get all available AUDL data in its rawest form from UltiAnalytics.')
    parser.add_argument('--updatecurrent', dest='updatecurrent', action='store_true',
                        default=False,
                        help='Only get latest year.')
    return  parser.parse_args()

def main():

    args = ParseArgs()
    allfiles = sorted(glob('data/teams*.csv'))
    filestoget = allfiles if not args.updatecurrent else [allfiles[-1]]
    for f in filestoget:
        df=pd.read_csv(f).sort_values(['year','teams'])
        for i,row in df.iterrows():
            teamno = row['teams-href'].split("/")[5]
            year = row['year']
            teamname = row['teams']
            url = 'http://www.ultianalytics.com/rest/view/team/{}/stats/export'.format(teamno)
            outfn = "output/{}_{}.csv".format(year,teamname).replace(' ','')
            print(year,teamname)
            urllib.request.urlretrieve(url, outfn)
main()

