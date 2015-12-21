from __future__ import division
import pickle
import pandas as pd
import requests
from bs4 import BeautifulSoup
import sys
import os
from collections import defaultdict
import re
import json
from collections import Counter
import dateutil
from dateutil import parser
from collections import defaultdict

import datetime

from numpy import arange
import matplotlib.pyplot as plt

from patsy import dmatrices
from patsy import dmatrix

import statsmodels.api as sm
from sklearn.linear_model import LinearRegression
import seaborn as sns

#-----------------------Determine genre--------------------------#


def make_genre_dictionary(movie_data, genre, condition, keyword):
    '''
    Function to extract movies of a certain user specfified genre
    and with user specified keywords and make a dictionary where
    'count' is the number of movies fitting the genre/keyword
    combination that were released in a given year
    
    Arguments: 
        movie_data: movie data scraped from imdb
        genre: find a list of them at: http://www.imdb.com/genre/
        condition: whether to filter items matching both keyword and genre or at least one of them.
                    enter 'and for both, and 'or' for at least one.
        keywords: find a list of them at: http://www.imdb.com/search/keyword/
    
    Returns:
        A dictionary with years and the number of movies released during that year
 
    '''
    genre_dict = defaultdict(dict)
    for key in movie_data.keys():
        ## if the condition is set to "and" and the matches must match both keywords:
        if condition == 'and':
        ## check to see if both conditions are present:
            if genre in movie_data[key]['keywords'] and keyword in movie_data[key]['keywords']:
                if date_helper(movie_data[key]['date']):
                    year = parser.parse(movie_data[key]['date']).year
                    ## add the movie to the count for that year
                    genre_dict['count'][year]= genre_dict['count'].get(year, 0) + 1
        ## if condition is set to "or":
        else: 
            ## check to see if either one or both conditions are matched by keywords
            if genre in movie_data[key]['keywords'] or keyword in movie_data[key]['keywords']:
                if date_helper(movie_data[key]['date']):
                    year = parser.parse(movie_data[key]['date']).year
                    ## add the movie to the count for that year
                    genre_dict['count'][year]= genre_dict['count'].get(year, 0) + 1 
    return genre_dict


def make_genre_data_frame(genre_dictionary, rolling_mean):
    '''
    Function that takes previously made genre dictionary and turns it into a pandas dataframe.
    
    Arguments:
        genre_dictionary: A dictionary of all movies matching a previously
        specified genre and keywords
        rolling_mean: how many years back you want the rolling mean to be based off of
    
    Returns:
        A pandas dataframe where the rolling mean column is the mean of the previous 5 years' counts, and the 
        diffrence from the mean column is how different the current year's mean is from 
        previous year's mean. 
    '''
    df = pd.DataFrame.from_dict(genre_dictionary)
    ## make the index of the dataframe consecutive years
    start = pd.datetime(1972, 1, 1)
    end = pd.datetime(2016, 1, 1)
    x = pd.date_range(start, end, freq='A').year
    df = df.reindex(x)
    df = df.fillna(0)
    ## make a column with the rolling mean of the n previous years
    df['rolling mean']=pd.rolling_mean(df['count'], rolling_mean).shift(+1)
    ## make a column that calculcated the proportion of the current year's movie count 
    ## and the rolling mean up to that point
    df['proportion of prior rolling mean']=df['count']/df['rolling mean']
    return df



#-----------------------Determine trends in genre--------------------------#



def plot_trendiness(genre_dataframe, trend_proportion_threshold):
    '''
    Function to plot the difference between the movies released per year and the previous
    3 year mean. If year features many more movies of a trend released than in years prior, we
    can say it is "trending."
    The threshold argument allows you to determine what the cutoff is to define 'trending'

    Arguments:
    df: a dataframe of movies released per year of the genre. 
    trend_proportion_threshold: movies above this proportion threshold will be considered "trending"



    Returns: a graph showing the trendiness of a movie for each year
    '''
    df_plot = genre_dataframe.reset_index()
    df_plot['trend_cutoff'] = trend_proportion_threshold
    count = df_plot['count']
    rolling_mean = df_plot['rolling mean']
    difference_mean = df_plot['proportion of prior rolling mean']
    date = df_plot['index']
    cutoff = df_plot['trend_cutoff']
    figure(figsize=(15,8))
    count_line = plt.plot(date, cutoff, 'r-', label=count)
    rolling_mean_line = plt.plot(date, difference_mean, 'y-', label=count)
    plt.legend(['Trend Threshold ({})'.format(trend_threshold), 'Count as Proportion of Rolling Mean'])
    plt.title('Trend Threshold')
    plt.ylabel('Movies Made')
    plt.xlabel('Year')
    plt.show()


