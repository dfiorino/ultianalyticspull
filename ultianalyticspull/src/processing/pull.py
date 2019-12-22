import ultianalyticspull.src.core.pullers as pullers
import ultianalyticspull.src.core.huddlers as huddlers

def pull(team_number : int = None,
         team_name : str = None,
         team_password : str = None,
         league : str = None,
         years : list = range(2014,get_current_year()+1),
         update_current : bool = False,
         username_playername_relation_file : str = None):
    """
    Single function to trigger an ultianalyticspull of a whole league
    or single team. Single team has the option to enter a team_password
    TODO: should this be two separate functions?
    """

    years = [current_year] if update_current else years

    if league:
        league_puller = pullers.LeaguePuller(league)
        league_puller.set_years(years)
        league_puller.pull()
    else:
        custom_puller = pullers.UltiAnalyticsPuller(team_number=team_number,
                                                   team_name=team_name,
                                                   # team_password=team_password,
                                                   year=years[-1],
                                                   output_dir = 'data/custom',
                                                   username_playername_relation_file = username_playername_relation_file)
        custom_puller.pull()
