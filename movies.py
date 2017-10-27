# -*- coding: utf-8 -*-
"""
Spyder Editor

Tutorial python script for data manipulation using pandas
"""

import pandas as pd

unames = ['user_id', 'gender', 'age', 'occupation', 'zip']
users = pd.read_table('../ch02/movielens/users.dat', sep='::', header=None, names=unames)

rnames = ['user_id', 'movie_id', 'rating', 'timestamp']
ratings = pd.read_table('../movielens/ratings.dat', sep='::', header=None, names=rnames)

mnames = ['movie_id', 'title', 'genres']
movies = pd.read_table('../movielens/movies.dat', sep='::', header=None, names=mnames)

# merge all three dataframes into one for further analysis
data = pd.merge(pd.merge(ratings,users),movies)

# use pivot_table to calculate mean ratings by gender for each movie
# so rows of the result will be the movies, cols will be mean ratings by gender
mean_ratings = data.pivot_table('rating', index='title', columns='gender',aggfunc = 'mean')

# use groupby title and aggregate by size (number of titles)
ratings_by_title = data.groupby('title').size()

# select only titles that have 250 or more ratings
active_titles = ratings_by_title.index[ratings_by_title >= 250]

# select active titles found above from the mean_ratings df
active_title_ratings = mean_ratings.ix[active_titles]

# top films as per female viewer ratings
top_f_ratings = mean_ratings.sort_index(by='F', ascending=False)

# what movies were most divisive among feamle and male viewers

# add a column to the df the value of which will be the difference between the ratings
mean_ratings['diff'] = mean_ratings['M'] - mean_ratings['F']
# sort by the new column
sort_by_diff = mean_ratings.sort_index(by='diff')

# find movies where the disagreement was the most
# ie std dev of the ratings was the highest
# group by title and then calculate the sd of the ratings
rating_std_by_title = data.groupby('title')['rating'].std()
rating_std_by_title = rating_std_by_title.ix[active_titles]
rating_std_by_title.order(ascending=False)[:10]
