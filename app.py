import os
import psycopg2
from flask import Flask, render_template, request, url_for, redirect, session, flash
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from forms import SignUpForm, EditForm, ThreadForm, ReplyForm
app = Flask(__name__)
app.secret_key = 'yoursecretkey'


def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='postgres',
                            user='postgres',
                            password='jason123')
    return conn



@app.route('/', methods=('GET', 'POST'))
def login():
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM project_schema.users WHERE username = %s AND password = %s', 
            (username, password,)
        )
        # Fetch one record and return result
        account = cur.fetchone()
        cur.close()
        conn.close()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

@app.route('/register/', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    form = SignUpForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm = form.confirm.data
        address = form.address.data
        latitude = form.latitude.data
        longitude = form.longitude.data
        profile = form.profile.data
        if password==confirm:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM project_schema.users WHERE username = %s', (username,))
            account = cur.fetchone()
            if account:
                msg = 'Account already exists!'
            else:
                # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
                cur.execute(
                    'INSERT INTO project_schema.users(userid, username, password, address, latitude, longitude, profile, photo) VALUES ((select max(userid)+1 from project_schema.users), %s, %s, %s, %s, %s, %s)',
                    (username, password, address, latitude, longitude, profile,)
                )
                conn.commit()
                cur.close()
                conn.close()
                msg = 'You have successfully registered!'
                return redirect(url_for('login'))
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'   
        
    # Show registration form with message (if any)
    
    return render_template('register.html', msg=msg, form=form)

@app.route('/logout/')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

@app.route('/index/')
def index():
    if 'loggedin' in session:
        return render_template('index.html', userid = session['id'], username=session['username'])
    return redirect(url_for('login'))

@app.route('/profile/')
def profile():
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM project_schema.users where userid=%s;',
            (session['id'],)
        )
        profile = cur.fetchone()
        cur.close()
        conn.close()
        return render_template('profile.html', profile=profile)
    return redirect(url_for('login'))

@app.route('/editprofile/', methods=['GET', 'POST'])
def editprofile():
    if 'loggedin' in session:
        form = EditForm()
        if request.method=='POST':
            print('check data and submit')
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'SELECT * FROM project_schema.users where userid=%s;',
                (session['id'],)
            )
            profile = cur.fetchone()
            form.address.data = profile[3]
            form.latitude.data = profile[4]
            form.longitude.data = profile[5]
            form.profile.data = profile[6]
            cur.close()
            conn.close()
            return render_template('editprofile.html', form=form)
        if form.validate_on_submit():
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'update project_schema.users set address=%s, latitude=%s, longitude=%s, profile=%s where userid=%s',
                (form.address.data, form.latitude.data, form.longitude.data, form.profile.data, session['id'],)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash('Update Successfully!')
            return redirect(url_for('profile'))
        return render_template('editprofile.html', title='Edit Account', form=form)
    

@app.route('/postthread/', methods=['GET', 'POST'])
def postthread():
    form = ThreadForm()
    if 'loggedin' in session:
        if form.validate_on_submit():
            title = form.title.data 
            lat = form.latitude.data
            long = form.longitude.data
            rid = form.rid.data
            target = form.target.data
            body = form.body.data
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute(
                'insert into project_schema.threads(title, locationlatitude, locationlongitude, recipientid, target) values(%s, %s, %s, %s, %s)', 
                (title, lat, long, rid, target)
            )
            conn.commit()
            cur.execute(
                'insert into project_schema.messages(threadid, authorid, timestamp, body) values((select max(threadid) from project_schema.threads), %s, CURRENT_TIMESTAMP, %s)',
                (session['id'], body)
            )
            conn.commit()
            cur.close()
            conn.close()
            flash('Post Successfully!')
            return redirect(url_for('index'))
        return render_template('post.html', form=form)

            
@app.route('/threads/', methods=['GET', 'POST'])
def threads():
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM project_schema.threads where recipientid=%s;',(session['id'],))
        threads = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('threads.html', userid = session['id'], username=session['username'], threads=threads)
    return redirect(url_for('login'))

@app.route('/messages/<id>', methods=['GET', 'POST'])
def messages(id):
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM project_schema.messages where threadid=%s;',(id,))
        m = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('messages.html', messages=m)
    return redirect(url_for('login'))

