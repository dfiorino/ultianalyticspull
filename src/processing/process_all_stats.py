import pandas as pd
from src.processing.utils import load_data, DATA_DIR
from src.processing.stats import calculate_rates, calculate_sum_stats
from src.processing.stats import calculate_gameplay_stats, calculate_gameplay_stats_by_player


# NOTE - the current player functions get prohibitively slow if indexed on game
TEAM_INDEX_VARS = ['year', 'team', 'opponent', 'date', 'game']
PLAYER_INDEX_VARS = ['year', 'team', 'player']


def make_team_indicators(df, index_vars=TEAM_INDEX_VARS):
    """
    High-level function for all team stats
    :param df: raw data
    :param index_vars: list of groupby cols - help define whether to aggregate by game or by year
    :return: pd.DataFrame of all team stats
    """
    df_sum = calculate_sum_stats(df, index_vars, entity='team')

    level_col = f'level_{len(index_vars)}'
    df_gameplay = df.groupby(index_vars).apply(calculate_gameplay_stats).reset_index().drop(columns=level_col)

    df_wide = pd.merge(df_sum, df_gameplay, on=index_vars)
    df_wide = calculate_rates(df_wide)

    return df_wide


def make_player_indicators(df):
    """
    High-level function for all player stats
    :param df: raw data
    :return: pd.DataFrame of all player stats
    """
    df_sum = calculate_sum_stats(df, PLAYER_INDEX_VARS, entity='player')

    index_vars = PLAYER_INDEX_VARS[:-1]  # the aggregation by player happens within calculate_gameplay_stats_by_player
    level_col = f'level_{len(index_vars)}'
    df_gameplay = df.groupby(index_vars).apply(calculate_gameplay_stats_by_player).reset_index().drop(level_col, axis=1)

    df_wide = pd.merge(df_sum, df_gameplay, on=PLAYER_INDEX_VARS, how='outer')
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


if __name__ == '__main__':
    df = load_data()

    df_team = make_team_indicators(df)
    df_team.to_csv(f'{DATA_DIR}/final/team_stats.csv', index=False)

    df_team_eoy = make_team_indicators(df, index_vars=TEAM_INDEX_VARS[:2])
    df_team_eoy.to_csv(f'{DATA_DIR}/final/team_stats_by_year.csv', index=False)

    df_player = make_player_indicators(df)
    df_player.to_csv(f'{DATA_DIR}/final/player_stats.csv', index=False)

    df_goals = clean_goals_for_sanke(df)
    df_goals.to_csv(f'{DATA_DIR}/final/all_goals.csv', index=False)
