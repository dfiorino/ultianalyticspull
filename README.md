# audl-pull

Use *audl-pull* to grab, clean, and enhance all of the available UltiAnalytics data for AUDL seasons 2014 to 2018. It comes with *individual-stats* which will tabulate player stats like goals, assists, blocks, and over 20 others!

**Description**

This project grabs AUDL data from the UltiAnalytics website using a pre-webscraped list of file paths. Data for each team and year are returned separately. Enhancements and regularizations are performed on the raw CSV to make them "analysis ready." The command-line interface allows for the latest year of data to be pulled instead of all years.

**Features**

- Formatted for use with super fast and awesome Python Pandas!
- Auto-matches player names for 97% of the 4,000+ usernames associated with players!
- Fixes to data entry errors (e.g. missing GameOver)!
- Standardized team names!
- Extra columns to distinguish games, quarters, points, and even possessions!
- Individual player stats
- Home/Away ***coming soon***
- Playoff/Regular season ***coming soon***
- Merged game stats ***coming soon***

**Usage**

`python audl-pull.py [--updatecurrent]`

then 

`python individual-stats.py`

That's it! 

The only optional input is the flag `updatecurrent` which will only re-pull the latest season's data. The 2018 season is over though, so there's no need to use it!

**Requirements**
- Python >= 3.0
- Internet connection ;)
- Python libraries: glob,urllib,argparse,pandas,numpy,csv,argparse (pretty standard stuff)
