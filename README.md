# audl-pull
**Description**

Use *audl-pull* to grab all of the available raw UltiAnalytics data for AUDL seasons 2014 to 2018.

**Usage**

`python audl-pull.py [--updatecurrent]`

That's it! 

The only optional input is the flag `updatecurrent` which will only re-pull the latest season's data. The 2018 season is over though, so there's no need to use it!

**Requirements**
- Python >= 3.0
- Internet connection ;)
- Python libraries: glob,urllib,argparse,pandas
