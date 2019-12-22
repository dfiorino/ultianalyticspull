# Get Handmade data and data paths
import importlib.resources as import_resources
import pandas as pd

def get_audl_teams_dataframe():
    with import_resources.path('ultianalyticspull.data.audl.supplemental', 'audl_teams.csv') as audl_teams:
        return pd.read_csv(audl_teams)


def get_audl_logos_path():
    with import_resources.path('ultianalyticspull.images.audl-logos', '')as images_path:
        return images_path

def get_audl_supplemental_data_path():
    with import_resources.path('ultianalyticspull.data.audl.supplemental', '') as audl_data_path:
        return audl_data_path
        
# def audl_data(years : list = [2014,2015,2016,2017,2018,2019], processed : bool = True):
#     """Get throw-by-throw data for each team. Raw data from Ultianalytics has been processed by AUDL Pull"""
#     file_type = 'processed' if processed else 'raw'
#     file_list = [file for yr in years for file in glob.glob(f'{__this_dir__}/../data/{file_type}/audl/{yr}/*csv')]
#     return pd.concat([pd.read_csv(i) for i in file_list])
#
# def pul_data(years : list = [2019], processed : bool = True):
#     """Get throw-by-throw data for each team. Raw data from Ultianalytics has been processed by PUL Pull"""
#     file_type = 'processed' if processed else 'raw'
#     file_list = [file for yr in years for file in glob.glob(f'{__this_dir__}/../data/{file_type}/pul/{yr}/*csv')]
#     return pd.concat([pd.read_csv(i) for i in file_list])
#
# def get_audl_games():
#     """Get DataFrame of all AUDL games"""
#     return pd.read_csv(f'{__this_dir__}/../data/supplemental/audl/audl_games.csv')
#
# # def get_pul_games():
# #     """Get DataFrame of all PUL games"""
# #     return pd.read_csv(f'{__this_dir__}/../data/supplemental/pul/pul_games.csv')
#
# def get_audl_teams():
#     """Get DataFrame of AUDL Team information."""
#     return pd.read_csv(f'{__this_dir__}/../data/supplemental/audl/audl_teams.csv')
#
# def get_pul_teams():
#     """Get DataFrame of PUL Team information."""
#     return pd.read_csv(f'{__this_dir__}/../data/supplemental/pul/pul_teams.csv')
#
# def get_audl_weekly_rosters():
#     """Get DataFrame of weekly AUDL active rosters."""
#     return pd.read_csv(f'{__this_dir__}/../data/supplemental/audl/audl_weekly_active_rosters.csv')
