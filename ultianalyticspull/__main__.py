from ultianalytics.src.core import pullers
from ultianalytics.src.core import huddlers
from ultianalytics.src.processing.pull import pull

import argparse

def get_current_year():
    current_year = 2019
    return current_year

def parse_args():
    """Setup command-line interface"""
    description = 'Get and enhance data from UltiAnalytics for individual teams ' +\
                  'or the entire professional leagues (AUDL and PUL)'
    parser = argparse.ArgumentParser(description=description)

    # Arguments for league pull
    parser.add_argument('--league','-L',default=None,
                       choices=['audl','pul'],
                       help="League of Ultianalytics pull to do." +\
                            "Custom requires specifying UltiAnalytics team " +\
                            "number and username_playername_relation_file")
    parser.add_argument('--years','-y', nargs='+',dest='years',
                        default=range(2014,get_current_year()+1),
                        help='Year(s) to pull')
    parser.add_argument('--updatecurrent', dest='update_current', action='store_true',
                        default=False,
                        help='Only get latest year.')

    # Arguments for a single team pull
    parser.add_argument('--team_number','-n',default=None,
                       help='ultianalytics team number. can be found on ultianalytics page')
    parser.add_argument('--team_name','-t',default=None,
                       help='Team name')
    parser.add_argument('--username_playername_relation_file','-u',default=None,
                       help='username playername relation')

    args = parser.parse_args()

    if args.league:
        if args.league.lower() not in ['audl','pul']:
            raise ValueError('Undefined league. Choose from [AUDL, PUL]')
    else:
        if not args.team_number:
            raise ValueError('Team number must be defined for custom team pulls.')
        if not args.team_name:
            raise ValueError('Team name must be defined for custom team pulls.')

    return  args

if __name__ == '__main__':
    args = parse_args()
    # password=None
    # if args.team_number:
        # password = input('If team account is private,\nEnter password:')
    pull(team_number = args.team_number,
        team_name = args.team_name,
        # team_password = args.team_password,
        league = args.league,
        years= args.years,
        update_current = args.update_current,
        username_playername_relation_file = args.username_playername_relation_file )
