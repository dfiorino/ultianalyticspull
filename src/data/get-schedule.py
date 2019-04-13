# only works for 2019 :/
import pandas as pd
import glob
import requests
from bs4 import BeautifulSoup
import os

somelist=[]
for week_no in range(1,16):
    
    url = f'https://theaudl.com/league/schedule/week-{week_no}'
    result = requests.get(url)
    
    soup = BeautifulSoup(result.text,'lxml')
    
    matchup_links = [i.find_all('a')[0].attrs['href'] for i in soup.find_all('span',attrs={'class':'audl-schedule-gc-link'})]
    start_times_places = [i.text for i in soup.find_all('span',attrs={'class':'audl-schedule-start-time-text'})]

    scores = [i.text for i in soup.find_all('td',attrs={'class':"audl-schedule-team-score"})]
    team_names = [i.text for i in soup.find_all('td',attrs={'class':"audl-schedule-team-name"})]
    score_pairs = [(i,j) for i,j in zip(scores[::2],scores[1::2])]
    team_name_pairs = [(i,j) for i,j in zip(team_names[::2],team_names[1::2])]

    somelist+=[{'Year':2019,'Week':week_no,
                'Matchup Link':mul,'Date Location':stp,
                'Home Team':hm,'Away Team':aw,
                'Home Team Score':hms,'Away Team Score':aws
                } for mul,stp,(aws,hms),(aw,hm) in zip(matchup_links, start_times_places,score_pairs,team_name_pairs)]
         
audl_sched = pd.DataFrame(somelist)
audl_sched.to_csv('../../data/teams/schedule.csv')
audl_sched