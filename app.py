from flask import Flask, render_template, request, redirect, url_for
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)


#web scraping part of the project

#takes the movie title and returns the url for the movie cast list
def get_movie_url(title):
    api_key = "5cb75ca6"
    search_url = f"http://www.omdbapi.com/?t={title}&apikey={api_key}" #search the movie title using the api key

    response = requests.get(search_url)

    if response.status_code != 200:
        print("Problem grabbing the movie ID from the title, it is likely that the movie title is spelled incorrectly")
        return None
    
    data = response.json()

    if data['Response'] == 'False':
        print("Movie Not Found")
        return None
    
    imdb_id = data['imdbID']
    movie_url = f"https://www.imdb.com/title/{imdb_id}/fullcredits" #grab the movie cast url
    return movie_url

def get_cast(movie_url):
    response = requests.get(movie_url) #accesses the cast website url

    #print(response.text)

    soup = BeautifulSoup(response.text, 'html.parser') #parse the data

    cast_section = soup.find('table', {'class': 'cast_list'}) #grab the table

    if cast_section == None: #error handling
        print("throwing error under get_cast")
        return redirect(url_for('error'))

    actors = cast_section.find_all('a', {'href': lambda x: x and x.startswith('/name/')}) #stackoverflow moment

    actor_names = [actor.get_text(strip=True) for actor in actors] #create the list of actor names

    return actor_names


def driver_logic(movies):
    
    num_of_movies = len(movies) #grab how many movies the user input

    #get the movie urls for the cast
    def get_urls(movies):
        cast_URLs = []
        for movie in movies:
            curUrl = get_movie_url(movie)
            if curUrl == None:
                print("throwing error under driver logic getting movie cast URLs")
                return "error"
            cast_URLs.append(curUrl)
        return cast_URLs

    cast_URLs = get_urls(movies) #the list of the urls for the movie casts

    #set up a list to store all of the cast lists
    cast_lists = []
    #cast_lists -> cast_list -> cast_member
    for url in cast_URLs:
        cast_lists.append(get_cast(url))
    
    #throw every name into a dictionary, increment if we already have that name in the dictionary
    #at the end, if the increments is equal to num_of_movies, then that person had to have been in all given movies
    big_cast_list = dict()

    for cast_list in cast_lists:
        for cast_member in cast_list:
            if cast_member in big_cast_list: #if already found, just increment
                big_cast_list[cast_member] = big_cast_list[cast_member] + 1
            else:
                big_cast_list[cast_member] = 1
    
    final_cast_list = []

    names = big_cast_list.keys() #grab the names

    for name in names: #loop through the names
        if big_cast_list[name] == num_of_movies:
            final_cast_list.append(name)

    return final_cast_list


@app.route('/', methods=['GET', 'POST'])
#here is the home screen, where we ask users about the movies they are trying to find common actors for
def index():
    if request.method == 'POST':
        #get all movie titles
        movie_titles = request.form.getlist('movie')
        #perform driver logic
        actor_list = driver_logic(movie_titles)

        if actor_list == "error":
            return redirect(url_for('error'))

        return redirect(url_for('actors', actors=','.join(actor_list)))
    return render_template('index.html')

#this is the actor screen, essentially the result screen for the movies input
@app.route('/actors')
def actors():
    #names
    actors = request.args.get('actors', '')
    #split actors back into a list
    actor_list = actors.split(',')
    return render_template('actors.html',actor_list=actor_list)

@app.route('/error')
def error():
    return render_template('error.html')


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)


