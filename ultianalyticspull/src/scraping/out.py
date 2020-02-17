import ultianalyticspull.src.getters.datagetters as getters
import ultianalyticspull.src.scraping.scrape as scrape
import urllib.request

def output_audl_weekly_active_rosters():
    # Get Data/Paths
    audl_data_path = getters.get_audl_logos_path()
    audl_active = scrape.get_audl_weekly_active_rosters()
    # Output
    output_csv = f'{audl_data_path}/audl_weekly_active_rosters.csv'
    audl_active.to_csv(output_csv)
    print(f"\tWrote {output_csv}")

def output_audl_rosters_from_stats_page(page_start = 0,
                                        page_max = 116):
    # Get Data/Paths
    audl_data_path = getters.get_audl_data_path()
    audlstats_players = scrape.get_audl_rosters_from_stats_page(page_start = page_start,
                                                                page_max = page_max)
    # Output
    output_csv = f"{audl_data_path}/audl_players_from_stats_page.csv"
    audlstats_players.to_csv(output_csv)
    print(f"\tWrote {output_csv}")

def output_audl_game_results(years=[2012,2013,2014,2015,2016,2017,2018,2019]):
    # Get Data/Paths
    audl_data_path = getters.get_audl_data_path()
    games = scrape.get_audl_game_results(years=years)
    # Output
    output_csv = f"{audl_data_path}/audl_games.csv"
    games.sort_values('Date').reset_index(drop=True).to_csv(output_csv)
    print(f"\tWrote {output_csv}")

def output_audl_current_rosters():

    # Get Data/Paths
    audl_data_path = getters.get_audl_data_path()
    audldotcom_rosters = scrape.get_audl_current_rosters()
    # Output
    output_csv = f"{audl_data_path}/2019_rosters.csv"
    audldotcom_rosters.to_csv(output_csv)
    print(f"\tWrote {output_csv}")

def output_audl_team_logos():
    # Get Data/Paths
    audl_data_path = getters.get_audl_logos_path()
    teams_df = getters.get_audl_teams_dataframe()

    # Output PNGs
    for abbr in teams_df[teams_df['Active']]['Team Abv']:
        url = f'https://theaudl.com/sites/default/files/logo-team-{abbr}.png'
        output_png = f'{audl_data_path}/logo-team-{abbr}.png'
        urllib.request.urlretrieve(url,output_png)
        print(f"\tWrote {output_png}")

def output_scraped_data(include_rosters_from_stats_page=False):
    print('Getting AUDL weekly active rosters')
    output_audl_weekly_active_rosters()
    if include_rosters_from_stats_page:
        # This takes a long time
        print('Getting AUDL historical rosters from stats page')
        print('May take ~30 minutes')
        output_audl_rosters_from_stats_page()
    print('Getting AUDL game results')
    output_audl_game_results()
    print('Getting AUDL current rosters')
    output_audl_current_rosters()
    print('Getting AUDL logos')
    output_audl_team_logos()
