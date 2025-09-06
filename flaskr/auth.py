# Blueprint for authenticating users
import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.db import getDb

bp = Blueprint('auth', __name__, url_prefix='/auth')

# handle user registration
@bp.route('/register', methods=('GET', 'POST'))
def register():
    # user submits the form; authenticate username and password are valid
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = getDb()
        error = None
        
        # check that username and password fields were filled
        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"
        
        # insert user into the database
        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password=password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            # redirect user to login page
            else:
                return redirect(url_for("auth.login"))
            
        flash(error)
    
    return render_template('auth/register.html')

# handle user login
@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = getDb()
        error = None
        # select username from db table
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        
        # user not found in database
        if user is None:
            error = "Incorrect username"
        # incorrect password inputted
        elif not check_password_hash(user['password'], password):
            error = "Incorrect password"
        
        # successful user login
        if error is None:
            session.clear()
            session['user_id'] = user['id']
            # redirect user to home page
            return redirect(url_for('index'))
    
        flash(error)
        
    return render_template('auth/login.html')

# runs before the view function
# checks if a user id is stored in the session and gets stores their data on g.user
@bp.before_app_request
def loadLoggedInUser():
    user_id = session.get('user_id')
    
    if user_id is None:
        g.user = None
    else:
        g.user = getDb().execute(
            'SELECT * FROM user WHERE id = ?', (user_id),
        ).fetchone()
        
# handle user logout
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# redirect to login page if user is not logged in
def loginRequired(view):
    @functools.wraps(view)
    def wrappedView(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    
    return wrappedView