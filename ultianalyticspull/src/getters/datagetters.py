# Get Handmade data and data paths
import importlib.resources as import_resources
import pandas as pd

def get_audl_teams_dataframe():
    with import_resources.path('ultianalyticspull.data.audl', 'audl_teams.csv') as audl_teams:
        return pd.read_csv(audl_teams)


def get_audl_logos_path():
    with import_resources.path('ultianalyticspull.images.audl-logos', '')as images_path:
        return images_path

def get_audl_data_path():
    with import_resources.path('ultianalyticspull.data.audl', '') as audl_data_path:
        return audl_data_path
