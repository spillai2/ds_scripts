# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 20:41:52 2017

Parse US baby names data using pandas

@author: san
"""
import pandas as pd
import numpy as np

# read in file with data from 1880
columns = ['name','sex','births']
names1880 = pd.read_csv('/home/san/python/data_analysis/pydata/ch02/names/yob1880.txt', names=columns)

# number of male/female births
names1880.groupby('sex')['births'].sum()

# assemble all the data from 1880-2010 into a single dataframe
years = range(1880,2011)

pieces = []
for year in years:
    path = '/home/san/python/data_analysis/pydata/ch02/names/yob%d.txt' % year
    frame = pd.read_csv(path, names=columns)
    frame['year'] = year
    pieces.append(frame)
    
# concatenate all into one df
names = pd.concat(pieces, ignore_index=True)

# total births by gender
total_births = names.pivot_table('births', index='year', columns='sex', aggfunc=sum)
total_births.plot(title='Total births by year and sex')

# what fraction of babies were given a certain name each year
# function to do the calculation
def add_prop(group):
    births = group.births.astype(float)
    group['prop'] = births / births.sum()
    return group
# call the function after grouping
# after groupby a custom function can be called 
names = names.groupby(['year','sex']).apply(add_prop)
# check if proportion adds upto 1 for each year
np.allclose(names.groupby(['year','sex'])['prop'].sum(),1)

# get most popular M and F names for each year ( 2 ways)
names[names['prop'] == names.groupby(['year','sex'])['prop'].transform(max)]
# or
names.loc[names.groupby(['year','sex'])['prop'].idxmax()]

# get 1000 most poular M and F names for each year/sex combination
def get_top1000(group):
    return group.sort_values(by='births', ascending=False)[:1000]
# call function after grouping
top_1000 = names.groupby(['year','sex']).apply(get_top1000)

# Time series analysis of names
# number of times each name occurs by year
total_births = top_1000.pivot_table('births', index='year', columns='name', aggfunc=sum )
# plot for a select set of names
subset = total_births[['John','Harry','Mary','Marylin']]
subset.plot(subplots=True, figsize=(12,10), grid=False, title='Number of births per year')
# proportion of births
table = top_1000.pivot_table('prop', index='year', columns='sex', aggfunc=sum)
table.plot(title='proportion of top 1000 names of total', yticks=np.linspace(0,1.2,13), xticks=range(1880, 2020, 10))

# number of distinct names in order or popularity, comparing between 1900 and 2010
boys = top_1000[top_1000.sex == 'M']
df2010 = boys[boys['year'] == 2010]
# cumulative sum of top names making up 50% of total births
prop_cumsum2010 = df2010.sort_values(by='prop', ascending=False)['prop'].cumsum()
# how many names does it take to get to 50%
prop_cumsum2010.values.searchsorted(0.5) + 1
# repeat for 1900
df1900 = boys[boys.year == 1900]
prop_cumsum1900 = df1900.sort_values(by='prop', ascending=False)['prop'].cumsum()
prop_cumsum1900.values.searchsorted(0.5) +1
# now do for all years
# define function to do it for the whole set
def quantile_count(group, q=0.5):
    group = group.sort_values(by='prop', ascending=False)
    return group.prop.values.cumsum().searchsorted(q)+1
# call function after grouping
diversity = top_1000.groupby(['year','sex']).apply(quantile_count)
diversity = diversity.unstack('sex')
diversity.plot(title='number of distinct names in top 50%')

# distribution of names by last letter
# function to extract last letter
get_last_letter = lambda x: x[-1]
last_letters = names.name.map(get_last_letter)
last_letters.name = 'last_letter'
# pivot_table with num of births as values, last letters as rows and year/sex as cols
table = names.pivot_table('births', index=last_letters, columns=['sex','year'], aggfunc=sum)
# select 3 representative years
subtable = table.reindex(columns=[1910,1960,2010], level='year')
# normalize - calculate proportion of names ending in each last letter relative to total births
letter_prop = subtable/subtable.sum().astype(float)
# plot for each gender 
import matplotlib.pyplot as plt
fig, axes = plt.subplots(2,1, figsize=(10,8))
letter_prop['M'].plot(kind='bar',rot=0,ax=axes[0], title='Male')
letter_prop['F'].plot(kind='bar',rot=0,ax=axes[1], title='Female', legend=False)
# normalize by year and sex for a select set of letters by transposing
letter_prop = table/table.sum().astype(float)
dny_ts = letter_prop.ix[['d','n','y'],'M'].T
dny_ts.plot() # shows trends in last names ending with these letters

# find names that have changed gender over the years
all_names = top_1000.name.unique()
mask = np.array(['lesl' in x.lower() for x in all_names])
les_like = all_names[mask]
filtered = top_1000[top_1000.name.isin(les_like)]
filtered.groupby('name').births.sum()
table = filtered.pivot_table('births', index='year', columns='sex', aggfunc='sum')
table = table.div(table.sum(1), axis=0)
table.plot(style = {'M':'k-', 'F':'k--'})