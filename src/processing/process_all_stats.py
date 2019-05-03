import pandas as pd
from src.processing.utils import load_data, team_index_vars, player_index_vars, DATA_DIR
from src.processing.stats import calculate_conversion_rates, calculate_sum_stats
from src.processing.stats import calculate_gameplay_stats, calculate_gameplay_stats_by_player

team_count_indicators = ['Goals', 'Goals Against', 'Blocks', 'Drops', 'Throwaways', 'Turnovers']


def make_team_indicators(df, index_vars=team_index_vars):
    df_counts = calculate_sum_stats(df, index_vars, entity='team')

    # Non row-wise indicators
    level_col = f'level_{len(index_vars)}'
    df_gameplay = df.groupby(index_vars).apply(calculate_gameplay_stats).reset_index().drop(columns=level_col)

    df_wide = pd.merge(df_counts, df_gameplay, on=index_vars)
    df_wide = calculate_conversion_rates(df_wide)

    return df_wide


# TODO - clean up all lists of stat names
PLAYER_SUM_INDICATORS = ['Completions', 'Assists', 'Hockey Assists', 'Throwaways', 'Receptions', 'Goals', 'Drops',
                         'Blocks', 'Callahans', 'Stalls', 'Callahans thrown']


def make_player_indicators(df):
    df_counts = calculate_sum_stats(df, player_index_vars, entity='player')

    # Non row-wise indicators
    df_gameplay = df.groupby(player_index_vars[:-1]).apply(calculate_gameplay_stats_by_player).reset_index().drop(
        'level_2', axis=1)

    df_wide = pd.merge(df_counts, df_gameplay, on=player_index_vars, how='outer')
    df_wide = calculate_conversion_rates(df_wide)

    return df_wide


def clean_goals_for_sanke(df):
    cols = ['team', 'year', 'Passer', 'Receiver', 'Line']
    df = df.loc[(df.Action == "Goal") & (df['Event Type'] == 'Offense')][cols].dropna(how='any')
    return df


if __name__ == '__main__':
    df = load_data()

    df_team = make_team_indicators(df)
    df_team.to_csv(f'{DATA_DIR}/final/team_stats.csv', index=False)

    df_team_eoy = make_team_indicators(df, index_vars=team_index_vars[:2])
    df_team_eoy.to_csv(f'{DATA_DIR}/final/team_stats_by_year.csv', index=False)

    df_player = make_player_indicators(df)
    df_player.to_csv(f'{DATA_DIR}/final/player_stats.csv', index=False)

    df_goals = clean_goals_for_sanke(df)
    df_goals.to_csv(f'{DATA_DIR}/final/all_goals.csv', index=False)
