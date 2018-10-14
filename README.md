# audl-pull

Use *audl-pull* to grab all of the available UltiAnalytics data for AUDL seasons 2014 to 2018. 

**Description**

This project gets the AUDL data from a pre-webscraped list of file paths. It then returns data for each team and year separately. The data have minor enhancements and regularization of columns from the raw CSV provided by UltiAnalytics. The command-line interface allows for the latest year of data to be pulled instead of all years.

**Usage**

`python audl-pull.py [--updatecurrent]`

That's it! 

The only optional input is the flag `updatecurrent` which will only re-pull the latest season's data. The 2018 season is over though, so there's no need to use it!

**Requirements**
- Python >= 3.0
- Internet connection ;)
- Python libraries: glob,urllib,argparse,pandas
