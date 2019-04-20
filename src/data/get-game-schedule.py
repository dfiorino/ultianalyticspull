import pandas as pd
import glob
import requests
from bs4 import BeautifulSoup
import os

## Previous Years
df_list = []

for year_id, (year,max_pages) in enumerate([[2018,9],[2017,9],[2016,10],
                                            [2015,10],[2014,7],[2013,6],[2012,4]]):

    for page_num in range(0,max_pages):
        url = f'https://theaudl.com/league/game?page={page_num}&year={year_id+1}'
        result = requests.get(url)

        soup = BeautifulSoup(result.text,'lxml')

        matchup_links = [i.find_all('a')[0].attrs['href'] for i in soup.find_all('td',attrs={'class':"audl-schedule-game-center",'colspan':"3"})]
        start_times_places = [i.text for i in soup.find_all('td',attrs={'class':"audl-schedule-start-time",'colspan':"2"})]

        scores = [i.text for i in soup.find_all('td',attrs={'class':"audl-schedule-team-score"})]
        team_names = [i.text for i in soup.find_all('td',attrs={'class':"audl-schedule-team-name"})]
        score_pairs = [(i,j) for i,j in zip(scores[::2],scores[1::2])]
        team_name_pairs = [(i,j) for i,j in zip(team_names[::2],team_names[1::2])]

        somelist=[{'Year':mul.split('/')[-1].split('-')[0],'Week':'?',
                    'Matchup Link':mul,'Date Location':stp,
                    'Home Team':hm,'Away Team':aw,
                    'Home Team Score':hms,'Away Team Score':aws
                    } for mul,stp,(aws,hms),(aw,hm) in zip(matchup_links, start_times_places,score_pairs,team_name_pairs)]

        df_list.append(pd.DataFrame(somelist))
    

## 2019 / current year
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
         
games = pd.concat([pd.DataFrame(somelist)]+df_list)

# Fill in Week Number
games['Date'] = games['Matchup Link'].apply(lambda x : '/'.join(x.split('/')[3].split('-')[:3]) )
games['Date'] = pd.to_datetime(games['Date'],format='%Y/%m/%d')
games['Week'] = games['Date'].dt.strftime('%W').astype(int)
games['Week'] = games.apply(lambda x : x.Week - games[games.Year==x.Year].Week.min() + 1,axis=1)

games.to_csv('../../data/supplemental/games.csv')

