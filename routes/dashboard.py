from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from flask_bcrypt import Bcrypt
import sqlite3
import requests
import datetime
import os
from dotenv import load_dotenv

dashboard_bp = Blueprint("dashboard", __name__, static_folder='../static', template_folder='../templates/dashboard')
bcrypt = Bcrypt()

# Get API Key for The Movie Database (TMDB) API from .env file
load_dotenv()
API_KEY = os.getenv('TMDB_API_KEY')

# Route for index page where everyone landed when they access the application (pagination supported)
@dashboard_bp.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('dashboard.home'))
    else:
        api_query_url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1"
        popular_movies_data = requests.get(api_query_url).json()['results']
        return render_template('movies.html', movies=popular_movies_data)

@dashboard_bp.route('/<page>')
def index_paginate(page):
    if 'user' in session:
        return redirect(url_for('dashboard.home'))
    else:
        if page == '1':
            return redirect(url_for('dashboard.index'))
        api_query_url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page={page}"
        popular_movies_data = requests.get(api_query_url).json()['results']
        return render_template('movies.html', movies=popular_movies_data)

### Routes for providing personalized content for users (only login users can access this route)

# Route for providing users the most trending and popular movie list (only login users can access this route) (pagination supported)
@dashboard_bp.route('/home')
def home():
    # Redirect users to login page if they are not authenticated yet
    if 'user' not in session:
        flash('You must login to access this page!', category='error')
        return redirect(url_for('auth.login'))
    api_query_url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1"
    popular_movies_data = requests.get(api_query_url).json()['results']
    return render_template('movies.html', user=session['user'], home=True, movies=popular_movies_data)

@dashboard_bp.route('/home/<page>')
def home_paginate(page):
    # Redirect users to login page if they are not authenticated yet
    if 'user' not in session:
        flash('You must login to access this page!', category='error')
        return redirect(url_for('auth.login'))
    if page == '1':
        return redirect(url_for('dashboard.home'))
    api_query_url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page={page}"
    popular_movies_data = requests.get(api_query_url).json()['results']
    return render_template('movies.html', user=session['user'], home=True, movies=popular_movies_data)

# Route for allowing users to edit their profile (only login users can access this route)
@dashboard_bp.route('/edit-profile', methods=['GET', 'POST'])
def edit_profile():
    # Redirect users to login page if they are not authenticated yet
    if 'user' not in session:
        flash('You must login to access this page!', category='error')
        return redirect(url_for('auth.login'))
    if request.method == 'GET':
        return render_template('profile.html', user=session['user'])
    else:
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        # Check whether password match confirm_password
        if password != confirm_password:
            flash('Password do not match!', category='error')
            return render_template('profile.html', user=session['user'])

        # Make sure password has at least 8 characters for better security
        if len(password) < 8:
            flash('Password should have at least 8 characters', category='error')
            return render_template('profile.html', user=session['user'])

        # Hash password for security reason
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Update user data in the User table
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            sql_query = f"UPDATE User SET password = '{hashed_password}' WHERE username = '{session['user']}'"
            cur.execute(sql_query)
            con.commit()
            flash('Successfully changed your profile', category='info')
            return render_template('profile.html', user=session['user'])
        except:
            flash('Failed to change your profile', category='error')
            return render_template('profile.html', user=session['user'])

