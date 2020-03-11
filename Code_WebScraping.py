#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 15:52:19 2020
@author: Emilio
"""

import requests
from bs4 import BeautifulSoup
from IPython.core.display import HTML
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import *
from pylab import *
from collections import Counter
import time
import urllib
import re

def Convert(string): 
    return list(string.split(", "))  

def put_icon(path):
    return '<img src="'+ path + '" width="60" >'

def plot_loghist(x, bins):
  hist, bins = np.histogram(x, bins=bins)
  logbins = np.logspace(np.log10(bins[0]),np.log10(bins[-1]),len(bins))
  plt.hist(x, bins=logbins)
  plt.xscale('log')
  
def Make_spreadlist(data):
    Slist = []
    for d in data :
        for dl in d:
            Slist.append(dl)
    return Slist
  
def make_hist(data):
    counts = Counter(data)
    labels, values = zip(*counts.items())
    indexSort = np.argsort(values)[::-1] # sort your values in descending order
    labels = np.array(labels)[indexSort] # rearrange the data
    values = np.array(values)[indexSort]
    indexes = np.arange(len(labels))
    return values, labels, indexes

def make_hist_top(data, low=1):
    values, labels, indexes = make_hist(data)
    histo_top_values=[]
    j=0
    for i in values:
        if i>=low:
            histo_top_values.append(i)
            j+=1
        else:
            break;   
    return histo_top_values, labels[:j], np.arange(len(histo_top_values))


df = pd.DataFrame()
pages = (1, 51, 101, 151, 201)
Name = []
Year = []
Rate = []
posters_links = []
Runtime = []
Genre = []
Bloc_info = []

for k in pages :
    url = f'https://www.imdb.com/search/title/?groups=top_250&sort=user_rating,desc&start={k}&ref_=adv_nxt'
    response = requests.get(url)
    time.sleep(1) #important, if you run to much loops without a friendly delay, the website can fear an hacker attack -> sleep(1)
    html = response.content
    soup = BeautifulSoup(html, 'lxml')
    Name = Name + [i.text for i in soup.select('h3.lister-item-header a')]
    Year = Year + [re.findall("\d{4}", i.text) for i in soup.select('h3.lister-item-header span.lister-item-year')]
    Rate = Rate + [float(i.text) for i in soup.select('div.inline-block strong')]
    Runtime = Runtime + [i.text[:-4] for i in soup.select('p.text-muted span.runtime')]
    Genre = Genre + [i.text.strip() for i in soup.select('p.text-muted span.genre')]
    posters_links = posters_links + [link.get('loadlate') for link in soup.findAll('img')]
    Bloc_info = Bloc_info + [i.text for i in soup.select('div.lister-item-content p')]
    
df['Rank'] = np.arange(1,251,1)
df['Rate'] = Rate
df['Posters'] = posters_links
df['Name'] = Name
df['Year']=[int(Year[i][0]) for i in range (len(Year))]
df['Runtime (min)'] = Runtime
df['Genre'] = [Convert(Genre[i]) for i in range (len (Genre))]
df['Synopsis of the film'] = [i.replace("\n    ","") for i in Bloc_info[1::4]]
df['Director(s)']=[i[i.find(":")+1:i.find("|")].replace("\n","") for i in Bloc_info[2::4]]
df['Actor(s)'] = [Convert(i[i.find("|")+13:-1].replace("\n","")) for i in Bloc_info[2::4]]
df['Bugget (M$)'] = [float(i[i.find("|")+10:-2].replace("\n","").replace(",",".")) for i in Bloc_info[3::4]]  

pd.set_option('display.max_colwidth', -1)
HTML(df.to_html(escape=False, formatters=dict(Posters=put_icon)))

Genre_type = Make_spreadlist(df['Genre'])
Actors_list = Make_spreadlist(df['Actor(s)'])


fig = plt.figure(1, figsize=(10, 12)) 
plt.subplot(321)
plt.hist(df['Rate'], len(df['Rate'].value_counts()), rwidth = 0.75)
plt.xlabel('Rate /10', fontsize=10)
plt.ylabel('Number of movies', fontsize=10)
xlim(0, 10)
plt.title('Rate\'s distribution of the movies', fontsize=12)

plt.subplot(322)
bars = plt.hist(df['Year'], len(df['Year'].value_counts()), rwidth = 0.75)
maximums = [i for i, x in enumerate(bars[0]) if x == max(bars[0])]
plt.xlabel('Released year', fontsize=10)
plt.ylabel('Number of movies', fontsize=10)
plt.title('Year\'s distribution of movie release', fontsize=12)

plt.subplot(323)
plt.scatter(df['Year'], df['Rate'])
plt.xlabel('Released year', fontsize=10)
plt.ylabel('Number of movies', fontsize=10)
plt.title('Rate as a function of the released year', fontsize=12)
ylim(0, 10)

plt.subplot(324)
plt.scatter(df['Bugget (M$)'], df['Rate'])
plt.xlabel('Bugget (M$)', fontsize=10)
plt.ylabel('Movies rate', fontsize=10)
plt.title("Rate as a function of the Bugget", fontsize=12)
ylim(0, 10)
xlim(left=0)

plt.subplot(325)
plt.scatter(df['Year'], df['Bugget (M$)'])
plt.xlabel('Released year', fontsize=10)
plt.ylabel('Bugget (M$)', fontsize=10)
plt.title('Tim evolution of movie\'s bugget ', fontsize=12)
ylim(bottom=0)

plt.subplot(326)
plot_loghist(df['Bugget (M$)'], len(df['Bugget (M$)'].value_counts()))
plt.xlabel('Bugget (M$)', fontsize=10)
plt.ylabel('Number of movies', fontsize=10)
plt.title('Bugget\'s distribution of movie release', fontsize=12)

plt.tight_layout()


plt.figure(2, figsize=(16, 8)) 
values, labels, indexes = make_hist(Genre_type)
plt.bar(indexes, values)
plt.xticks(indexes, labels, rotation=45, ha='right')
plt.xlim(-0.75, len(indexes)-0.25)

plt.figure(3, figsize=(16, 8)) 
values, labels, indexes = make_hist_top(df['Director(s)'], 2)
plt.bar(indexes, values)
plt.xticks(indexes, labels, rotation=45, ha='right')
plt.xlim(-1, len(indexes))

plt.figure(4, figsize=(16, 8)) 
values, labels, indexes = make_hist_top(Actors_list, 3)
plt.bar(indexes, values)
plt.xticks(indexes, labels, rotation=45, ha='right')
plt.xlim(-1, len(indexes))

plt.show()