def make_genre_movie_info_dict(movie_data, genre, keyword):
    '''
    Function to make a dictionary with only movies of a specific user-defined
    genre and keywords
    
    Arguments:
        movie_data: movie data scraped from imdb
        genre: find a list of them at: http://www.imdb.com/genre/
        keywords: find a list of them at: http://www.imdb.com/search/keyword/
    
    Returns:
        A dictionary with only movies of specific genre and keyword, and their 
        release data, and opening weekend screen numbers and box office intake. 
    '''
    movie_info_dict = defaultdict(dict)
    for key in movie_data.keys():
        if genre in movie_data[key]['genre'] and keyword in movie_data[key]['keywords']:
            if date_helper(movie_data[key]['date']):
                year = parser.parse(movie_data[key]['date']).year
                movie_info_dict[year][key]= defaultdict(dict)
                movie_info_dict[year][key]['date']= movie_data[key]['date']
                movie_info_dict[year][key]['screens']= movie_data[key]['screens']
                movie_info_dict[year][key]['opening']= movie_data[key]['opening']
    return movie_info_dict


def make_genre_df(genre_movie_info_dict, min_screens=0):
    '''
    Function to take a dictionary of movies and make a dataframe out of their info.
    
    Arguments:
        genre_movie_info_dict: a dictionary with movie_info 
        min_screens: allows you to filter out movies released on very few screens
    Returns:
        a pandas dataframe with all the movie info, and with movies with n/a's for
        screens released and opening intake filtered out.
        'normalized opening' column indicates the $ gross for the opening weekend per screen 
        upon which the movie was released that weekend. 
    
    '''
    frames = []
    years = []
    for year, movies in genre_movie_info_dict.items():
        years.append(year)
        frames.append(pd.DataFrame.from_dict(movies, orient='index'))
    ## filter out all movies that don't have the opening or screens data
    genre = pd.concat(frames, keys=years)
    genre = genre[genre.screens != 'N/A']
    genre = genre[genre.screens != 'n/a']
    genre = genre[genre.screens != 'Error']
    genre = genre[genre.opening != 'N/A']
    genre = genre[genre.screens != '']
    genre = genre[genre.opening != '']
    genre = genre[genre.opening != 'n/a']
    genre = genre[genre.opening != 'Error']
    genre['opening'] = genre['opening'].map(lambda x: parseint(x))
    genre['screens'] = genre['screens'].map(lambda x: parseint(x))
    genre['date'] = genre['date'].map(lambda x: parser.parse(x))
    ## create a normalized opeing column that calculates opening gross 
    ## per screen released. 
    genre['normalized_opening']= genre['opening']/genre['screens']
    ## filter out movies with outragous and erroneous gross 
    genre = genre[genre.normalized_opening < 20000]
    ## filter out movies released on very few screens. Those are either not such good
    ## indicators as being limited releases or simply bad data. 
    genre = genre[genre.screens > min_screens]
    genre = genre.reset_index()
    pd.set_option('display.max_rows', 1000)

    return genre

#-----------------------plot trends--------------------------#


def plot_trend(genre_df, start_year, end_year):
    '''
    Takes a dataframe with all the movies of a trend and their box office stats
    and plots them in chronological order to see how the trend plays out over time.
    
    
    Arguments:
        trend_df: a dataframe with the trend info
        start_year: starting year of the trend
        end_year: ending year of the trend
    
    Returns: 
        a plot graphing the trend
    '''
    trend_df = genre_df[genre_df['level_0'].isin([i for i in range(start_year, end_year+ 1)])]
    figure(figsize=(17,13))
    trend_df = trend_df.sort(['date'])
    plt.plot(trend_df['date'], trend_df['normalized_opening'])
    plt.legend(["Opening Weekend $ per Screen Released"])
    return plt.show()
    

def sort_season(x):
    '''
    Adds a feature of season bins, to be used in the linear
    regressoin
    '''
    if x in [11, 12, 1]:
        return 'Winter'
    if x in [5, 6, 7, 8]:
        return 'Summer'
    if x in [9, 10,]:
        return 'Fall'
    if x in [2, 3, 4,]:
        return 'Spring'

def prepare_df_for_LR(trend_df, start_year, end_year):
	'''
	Takes the trend_df and adds the season feature, as well as adding 
	a time delta column, so we can plot the movie success against time 
	passed since movie trend began.
	Arguments: 
	trend_df: df of the movies belonging to the trend years
	start_year: year from which the progress of the trend will be plotted from

	'''
	## make a dataframe with only movies in the trend years we want to explore:
	trend = trend_df[trend_df['level_0'].isin([i for i in range(start_year, end_year+ 1)])]
	start_year = '01/01/' + str(start_year)
	trend = trend.sort(['date'])
	## time delta is time surpassed from the beginning of the year the trend started to the end of the trend
	trend['time_delta']=trend['date'].apply(lambda x: str(x - parser.parse(str(start_year))))
	trend['time_delta_num'] = trend['time_delta'].str.replace(r'days[\s\S]+', '').apply(lambda x: int(x))
	## indicate which season the movie was released in, so we can add that as a feature
	trend['season']=trend['date'].apply(lambda x: sort_season(x.month))
	return trend
    
    



#-----------------------helper functions------------------------------------#


def parseint(string):
    '''
    Function to take a string and return only the digits from it
    '''
    string = str(string)
    return int(''.join([x for x in string if x.isdigit()]))


def date_helper(date):
    '''
    Function to confirm a data can be parsed into a datetime object. 
    '''
    try:
        date = parser.parse(date)
        return True
    except: 
        pass
    return False


#-----------------------helper functions--------------------------#