# Route for allowing users to add/delete movies from their favourite movie list (only login users can access this route)
@dashboard_bp.route('/my-favourite', methods=['GET', 'POST', 'DELETE'])
def my_favourite():
    # Redirect users to login page if they are not authenticated yet
    if 'user' not in session:
        flash('You must login to access this page!', category='error')
        return redirect(url_for('auth.login'))
    if request.method == 'GET':
        # Get user's favourite movie list from the Favourite table
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            sql_query = f"SELECT id FROM User Where username = '{session['user']}'"
            user_id = cur.execute(sql_query).fetchone()[0]
            sql_query = f"SELECT movie_id FROM Favourite WHERE user_id = {user_id} ORDER BY datetime DESC"
            movie_ids = cur.execute(sql_query).fetchall()
            my_favourite = []
            for movie_id in movie_ids:
                api_query_url = f"https://api.themoviedb.org/3/movie/{movie_id[0]}?api_key={API_KEY}"
                movie_data = requests.get(api_query_url).json()
                my_favourite.append(movie_data)
            return render_template('favourite.html', user=session['user'], my_favourite=my_favourite)
        except:
            return render_template('favourite.html', user=session['user'], my_favourite=[])
    # Add movies to user's favourite movie list in Favourite table
    elif request.method == 'POST':
        movie_id = int(request.get_json(force=True)['movie_id'])
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            sql_query = f"SELECT id FROM User Where username = '{session['user']}'"
            user_id = cur.execute(sql_query).fetchone()[0]
            sql_query = f"INSERT INTO Favourite VALUES ({user_id}, {movie_id}, '{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')"
            cur.execute(sql_query)
            con.commit()
            flash('Successfully added to my favourite list!', category='info')
            return 'Successfully added to my favourite list'
        except:
            flash('Failed to add to my favourite list', category='error')
            return 'Failed to add to my favourite list'
    # Delete movies from user's favourite movie list in Favourite table
    else:
        movie_id = int(request.get_json(force=True)['movie_id'])
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            sql_query = f"SELECT id FROM User Where username = '{session['user']}'"
            user_id = cur.execute(sql_query).fetchone()[0]
            sql_query = f"DELETE FROM Favourite WHERE user_id = {user_id} AND movie_id = {movie_id}"
            cur.execute(sql_query)
            con.commit()
            flash('Successfully deleted from my favourite list!', category='info')
            return 'Successfully deleted from my favourite list'
        except:
            flash('Failed to delete from my favourite list', category='error')
            return 'Failed to delete from my favourite list'

# Route for tracking user's movie watch history (only login users can access this route)
@dashboard_bp.route('/watch-history', methods=['GET', 'DELETE'])
def watch_history():
    # Redirect users to login page if they are not authenticated yet
    if 'user' not in session:
        flash('You must login to access this page!', category='error')
        return redirect(url_for('auth.login'))
    # Get user's movie watch history from the History table
    if request.method == 'GET':
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            sql_query = f"SELECT id FROM User Where username = '{session['user']}'"
            user_id = cur.execute(sql_query).fetchone()[0]
            sql_query = f"SELECT movie_id, datetime FROM History WHERE user_id = {user_id} ORDER BY datetime DESC"
            movie_history_data = cur.execute(sql_query).fetchall()
            watch_history = []
            for movie_history in movie_history_data:
                api_query_url = f"https://api.themoviedb.org/3/movie/{movie_history[0]}?api_key={API_KEY}"
                movie_data = requests.get(api_query_url).json()
                movie_data['last_watched'] = movie_history[1]
                watch_history.append(movie_data)
            return render_template('history.html', user=session['user'], watch_history=watch_history)
        except:
            return render_template('history.html', user=session['user'], watch_history=[])
    # Delete a specific movie from user's watch history
    else:
        data = request.get_json(force=True)
        movie_id = int(data['movie_id'])
        datetime = data['datetime']
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            sql_query = f"SELECT id FROM User Where username = '{session['user']}'"
            user_id = cur.execute(sql_query).fetchone()[0]
            sql_query = f"DELETE FROM History WHERE user_id = {user_id} AND movie_id = {movie_id} AND datetime = '{datetime}'"
            cur.execute(sql_query)
            con.commit()
            flash('Successfully deleted from watch history list!', category='info')
            return 'Successfully deleted from watch history list'
        except:
            flash('Failed to delete from watch history list', category='error')
            return 'Failed to delete from watch history list'

