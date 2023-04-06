from flask import Flask
from datetime import timedelta
import sqlite3

# Setting up application
app = Flask(__name__)

# Configure application
app.config['SECRET_KEY'] = 'jad919bxuq11'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

# Create database schema
con = sqlite3.connect('database.db')
cur = con.cursor()

# Create User table
create_user_table_query = '''
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
'''
cur.execute(create_user_table_query)

# Create Favourite table
create_favourite_table_query = '''
    CREATE TABLE IF NOT EXISTS Favourite (
        user_id INT NOT NULL,
        movie_id INT NOT NULL,
        datetime DATETIME NOT NULL,
        PRIMARY KEY(user_id, movie_id),
        FOREIGN KEY(user_id) REFERENCES User(id)
    );
'''
cur.execute(create_favourite_table_query)

# Create History table
create_history_table_query = '''
    CREATE TABLE IF NOT EXISTS History (
        user_id INT NOT NULL,
        movie_id INT NOT NULL,
        datetime DATETIME NOT NULL,
        FOREIGN KEY(user_id) REFERENCES User(id)
    );
'''
cur.execute(create_history_table_query)

# Create Review table
create_review_table_query = '''
    CREATE TABLE IF NOT EXISTS Review (
        user_id INT NOT NULL,
        movie_id INT NOT NULL,
        rating FLOAT NOT NULL,
        content TEXT NOT NULL,
        datetime DATETIME NOT NULL,
        FOREIGN KEY(user_id) REFERENCES User(id)
    );
'''
cur.execute(create_review_table_query)

# Registering blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp

app.register_blueprint(auth_bp, url_prefix='/')
app.register_blueprint(dashboard_bp, url_prefix='/')

# Set application listen to port
if __name__ == '__main__':
    app.run()