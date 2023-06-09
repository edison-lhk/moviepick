<h1 align="center">MoviePick 🍿</h1>

## Description:

MoviePick is a Full-Stack Movie Review App designed specifically for people who love movies,
but have the tiny little problem of spending most of their time for school or work, so finding
whether a movie is worth the time they spend on during their precious free time is very important.
MoviePick provides these kind of people a platform to browse the most recent trending and popular movies
of different categories (popular, top rated, upcoming) and genres (action, adventure, comedy, etc..), and
the specific movie details and reviews, so that they can find the best movie that is worth watching in their
free time.

## Special Features:
- Provide authenticated users with personalized content section (Home, Edit Profile, My Favourite, Watch History)
- Provide only authenticated users the ability to add a movie to their favourite list by clicking the heart button in a movie details page
- Provide only authenticated users the ability to track their movie watch history
- Provide only authenticated users the ability to create reviews for a particular movie in a movie details page
- In my favourite section, users are able to delete movie from their favourite list
- In watch history section, users are able to delete movie form their watch history
- Provide pagination supported for movie list page

## User account

Just in case you don't want to manually create a new user account
- username: edisonliem
- password: edisonliem1234

## Getting Started

### Requirements

- Python3
- Pip3

### Installation

1. Create and activate virtual environment using venv
```bash
$ python3 -m venv env
$ source env/bin/activate
```

2. Use Python's package manager pip to install all packages
```bash
$ pip3 install -r requirements.txt
```

### .env Setup

Create a .env file in the root directory of the project, then type the following code into the file to create all required environment variables: (Replace values with API KEY VALUE)

```bash
TMDB_API_KEY='API KEY VALUE'
```

### Run Application
```bash
$ python3 app.py
```

## Language and Tools:

<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML Badge" style="padding-right: 10px;"> <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS Badge" style="padding-right: 10px;"> <img src="https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E" alt="CSS Badge" style="padding-right: 10px;"> <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Badge" style="padding-right: 10px;"> <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white" alt="Flask Badge" style="padding-right: 10px;"> <img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite Badge" style="padding-right: 10px;">