# Route for user's movie query (pagination supported)
@dashboard_bp.route('/search-movie')
def search_movie():
    query = request.args.get('query')
    page = request.args.get('page')
    if not page:
        page = 1
    api_query_url = f"https://api.themoviedb.org/3/search/movie?api_key={API_KEY}&query={query}&language=en-US&page={page}"
    search_movies_data = requests.get(api_query_url).json()['results']
    movies = []
    for movie in search_movies_data:
        if movie['backdrop_path'] and movie['poster_path'] and movie['release_date'] != '' and movie['overview'] != '':
            movies.append(movie)
    if len(movies) < 3:
        if page == 1:
            flash('Failed to find any related movies', category='error')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Failed to find any related movies', category='error')
            return redirect(url_for('dashboard.search_movie', query=query, page=int(page)-1))
    else:
        if 'user' in session:
            return render_template('movies.html', user=session['user'], movies=movies)
        else:
            return render_template('movies.html', movies=movies)

# Route for browsing the details of a specific movie
@dashboard_bp.route('/movie/<id>')
def movie_details(id):
    # Add to user's watch history in History table whenever user browse the details of a movie
    if 'user' in session:
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        sql_query = f"SELECT id FROM User Where username = '{session['user']}'"
        user_id = cur.execute(sql_query).fetchone()[0]
        sql_query = f"SELECT * FROM History WHERE user_id = {user_id} ORDER BY DATETIME DESC"
        movie_history = cur.execute(sql_query).fetchall()
        if (len(movie_history) == 0 or not (movie_history[0][0] == user_id and movie_history[0][1] == int(id))):
            sql_query = f"INSERT INTO History VALUES ({user_id}, {int(id)}, '{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')"
            cur.execute(sql_query)
            con.commit()
    api_query_url = f"https://api.themoviedb.org/3/movie/{id}?api_key={API_KEY}&append_to_response=videos,credits,reviews,recommendations"
    movie_details_data = requests.get(api_query_url).json()
    # Sanitize movie details data to ensure data is clean and useful
    for i in range(len(movie_details_data['videos']['results'])):
        if 'Official Trailer' in movie_details_data['videos']['results'][i]['name']:
            movie_details_data['videos']['results'][0] = movie_details_data['videos']['results'][i]
    if len(movie_details_data['videos']['results']) > 0 and 'Official Trailer' not in movie_details_data['videos']['results'][0]['name']:
        for i in range(len(movie_details_data['videos']['results'])):
            if 'Trailer' in movie_details_data['videos']['results'][i]['name']:
                movie_details_data['videos']['results'][0] = movie_details_data['videos']['results'][i]
    recommendations = []
    for i in range(len(movie_details_data['recommendations']['results'])):
        if movie_details_data['recommendations']['results'][i]['backdrop_path'] and movie_details_data['recommendations']['results'][i]['poster_path'] and movie_details_data['recommendations']['results'][i]['release_date'] != '' and movie_details_data['recommendations']['results'][i]['overview'] != '':
            recommendations.append(movie_details_data['recommendations']['results'][i])
    movie_details_data['recommendations']['results'] = recommendations
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    sql_query = f"SELECT User.username, Review.rating, Review.content, Review.datetime FROM Review JOIN User on Review.user_id = User.id WHERE Review.movie_id = {int(id)} ORDER BY DATETIME DESC"
    reviews_data = cur.execute(sql_query).fetchall()
    # Group the database's review data for the specific movie and TMDB data together to provide a complete review data for the movie
    reviews = []
    for review_data in reviews_data:
        review = {'author': review_data[0], 'author_details': {'rating': review_data[1]}, 'content': review_data[2], 'updated_at': review_data[3]}
        reviews.append(review)
    for review in movie_details_data['reviews']['results'][::-1]:
        reviews.append(review)
    movie_details_data['reviews']['results'] = reviews
    # Check whether user has this specific movie in their favourite movie list
    if 'user' in session:
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            sql_query = f"SELECT id FROM User Where username = '{session['user']}'"
            user_id = cur.execute(sql_query).fetchone()[0]
            sql_query = f"SELECT * FROM Favourite WHERE user_id = {user_id} AND movie_id = {movie_details_data['id']}"
            my_favourite = cur.execute(sql_query).fetchall()
            if (len(my_favourite) > 0):
                movie_details_data['my_favourite'] = True
            else:
                movie_details_data['my_favourite'] = False
        finally:
            return render_template('movie_details.html', user=session['user'], movie=movie_details_data)
    else:
        return render_template('movie_details.html', movie=movie_details_data)

