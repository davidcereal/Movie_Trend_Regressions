# MovieTrendRegressions
A data science project mapping the life of movie trends using linear regression analysis.

MovieTrendRegressions is the repo for a data science project in which i scraped movie data from imdb (and supplemented it with boxofficemojo) and then tried to find historical "trending" occurences in movie genres and subgenres. 
A genre is "trending" when a signficant number more movies are released in a given timespan than normal. 
I plotted the life of these trending genres using their opening box office intake (normalized by number of screens released).
My goal was to determine if movies belonging to a trending genre could expect to make more or less money based on how much time had passed since the start of the trend. 

The modules contain most of the functions used for the scraping and all of the functions used for the demo where i explore how I went about classifying the movies into subgenres (gangster, dystopian, etc) and how I determined when, historically, these subgenres underwent trends. I also plot the trend using linear regression. 

Check out the [demo notebook](https://github.com/dberger1989/MovieTrendRegressions/blob/master/movie_trend_demo.ipynb) for a look at the methodology, and the [presentation pdf](https://github.com/dberger1989/MovieTrendRegressions/blob/master/movie_trend_presentation.pdf) for more of the details.

My next iteration will be to take a step back and use the keyword/genre data scraped for each movie and cluster the movies using an 
unsupervised clustering model to divide the movies into subgenres, and then run the trend analysis from there. 
