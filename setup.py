#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='ultianalyticspull',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>3.5.2',
    version='0.3.0',
    description='Tools to pull and process data from the American Ultimate Disc League and Premier Ultimate League',
    author="Dan Fiorino <danielfiorino@gmail.com>, Zane Rankin <zwrankin@gmail.com>",
    license='GPL',
    entry_points={'console_scripts': [
                'aggregate_stats = src.processing.process_all_stats.py:main']
                }
)