# Route for allowing users to create reviews for a specific movie
@dashboard_bp.route('/add-review', methods=['POST'])
def add_review():
    # Redirect users to login page if they are not authenticated yet
    if 'user' not in session:
        flash('You must login to access this page')
        return redirect(url_for('auth.login'))
    movie_id = int(request.form['movie_id'])
    rating = float(request.form['rating'])
    review = request.form['review']
    try:
        con = sqlite3.connect('database.db')
        cur = con.cursor()
        sql_query = f"SELECT id FROM User Where username = '{session['user']}'"
        user_id = cur.execute(sql_query).fetchone()[0]
        sql_query = f"INSERT INTO Review VALUES ({user_id}, {movie_id}, {rating}, '{review}', '{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}')"
        cur.execute(sql_query)
        con.commit()
        flash("Successfully added you review for this movie!", category='info')
        return "Successfully added you review for this movie!"
    except:
        flash("Failed to add your review for this movie!", category='error')
        return "Failed to add your review for this movie!"

### Routes for providing movie list of different categories (pagination supported)

@dashboard_bp.route('/popular')
def popular():
    api_query_url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page=1"
    popular_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=popular_movies_data)
    else:
        return render_template('movies.html', movies=popular_movies_data)

@dashboard_bp.route('/popular/<page>')
def popular_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.popular'))
    api_query_url = f"https://api.themoviedb.org/3/movie/popular?api_key={API_KEY}&language=en-US&page={page}"
    popular_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=popular_movies_data)
    else:
        return render_template('movies.html', movies=popular_movies_data)

@dashboard_bp.route('/top-rated')
def top_rated():
    api_query_url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&language=en-US&page=1"
    top_rated_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=top_rated_movies_data)
    else:
        return render_template('movies.html', movies=top_rated_movies_data)

@dashboard_bp.route('/top-rated/<page>')
def top_rated_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.top_rated'))
    api_query_url = f"https://api.themoviedb.org/3/movie/top_rated?api_key={API_KEY}&language=en-US&page={page}"
    top_rated_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=top_rated_movies_data)
    else:
        return render_template('movies.html', movies=top_rated_movies_data)

@dashboard_bp.route('/upcoming')
def upcoming():
    api_query_url = f"https://api.themoviedb.org/3/movie/upcoming?api_key={API_KEY}&language=en-US&page=1"
    upcoming_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=upcoming_movies_data)
    else:
        return render_template('movies.html', movies=upcoming_movies_data)

@dashboard_bp.route('/upcoming/<page>')
def upcoming_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.upcoming'))
    api_query_url = f"https://api.themoviedb.org/3/movie/upcoming?api_key={API_KEY}&language=en-US&page={page}"
    upcoming_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=upcoming_movies_data)
    else:
        return render_template('movies.html', movies=upcoming_movies_data)

### Routes for providing movie list of different genres (pagination supported)

@dashboard_bp.route('/action')
def action():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=28&language=en-US&page=1"
    action_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=action_movies_data)
    else:
        return render_template('movies.html', movies=action_movies_data)

@dashboard_bp.route('/action/<page>')
def action_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.action'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=28&language=en-US&page={page}"
    action_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=action_movies_data)
    else:
        return render_template('movies.html', movies=action_movies_data)

@dashboard_bp.route('/adventure')
def adventure():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=12&language=en-US&page=1"
    adventure_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=adventure_movies_data)
    else:
        return render_template('movies.html', movies=adventure_movies_data)

