#!/usr/bin/env python
from setuptools import find_packages, setup

install_requires=[  'argparse',
                    'pandas',
                    'numpy',
                    'bs4',
                    'requests']

setup(
    name='ultianalyticspull',
    version='0.4.0',

    description='Tools to pull and process data from the American Ultimate Disc League and Premier Ultimate League',
    author="Dan Fiorino <danielfiorino@gmail.com>, Zane Rankin <zwrankin@gmail.com>",
    license='GPL',

    python_requires='>3.5.2',
    install_requires=install_requires,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,

    entry_points={'console_scripts': ['aggregate_stats = ultianalyticspull.src.processing.process_all_stats.py:main',
                                      'output-scraped-data = ultianalyticspull.src.scraping.out:output_scraped_data',
                                      ]
        }
)
