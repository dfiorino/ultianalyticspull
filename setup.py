#!/usr/bin/env python
from setuptools import find_packages, setup

install_requires=[  'argparse',
                    'pandas',
                    'numpy',
                    'bs4',
                    'requests']

setup(
    name='ultianalyticspull',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>3.5.2',
    install_requires=install_requires,
    version='0.4.0',
    description='Tools to pull and process data from the American Ultimate Disc League and Premier Ultimate League',
    author="Dan Fiorino <danielfiorino@gmail.com>, Zane Rankin <zwrankin@gmail.com>",
    license='GPL',
    entry_points={'console_scripts': ['aggregate_stats = ultianalyticspull.src.processing.process_all_stats.py:main',
                                      'get-audl-current-rosters = ultianalyticspull.src.scraping.audlcurrentrosters:get_audl_current_rosters',
                                      'get-audl-game-results = ultianalyticspull.src.scraping.audlgameresults:main',
                                      'get-audl-players = ultianalyticspull.src.scraping.audlrostersfromstatspage:get_audl_rosters_from_stats_page',
                                      'get-audl-logos = ultianalyticspull.src.scraping.audlteamlogos:get_audl_team_logos',
                                      'get-audl-weekly-active-rosters= ultianalyticspull.src.scraping.getaudlweeklyactiverosters:get_audl_weekly_active_rosters',
            ]
        }
)