@dashboard_bp.route('/adventure/<page>')
def adventure_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.adventure'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=12&language=en-US&page={page}"
    adventure_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=adventure_movies_data)
    else:
        return render_template('movies.html', movies=adventure_movies_data)

@dashboard_bp.route('/animation')
def animation():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=16&language=en-US&page=1"
    animation_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=animation_movies_data)
    else:
        return render_template('movies.html', movies=animation_movies_data)

@dashboard_bp.route('/animation/<page>')
def animation_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.animation'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=16&language=en-US&page={page}"
    animation_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=animation_movies_data)
    else:
        return render_template('movies.html', movies=animation_movies_data)

@dashboard_bp.route('/comedy')
def comedy():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=35&language=en-US&page=1"
    comedy_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=comedy_movies_data)
    else:
        return render_template('movies.html', movies=comedy_movies_data)

@dashboard_bp.route('/comedy/<page>')
def comedy_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.comedy'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=35&language=en-US&page={page}"
    comedy_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=comedy_movies_data)
    else:
        return render_template('movies.html', movies=comedy_movies_data)

@dashboard_bp.route('/crime')
def crime():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=80&language=en-US&page=1"
    crime_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=crime_movies_data)
    else:
        return render_template('movies.html', movies=crime_movies_data)

@dashboard_bp.route('/crime/<page>')
def crime_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.crime'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=80&language=en-US&page={page}"
    crime_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=crime_movies_data)
    else:
        return render_template('movies.html', movies=crime_movies_data)

@dashboard_bp.route('/documentary')
def documentary():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=99&language=en-US&page=1"
    documentary_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=documentary_movies_data)
    else:
        return render_template('movies.html', movies=documentary_movies_data)

@dashboard_bp.route('/documentary/<page>')
def documentary_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.documentary'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=99&language=en-US&page={page}"
    documentary_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=documentary_movies_data)
    else:
        return render_template('movies.html', movies=documentary_movies_data)

@dashboard_bp.route('/drama')
def drama():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=18&language=en-US&page=1"
    drama_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=drama_movies_data)
    else:
        return render_template('movies.html', movies=drama_movies_data)

@dashboard_bp.route('/drama/<page>')
def drama_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.drama'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=18&language=en-US&page={page}"
    drama_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=drama_movies_data)
    else:
        return render_template('movies.html', movies=drama_movies_data)

@dashboard_bp.route('/family')
def family():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=10751&language=en-US&page=1"
    family_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=family_movies_data)
    else:
        return render_template('movies.html', movies=family_movies_data)

@dashboard_bp.route('/family/<page>')
def family_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.family'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=10751&language=en-US&page={page}"
    family_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=family_movies_data)
    else:
        return render_template('movies.html', movies=family_movies_data)

@dashboard_bp.route('/fantasy')
def fantasy():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=14&language=en-US&page=1"
    fantasy_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=fantasy_movies_data)
    else:
        return render_template('movies.html', movies=fantasy_movies_data)

@dashboard_bp.route('/fantasy/<page>')
def fantasy_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.fantasy'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=14&language=en-US&page={page}"
    fantasy_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=fantasy_movies_data)
    else:
        return render_template('movies.html', movies=fantasy_movies_data)

@dashboard_bp.route('/history')
def history():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=36&language=en-US&page=1"
    history_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=history_movies_data)
    else:
        return render_template('movies.html', movies=history_movies_data)

@dashboard_bp.route('/history/<page>')
def history_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.history'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=36&language=en-US&page={page}"
    history_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=history_movies_data)
    else:
        return render_template('movies.html', movies=history_movies_data)

@dashboard_bp.route('/horror')
def horror():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=27&language=en-US&page=1"
    horror_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=horror_movies_data)
    else:
        return render_template('movies.html', movies=horror_movies_data)

