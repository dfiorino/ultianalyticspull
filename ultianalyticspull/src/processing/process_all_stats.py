import pandas as pd
from ultianalyticspull.src.processing.utils import load_data, get_default_data_directory
from ultianalyticspull.src.processing.stats import calculate_rates, calculate_sum_stats
from ultianalyticspull.src.processing.stats import calculate_gameplay_stats, calculate_gameplay_stats_by_player


def get_team_index_vars(by_game:bool=False):
    """
    Return the index variables needed to summarize each team.
    Default behavior is every year. Optional flag sums by game.
    :param by_game: define whether to aggregate by game or by year
    :return: list of index variables
    """
    if by_game:
        return ['year', 'team', 'opponent', 'date', 'game']
    return ['year', 'team']

def get_player_index_vars(by_game:bool=False):
    """
    Return the index variables needed to summarize each player.
    Default behavior is every year. Optional flag sums by game.
    NOTE - the current player functions get prohibitively slow if indexed on game
    :param by_game: define whether to aggregate by game or by year
    :return: list of index variables
    """
    if by_game:
        print('NOTE - the current player functions get prohibitively slow if indexed on game')
        return ['year', 'team', 'player', 'opponent', 'date', 'game']
    return ['year', 'team', 'player']

def make_team_indicators(df, by_game:bool=False):
    """
    High-level function for all team stats
    :param df: raw data
    :param by_game: define whether to aggregate by game or by year
    :return: pd.DataFrame of all team stats
    """
    index_vars = get_team_index_vars(by_game=by_game)

    df_sum = calculate_sum_stats(df, index_vars, entity='team')

    level_col = f'level_{len(index_vars)}'
    df_gameplay = df.groupby(index_vars).apply(calculate_gameplay_stats).reset_index().drop(columns=level_col)

    df_wide = pd.merge(df_sum, df_gameplay, on=index_vars)
    df_wide = calculate_rates(df_wide)

    return df_wide


def make_player_indicators(df, by_game=False):
    """
    High-level function for all player stats
    :param df: raw data
    :param by_game: define whether to aggregate by game or by year
    :return: pd.DataFrame of all player stats
    """
    index_vars = get_player_index_vars(by_game=by_game)

    df_sum = calculate_sum_stats(df, index_vars, entity='player')

    # Note, the aggregation by player happens within calculate_gameplay_stats_by_player
    level_col = f'level_{len(index_vars)-1}'
    gameplay_index_vars = [idx for idx in index_vars if idx != 'player']
    df_gameplay = df.groupby(gameplay_index_vars).apply(calculate_gameplay_stats_by_player).reset_index().drop(level_col, axis=1)

    df_wide = pd.merge(df_sum, df_gameplay, on=index_vars, how='outer')
    df_wide = calculate_rates(df_wide)

    return df_wide


def clean_goals_for_sanke(df):
    """
    Format goal data for Sankey plot
    :param df: raw data
    :return: pd.DataFrame of goals
    """
    cols = ['team', 'year', 'Passer', 'Receiver', 'Line']
    df = df.loc[(df.Action == "Goal") & (df['Event Type'] == 'Offense')][cols].dropna(how='any')
    return df

def main(data_dir = get_default_data_directory()):
        df = load_data()

        print('Generating Team By Game Stats...')
        out_file_team = f'{data_dir}/final/audl/team_stats.csv'
        df_team = make_team_indicators(df,by_game=True)
        df_team.to_csv(out_file_team, index=False)
        print(f'\twrote {out_file_team}')

        print('Generating Team By Year Stats...')
        out_file_team_by_year = f'{data_dir}/final/audl/team_stats_by_year.csv'
        df_team_eoy = make_team_indicators(df)
        df_team_eoy.to_csv(out_file_team_by_year, index=False)
        print(f'\twrote {out_file_team_by_year}')

        print('Generating Player By Year Stats...')
        out_file_player = f'{data_dir}/final/audl/player_stats.csv'
        df_player = make_player_indicators(df)
        df_player.to_csv(out_file_player, index=False)
        print(f'\twrote {out_file_player}')

        print('Generating Goals File for Sankey...')
        out_file_goals = f'{data_dir}/final/audl/all_goals.csv'
        df_goals = clean_goals_for_sanke(df)
        df_goals.to_csv(out_file_goals, index=False)
        print(f'\twrote {out_file_goals}')

if __name__ == '__main__':
    main()
