from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from flask_bcrypt import Bcrypt
import sqlite3

auth_bp = Blueprint("auth", __name__, static_folder='../static', template_folder='../templates/auth')
bcrypt = Bcrypt()

# Handle Login functionality of the application
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # If user session appears, direct user to home page without the need of logging in
        if 'user' in session:
            return redirect(url_for('dashboard.home'))
        else:
            return render_template('login.html')
    else:
        username = request.form['username']
        password = request.form['password']

        con = sqlite3.connect('database.db')
        cur = con.cursor()
        sql_query = f"SELECT * FROM User WHERE username = '{username}'"
        users = cur.execute(sql_query).fetchall()

        # Check if username appear in the User table
        if (len(users) == 0):
            flash('User does not exist', category='error')
            return render_template('login.html')
        # Check if password is correct
        elif(not bcrypt.check_password_hash(users[0][2], password)):
            flash('Sorry, Wrong Password!', category='error')
            return render_template('login.html')
        else:
            session['user'] = username
            return redirect(url_for('dashboard.home'))

# Handle Sign Up Functionality of the application
@auth_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'GET':
        return render_template('sign_up.html')
    else:
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        # Check if password match confirm_password
        if password != confirm_password:
            flash('Passwords not match!', category='error')
            return render_template('sign_up.html')

        # Make sure password have at least 8 characters for a better security
        if len(password) < 8:
            flash('Password should have at least 8 characters', category='error')
            return render_template('sign_up.html')

        # Hash password for security reason
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create user account in the User table
        try:
            con = sqlite3.connect('database.db')
            cur = con.cursor()
            sql_query = f"INSERT INTO User (username, password) VALUES ('{username}', '{hashed_password}')"
            cur.execute(sql_query)
            con.commit()
            flash('Sign Up Successful', category='info')
            return redirect(url_for('auth.login'))
        except sqlite3.IntegrityError:
            flash('User has already existed!', category='error')
            return render_template('sign_up.html')

@auth_bp.route('/logout')
def logout():
    # Remove user from the session data
    session.pop('user', None)
    return redirect(url_for('dashboard.index'))