@dashboard_bp.route('/horror/<page>')
def horror_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.horror'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=27&language=en-US&page={page}"
    horror_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=horror_movies_data)
    else:
        return render_template('movies.html', movies=horror_movies_data)

@dashboard_bp.route('/music')
def music():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=10402&language=en-US&page=1"
    music_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=music_movies_data)
    else:
        return render_template('movies.html', movies=music_movies_data)

@dashboard_bp.route('/music/<page>')
def music_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.music'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=10402&language=en-US&page={page}"
    music_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=music_movies_data)
    else:
        return render_template('movies.html', movies=music_movies_data)

@dashboard_bp.route('/mystery')
def mystery():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=9648&language=en-US&page=1"
    mystery_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=mystery_movies_data)
    else:
        return render_template('movies.html', movies=mystery_movies_data)

@dashboard_bp.route('/mystery/<page>')
def mystery_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.mystery'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=9648&language=en-US&page={page}"
    mystery_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=mystery_movies_data)
    else:
        return render_template('movies.html', movies=mystery_movies_data)

@dashboard_bp.route('/romance')
def romance():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=10749&language=en-US&page=1"
    romance_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=romance_movies_data)
    else:
        return render_template('movies.html', movies=romance_movies_data)

@dashboard_bp.route('/romance/<page>')
def romance_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.romance'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=10749&language=en-US&page={page}"
    romance_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=romance_movies_data)
    else:
        return render_template('movies.html', movies=romance_movies_data)

@dashboard_bp.route('/science-fiction')
def science_fiction():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=878&language=en-US&page=1"
    science_fiction_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=science_fiction_movies_data)
    else:
        return render_template('movies.html', movies=science_fiction_movies_data)

@dashboard_bp.route('/science-fiction/<page>')
def science_fiction_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.science_fiction'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=878&language=en-US&page={page}"
    science_fiction_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=science_fiction_movies_data)
    else:
        return render_template('movies.html', movies=science_fiction_movies_data)

@dashboard_bp.route('/tv-movie')
def tv_movie():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=10770&language=en-US&page=1"
    tv_movie_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=tv_movie_movies_data)
    else:
        return render_template('movies.html', movies=tv_movie_movies_data)

@dashboard_bp.route('/tv-movie/<page>')
def tv_movie_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.tv_movie'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=10770&language=en-US&page={page}"
    tv_movie_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=tv_movie_movies_data)
    else:
        return render_template('movies.html', movies=tv_movie_movies_data)

@dashboard_bp.route('/thriller')
def thriller():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=53&language=en-US&page=1"
    thriller_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=thriller_movies_data)
    else:
        return render_template('movies.html', movies=thriller_movies_data)

@dashboard_bp.route('/thriller/<page>')
def thriller_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.thriller'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=53&language=en-US&page={page}"
    thriller_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=thriller_movies_data)
    else:
        return render_template('movies.html', movies=thriller_movies_data)

@dashboard_bp.route('/war')
def war():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=10752&language=en-US&page=1"
    war_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=war_movies_data)
    else:
        return render_template('movies.html', movies=war_movies_data)

@dashboard_bp.route('/war/<page>')
def war_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.war'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=10752&language=en-US&page={page}"
    war_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=war_movies_data)
    else:
        return render_template('movies.html', movies=war_movies_data)

@dashboard_bp.route('/western')
def western():
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=37&language=en-US&page=1"
    western_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=western_movies_data)
    else:
        return render_template('movies.html', movies=western_movies_data)

@dashboard_bp.route('/western/<page>')
def western_paginate(page):
    if page == '1':
        return redirect(url_for('dashboard.western'))
    api_query_url = f"https://api.themoviedb.org/3/discover/movie?api_key=9c22c7f5ca46a7e3e5b120043668bc39&with_genres=37&language=en-US&page={page}"
    western_movies_data = requests.get(api_query_url).json()['results']
    if 'user' in session:
        return render_template('movies.html', user=session['user'], movies=western_movies_data)
    else:
        return render_template('movies.html', movies=western_movies_data)