

#------------------------------scrape urls from imdb.com top 10,000 movies archive list-------------------------#

def scrape_urls_from_imdb_archive_page():
    '''
    function to get the movie urls of the top 10,000 movies from the 
    imdb archive pages. The pages have about 250 movies on each page 
    and go to 40 pages total. 
    '''
    ## 351 is the value present at the first page, and so that is what we start with. 
    list_position = 351
    ## url_list will contain the links for the individual movies
    url_list = []
    for i in range(40):
        ## the base url does not change, but the list_position does in increments of 250, 
        ## as mentioned in the doc string
        url = 'http://www.imdb.com/list/ls057823854/?start={}&view=compact&sort=release_date_us:desc'.format(str(list_position))
        print url
        response = requests.get(url)
        page = response.text
        ## xml is necessary because the html5 parser cuts off the list pages.
        soup = BeautifulSoup(page, 'xml')
        ## get list of titles of the movies
        title_list = soup.find_all(class_='title')
        count = 0
        ## make urls out of the titles by combining them with the 
        ## titles
        for title in title_list:
            while count < len(title_list):
                a = title_list[count].contents
                href = a[0].get('href')
                imdb = 'http://www.imdb.com'
                movie_url = str(imdb + href)
                url_list.append(movie_url)
                count += 1
        ## add 250 so next pass of the loop goes to the next page
        list_position += 250
        return url_list
                                                                                                         
                                                                                                        
                                                                                                         
 



#------------------------------scrape data from each movie's page using its url-------------------------#
def scrape_movie_page_data(url):
    '''
    function to scrape each movie page from the url list
    and return the html text of the page
    '''
    response = requests.get(url)
    ## make sure we connected
    if response.status_code != requests.codes.ok:
        print i, 'Error: request.get(url) Status NOT 200'
        return None
    page = response.text
    return page


 def get_release_date(soup):
    '''
    Function to get the release date of the movie by trying to find
    it in numerous places on the page
    '''
    try:
        if soup('h4')[20].contents == [u'Release Date:']:
            date_string = str(soup('h4')[20].next.next)
        elif soup('h4')[19].contents == [u'Release Date:']:
            date_string = str(soup('h4')[19].next.next)
        elif soup('h4')[17].contents == [u'Release Date:']:
            date_string = str(soup('h4')[17].next.next)    
        else:
            date_string = str(soup('h4')[18].next.next)
        date_split = date_string.split( ' ')
        date = date_split[1] + ' ' + date_split[2] + ' ' + date_split[3]
    except :
        date = 'Error' 
    return date


def get_genres(soup):
    '''
    Function to get the genres of the movie, and append
    them to a list, which is returned.
    '''
    genre_list = []
    genre_tags = soup('span', itemprop="genre")
    for item in genre_tags:
        genre = str(item.string)
        genre_list.append(genre)
    return genre_list



def get_box_office_html(soup):
    '''
    Function to scrape the box office info page and get 
    the html text
    '''
    ## genereic url extension for movie's box office page
    box_office_url_extension = 'business?ref_=tt_dt_bus'
    url = str(soup(property="og:url")[0]).split ('"')[1]
    box_office_url = url + box_office_url_extension
    ## get box office info html text
    response = requests.get(box_office_url)
    page = response.text
    soup = BeautifulSoup(page, 'xml')
    ## make sure we get response
    if response.status_code != requests.codes.ok:
        print i, 'Error: request.get(url) Status NOT 200'
        return None
    else:
        return soup


def get_opening_weekend(box_soup):
    '''
    Function to try and find opening weekend dollar amount.
    '''
    try:
        if box_soup(text='Weekend Gross'):
            if '$' in box_soup(text='Weekend Gross')[0].next:
                opening_string = str(box_soup(text='Weekend Gross')[0].next)
                opening_weekend = int(re.sub("[^0-9]", "", opening_string))
            else: opening_weekend = 'N/A'
        else: opening_weekend = 'N/A'
    except UnicodeEncodeError:
        opening_weekend = 'Error'
    return opening_weekend



def get_opening_weekend_screens(box_soup):
    '''
    Function to get the ammount of screens the movie opened on
    in its opening weekend and return that ammount.
    '''
    try:
        screen_string = str(box_soup('h5')[15].next.next.next.next.next.next.next.next)
        opening_weekend_screens = re.sub(r'\W+', '', screen_string)
    except :
        opening_weekend_screens = 'Error'
    return opening_weekend_screens
    




def get_movie_info(url_list):
    '''
    Function to scrape the title, release date, genres, and box office info(opening dollars)
    and screens released) for each movie.
    '''
    movie_info = defaultdict(dict)
    for url in url_list:
        page = scrape_movie_page_data(url)
        soup = BeautifulSoup(page, 'xml')
        ##check if it's a tv movie (we do not want those)
        tv_movie_tag = str(soup(class_="infobar")[0].next)
        try:
            if re.sub(r'\W+', '', tv_movie_tag) != 'TVMovie' and re.sub(r'\W+', '', tv_movie_tag) != 'TVSpecial':
                ## get title
                head = soup(class_='header')
                sp = head[0](class_="itemprop")
                title = str(sp[0].string)
        except UnicodeEncodeError:
            continue
        ## get and enter release date entry
        date = get_release_date(soup) 
        movie_info[title]['date']=date
        ## get genres   
        genre_list = get_genres(soup)
        movie_info[title]['genre']=genre_list
        ## go to box office info page to scrape that data
        if get_box_office_html(soup):
            box_soup = get_box_office_html(soup)
        else:
            opening_weekend = 'Error'
            screens = 'Error'    
        ## get opening weekend amount
        opening_weekend = get_opening_weekend(box_soup)
        movie_info[title]['opening']=opening_weekend
        ## get amount of screens movie opened on 
        screens = get_opening_weekend_screens(box_soup)
        movie_info[title]['screens']=screens
    return movie_info