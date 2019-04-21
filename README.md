# AUDL Pull <img align="right" width="100" height="100" src="images/logo.png">

Use *AUDL Pull* to grab, clean, and enhance all of the available UltiAnalytics data for AUDL seasons 2014 to 2019. It comes with *individual-stats* which will tabulate player stats like goals, assists, blocks, and over 20 others!

## Description

This project grabs AUDL data from the UltiAnalytics website using a pre-webscraped list of file paths. Data for each team and year are returned separately. Enhancements and regularizations are performed on the raw CSV to make them "analysis ready." The command-line interface allows for the latest year of data to be pulled instead of all years.

## Features

- Formatted for use with super fast and awesome Python Pandas!
- Auto-matched player names for over 4,000 usernames!
- Fixes to data entry errors!
- Standardized team names!
- Extra columns to distinguish games, quarters, points, and even possessions!
- Individual player stats!
- All Game Scores Ever Played!
- All AUDL Team info and logos!
- Grab Current Rosters!
- Grab Reported Active Rosters!
- Playoff/Regular season ***coming soon***
- Merged game stats ***coming soon***

## Usage

```bash
python audlpull.py
```

then 

```bash
python individualstats.py
```

That's it! 

## Requirements
- Python >= 3.0
- Internet connection ;)
- Python libraries: glob,urllib,argparse,pandas,numpy,csv (pretty standard stuff)

## Credit

Doing something cool with *AUDL Pull*? Let me know!

