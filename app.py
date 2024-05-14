import os
import psycopg2
from flask import Flask, render_template, request, url_for, redirect, session, flash
from wtforms import StringField, PasswordField, SubmitField, DateField, SelectField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from forms import SignUpForm, EditForm, ThreadForm, ReplyForm, BlockForm, SearchBar, FriendRequestForm
from utils import is_number

app = Flask(__name__)
app.secret_key = 'yoursecretkey'

# Get connection from database
def get_db_connection():
    conn = psycopg2.connect(host='localhost',
                            database='postgres',
                            user='postgres',
                            password='jason123')
    return conn

# Login
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
            'SELECT * FROM project_schema.users WHERE username = %s AND password = %s;', 
            (username, password,)
        )
        # Fetch one record and return result
        account = cur.fetchone()
        cur.close()
        conn.close()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session.permanent=False
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            conn = get_db_connection()
            cur = conn.cursor()
            # Fetch last login time
            cur.execute(
                'select lastaccesstimestamp from project_schema.useractivity where userid=%s;', 
                (session['id'],)
            )
            lastlogintime = cur.fetchone()
            
            # If it is user's first time login, log the current time and use it as last login time
            if not lastlogintime:
                cur.execute(
                    'insert into project_schema.useractivity(userid, lastaccesstimestamp) values(%s, CURRENT_TIMESTAMP);', 
                    (session['id'],)
                )
                conn.commit()
                cur.execute(
                    'select lastaccesstimestamp from project_schema.useractivity where userid=%s;', 
                    (session['id'],)
                )
                lastlogintime = cur.fetchone()
            # Else: fetch last login time and update 
            session['lastlogintime']=lastlogintime[0]
            # Update login time
            cur.execute(
                'insert into project_schema.useractivity(userid, lastaccesstimestamp) values(%s, CURRENT_TIMESTAMP) on conflict(userid) do update set lastaccesstimestamp=CURRENT_TIMESTAMP;', 
                (session['id'],)
            )
            conn.commit()
            cur.close()
            conn.close()
            # Redirect to home page
            return redirect(url_for('index'))
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('login.html', msg=msg)

# Register a new account
@app.route('/register/', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    form = SignUpForm()
    #Submit register form
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        confirm = form.confirm.data
        address = form.address.data
        latitude = form.latitude.data
        longitude = form.longitude.data
        profile = form.profile.data
        #Check if input is valid
        if password==confirm and is_number(latitude) and is_number(longitude):
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute('SELECT * FROM project_schema.users WHERE username = %s;', (username,))
            account = cur.fetchone()
            if account:
                msg = 'Account already exists!'
            else:
                # Account doesn't exist, and the form data is valid, so insert the new account into the accounts table
                cur.execute(
                    'INSERT INTO project_schema.users(userid, username, password, address, latitude, longitude, profile) VALUES ((select max(userid)+1 from project_schema.users), %s, %s, %s, %s, %s, %s);',
                    (username, password, address, latitude, longitude, profile,)
                )
                conn.commit()
                cur.close()
                conn.close()
                msg = 'You have successfully registered!'
                return redirect(url_for('login'))
        else:
            msg = 'Invalid Input!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'   
        
    # Show registration form with message (if any)
    
    return render_template('register.html', msg=msg, form=form)

# Logout
@app.route('/logout/')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))

# Home Page
@app.route('/index/')
def index():
    if 'loggedin' in session:
        return render_template('index.html', userid = session['id'], username=session['username'])
    return redirect(url_for('login'))

# My Profile
@app.route('/profile/')
def profile():
    #Fetch user profile if logged in
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM project_schema.users where userid=%s;',
            (session['id'],)
        )
        profile = cur.fetchone()
        # Fetch login time
        cur.execute(
            'SELECT * FROM project_schema.useractivity where userid=%s;',
            (session['id'],)
        )
        logintime = cur.fetchone()
        cur.close()
        conn.close()
        return render_template('profile.html', profile=profile, logintime=logintime)
    return redirect(url_for('login'))

# Editing profile
@app.route('/editprofile/', methods=['GET', 'POST'])
def editprofile():
    msg=''
    if 'loggedin' in session:
        form = EditForm()
        if request.method=='POST':
            print('check data and submit')
        else:
            #Fetch user profile to put in form
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
            #update profile if input is valid
            lat=form.latitude.data
            long=form.longitude.data
            if is_number(lat) and is_number(long):
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
            else:
                msg = 'Invalid Input!'
        elif request.method == 'POST':
            msg='Invalid Input!'
        return render_template('editprofile.html', title='Edit Account', form=form, msg=msg)

# Posting threads
@app.route('/postthread/', methods=['GET', 'POST'])
def postthread():
    #Insert into both thread and message table
    msg=''
    form = ThreadForm()
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT userid2, username FROM project_schema.userfriends uf, project_schema.users u where uf.userid2=u.userid and uf.userid1=%s;",
            (session['id'],))
        friends=cur.fetchall()
        cur.execute(
            "SELECT userid2, username FROM project_schema.userneighbors uf, project_schema.users u where uf.userid2=u.userid and uf.userid1=%s;",
            (session['id'],))
        neighbors=cur.fetchall()
        cur.execute(
            'SELECT b.blockid, b.name FROM project_schema.userblocks ub, project_schema.blocks b WHERE ub.blockid = b.blockid and userid=%s and isjoined=true;',
            (session['id'],)
        )
        blocks = cur.fetchall()
        cur.execute(
            'SELECT n.neighborhoodid, name FROM (select userid, neighborhoodid from project_schema.userblocks ub, project_schema.blocks b WHERE ub.blockid = b.blockid and userid=%s and isjoined=true) un, project_schema.neighborhoods n where un.neighborhoodid=n.neighborhoodid;',
            (session['id'],)
        )
        hoods = cur.fetchall()
        targets=[('friend,'+str(b[0]), 'Friend:'+str(b[0])+' '+b[1]) for b in friends]+[('neighbor,'+str(b[0]), 'Neighbor:'+str(b[0])+' '+b[1]) for b in neighbors]+[('block,'+str(b[0]), 'Block:'+str(b[0])+' '+b[1]) for b in blocks]+[('hood,'+str(b[0]), 'Neighborhood:'+str(b[0])+' '+b[1]) for b in hoods]
        form.target.choices=targets
        if form.validate_on_submit():
            title = form.title.data 
            lat = form.latitude.data
            long = form.longitude.data
            targetandid=form.target.data
            target = targetandid.split(',')[0]
            rid = int(targetandid.split(',')[1])
            
            body = form.body.data
            conn = get_db_connection()
            cur = conn.cursor()
            #Check if recipient is valid
            cur.execute(
                    "SELECT * FROM project_schema.userblocks where blockid=%s and userid=%s and isjoined=true;",
                    (rid, session['id'],))
            joinedblock = cur.fetchone()
            cur.execute(
                    "SELECT * FROM (select * from project_schema.userblocks where isjoined=true) ub, project_schema.blocks b where b.blockid=ub.blockid and neighborhoodid = %s and userid=%s;",
                    (rid, session['id'],))
            joinedhood = cur.fetchone()
            cur.execute(
                    "SELECT * FROM project_schema.userfriends where userid1 = %s and userid2=%s;",
                    (rid, session['id'],))
            isfriend = cur.fetchone()
            cur.execute(
                    "SELECT * FROM project_schema.userneighbors where userid1 = %s and userid2=%s;",
                    (rid, session['id'],))
            isneighbor = cur.fetchone()

            if target=='block' and not joinedblock:
                msg="You're not joined in this block!"
            elif target=='hood' and not joinedhood:
                msg="You're not joined in this hood!"
            elif target=='friend' and not isfriend:
                msg="You're not friend with this user!"
            elif target=='neighbor' and not isneighbor:
                msg="You're not neighbor with this user!"
            elif not is_number(lat) or not is_number(long):
                msg='Invalid location'
            
            else:
                # The recipient is valid, insert thread and the initial message
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
                return redirect(url_for('threads', source='my'))
        elif request.method == 'POST':
            msg='invalid post'    
        return render_template('post.html', form=form, msg=msg, username=session['username'])

# Threads
@app.route('/threads/<source>', methods=['GET', 'POST'])
def threads(source):
    # Search bar
    form=SearchBar()
    threads=[]
    msg=''
    # blank keyword
    keyword='%%'
    # Fetch threads
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        # Get keyword from search bar
        if form.validate_on_submit():
            keyword='%'+str(form.keyword.data)+'%'
        # All recieved threads
        if source=='all':
            # Personal threads
            cur.execute("SELECT * FROM project_schema.threads t where recipientid=%s and (target='friend' or target='neighbor') and (title ILIKE %s or exists(select * from project_schema.messages m where t.threadid = m.threadid and m.body ILIKE %s));"
                        ,(session['id'], keyword, keyword,))
            threads = cur.fetchall()
            # Block threads
            cur.execute(
                "SELECT * FROM project_schema.threads t, project_schema.userblocks ub where t.recipientid=ub.blockid and userid=%s and target='block' and (title ILIKE %s or exists(select * from project_schema.messages m where t.threadid = m.threadid and m.body ILIKE %s));"
                ,(session['id'], keyword, keyword,)
            )
            bthreads = cur.fetchall()
            # Neighborhood threads
            cur.execute(
                "SELECT * FROM project_schema.threads t, (select ub.userid, neighborhoodid from project_schema.userblocks ub, project_schema.blocks b where ub.blockid=b.blockid and ub.isjoined=true) un where t.recipientid=un.neighborhoodid and userid=%s and target='hood' and (title ILIKE %s or exists(select * from project_schema.messages m where t.threadid = m.threadid and m.body ILIKE %s));"
                ,(session['id'], keyword, keyword,)
            )
            nthreads = cur.fetchall()
            threads=threads+bthreads+nthreads
        # All new recieved threads
        elif source=='new':
            lastlogintime = str(session['lastlogintime'])
            # Personal threads
            cur.execute(
                "SELECT * FROM project_schema.threads t where t.recipientid=%s and (target='friend' or target='neighbor') and exists(select * from project_schema.messages m where m.threadid=t.threadid and m.timestamp>%s) and (title ILIKE %s or exists(select * from project_schema.messages m where t.threadid = m.threadid and m.body ILIKE %s));"
                ,(session['id'], lastlogintime, keyword, keyword,))
            threads = cur.fetchall()
            # Block threads
            cur.execute(
                'SELECT * FROM project_schema.threads t, project_schema.userblocks ub where t.recipientid=ub.blockid and userid=%s and target=%s and exists(select * from project_schema.messages m where m.threadid=t.threadid and m.timestamp>%s) and (title ILIKE %s or exists(select * from project_schema.messages m where t.threadid = m.threadid and m.body ILIKE %s));'
                ,(session['id'], 'block', lastlogintime, keyword, keyword,)
            )
            bthreads = cur.fetchall()
            # Neighborhood threads
            cur.execute(
                "SELECT * FROM project_schema.threads t, (select ub.userid, neighborhoodid from project_schema.userblocks ub, project_schema.blocks b where ub.blockid=b.blockid and ub.isjoined=true) un where t.recipientid=un.neighborhoodid and userid=%s and target='hood' and exists(select * from project_schema.messages m where m.threadid=t.threadid and m.timestamp>%s) and (title ILIKE %s or exists(select * from project_schema.messages m where t.threadid = m.threadid and m.body ILIKE %s));"
                ,(session['id'], lastlogintime, keyword, keyword,)
            )
            nthreads = cur.fetchall()
            threads=threads+bthreads+nthreads
            msg=str(len(threads))+' threads with messages after '+ lastlogintime
            
        # All threads that user has left messages in
        elif source=='my':
            cur.execute('SELECT * FROM project_schema.threads t where exists(select * from project_schema.messages m where t.threadid = m.threadid and m.authorid=%s) and (title ILIKE %s or exists(select * from project_schema.messages m where t.threadid = m.threadid and m.body ILIKE %s));'
                        ,(session['id'], keyword, keyword,))
            threads = cur.fetchall() 
        # Friend threads       
        elif source=='friend':
            cur.execute("SELECT * FROM project_schema.threads t where recipientid=%s and target=%s and (title ILIKE %s or exists(select * from project_schema.messages m where t.threadid = m.threadid and m.body ILIKE %s))"
                        ,(session['id'], source, keyword, keyword,))
            threads = cur.fetchall()
        # Neighbor Threads
        elif source=='neighbor':
            cur.execute("SELECT * FROM project_schema.threads t where recipientid=%s and target=%s and (title ILIKE %s or exists(select * from project_schema.messages m where t.threadid = m.threadid and m.body ILIKE %s))"
                        ,(session['id'], source, keyword, keyword,))
            threads = cur.fetchall()
        # Block threads
        elif source=='block':
            cur.execute(
                "SELECT * FROM project_schema.threads t, project_schema.userblocks ub where t.recipientid=ub.blockid and userid=%s and target=%s and (title ILIKE %s or exists(select * from project_schema.messages m where t.threadid = m.threadid and m.body ILIKE %s));"
                ,(session['id'], source, keyword, keyword,)
            )
            threads = cur.fetchall()
        # Neighborhood threads
        elif source=='hood':
            cur.execute(
                "SELECT * FROM project_schema.threads t, (select ub.userid, neighborhoodid from project_schema.userblocks ub, project_schema.blocks b where ub.blockid=b.blockid and ub.isjoined=true) un where t.recipientid=un.neighborhoodid and userid=%s and target=%s and (title ILIKE %s or exists(select * from project_schema.messages m where t.threadid = m.threadid and m.body ILIKE %s));"
                ,(session['id'], source, keyword, keyword,)
            )
            threads = cur.fetchall()
            
        cur.close()
        conn.close()
        return render_template('threads.html', userid = session['id'], username=session['username'], msg=msg, threads=threads, form=form)
    return redirect(url_for('login'))

@app.route('/messages/<id>/<target>', methods=['GET', 'POST'])
def messages(id, target):
    msg=''
    # Fetch messages from threads with id, and reply
    form = ReplyForm()
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        # Fetch all messages from thread with id
        cur.execute('SELECT * FROM project_schema.messages m, project_schema.users u where m.authorid = u.userid and threadid=%s order by timestamp asc;',(id,))
        m = cur.fetchall()
        # Reply
        if form.validate_on_submit():
            cur.execute(
                'insert into project_schema.messages(threadid, authorid, timestamp, body) values(%s, %s, CURRENT_TIMESTAMP, %s)',
                (id, session['id'], form.body.data)
            )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('messages', id=id, target=target))
        # Check if thread's target is block (can/cannot reply)
        if target=='block':
            cur.execute(
                'SELECT * FROM project_schema.userblocks where blockid = (select recipientid from project_schema.threads where threadid=%s) and userid=%s and isjoined=true;',
                (id, session['id'],))
            isjoin = cur.fetchone()
            if isjoin:
                # Render template with reply form
                return render_template('messages.html', messages=m, form=form, msg=msg, username=session['username'])
            else:
                # Render template without reply form
                msg='Only joined member can reply to this thread.'
                return render_template('messagesnoreply.html', messages=m, msg=msg)
        # User can reply to any other messages
        else:
            return render_template('messages.html', messages=m, form=form, msg=msg, username=session['username'])
    return redirect(url_for('login'))

# Show user's joined and followed block
@app.route('/blocks/', methods=['GET', 'POST'])
def blocks():
    if 'loggedin' in session:
        conn = get_db_connection()
        cur = conn.cursor()
        #Fetch joined block
        cur.execute(
            'SELECT b.blockid, b.name FROM project_schema.userblocks ub, project_schema.blocks b WHERE ub.blockid = b.blockid and userid=%s and isjoined=true;',
            (session['id'],)
        )
        jb = cur.fetchall()
        #Fetch joined hood
        cur.execute(
            'SELECT n.neighborhoodid, name FROM (select userid, neighborhoodid from project_schema.userblocks ub, project_schema.blocks b WHERE ub.blockid = b.blockid and userid=%s and isjoined=true) un, project_schema.neighborhoods n where un.neighborhoodid=n.neighborhoodid;',
            (session['id'],)
        )
        hood = cur.fetchall()
        #Fetch followed block
        cur.execute(
            'SELECT b.blockid, b.name FROM project_schema.userblocks ub, project_schema.blocks b WHERE ub.blockid = b.blockid and userid=%s and isjoined=false;',
            (session['id'],)
        )
        fb = cur.fetchall()
        #Fetch Requested block
        cur.execute(
            'SELECT blockid, approvedcount from project_schema.blockrequests where senderid=%s;',
            (session['id'],)
        )
        requests = cur.fetchall()
        cur.close()
        conn.close()
        return render_template('blocks.html', joinedblock=jb, followedblock=fb,hood=hood, requests=requests)
    return redirect(url_for('login'))

# Send a join block request or follow a block
@app.route('/joinblocks/', methods=['GET', 'POST'])
def joinblocks():
    msg = ''
    form = BlockForm()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM project_schema.blocks order by blockid;')
    blocks=cur.fetchall()
    cur.close()
    conn.close()
    #Get block name and id
    blocklist=[(b[0], b[1]) for b in blocks]
    form.blockid.choices=blocklist
    if form.validate_on_submit():
        blockid = form.blockid.data
        join=form.join.data
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM project_schema.userblocks where userid=%s and isjoined=true;', (session['id'],))
        joined=cur.fetchone()
        cur.execute('SELECT * FROM project_schema.userblocks where userid=%s and blockid=%s;', (session['id'], blockid))
        followedorjoined=cur.fetchone()
        cur.execute('SELECT * FROM project_schema.blockrequests where senderid=%s and blockid=%s;', (session['id'], blockid))
        request=cur.fetchone()
        cur.close()
        conn.close()
        #Check if user has joined a block
        if joined and join=='true':
            msg='Already joined a block!'
        #Check if the target block is already followed or joined
        elif followedorjoined:
            msg='Block already followed or joined!'
        #Check if request is sent
        elif request and join=='true':
            msg='Already sent a request!'
        
        #Insert to blockrequests for join/ Insert to userblocks for follow
        else:
            conn = get_db_connection()
            cur = conn.cursor()
            if join=='true':
                #Insert into blockrequests if join block
                cur.execute(
                    'INSERT INTO project_schema.blockrequests(requestid, senderid, blockid, approvedcount) VALUES ((select max(requestid)+1 from project_schema.blockrequests), %s, %s, 0)',
                    (session['id'], blockid)
                )
            else:
                #Insert into userblocks if follow block(no need to wait for approve)
                cur.execute(
                    'INSERT INTO project_schema.userblocks(userid, blockid, isjoined) VALUES (%s, %s, %s);',
                    (session['id'], blockid, join)
                )
            conn.commit()
            cur.close()
            conn.close()
            return redirect(url_for('blocks'))
    elif request.method == 'POST':
            msg='Invalid request!'
    return render_template('joinblocks.html', msg=msg, form=form)

# View the requests for joining user's joined block
@app.route('/viewrequests/', methods=['GET', 'POST'])
def viewrequests():
    #view requests for user's joined block
    msg=''
    conn = get_db_connection()
    cur = conn.cursor()
    #get the user's joined block
    cur.execute('SELECT blockid FROM project_schema.userblocks where userid=%s and isjoined=true;',(session['id'],))
    userblock = cur.fetchone()
    #Fetch the requests if user did joined a block, else redirect to blocks page
    if userblock:
        cur.execute(
            'SELECT * FROM project_schema.blockrequests br where blockid=%s and approvedcount<3 and not exists(select * from project_schema.requestapprovals r where approverid=%s and r.requestid=br.requestid);'
            ,(userblock[0], session['id'],)
        )
        requests = cur.fetchall()
    else:
        return redirect(url_for('blocks'))
    cur.close()
    conn.close()
    return render_template('viewrequests.html', msg=msg, requests=requests)

# Approve a request
@app.route('/approverequests/<id>')
def approverequests(id):
    msg=''
    conn = get_db_connection()
    cur = conn.cursor()
    #Check if user have approved this request before
    cur.execute('SELECT * FROM project_schema.requestapprovals where approverid=%s and requestid=%s;',(session['id'], id,))
    approval = cur.fetchone()
    if approval:
        msg='Already approved'
    else:
        #Insert approval record
        cur.execute(
            'INSERT INTO project_schema.requestapprovals(approvalid, requestid, approverid) VALUES ((select max(approvalid)+1 from project_schema.requestapprovals), %s, %s);',
            (id, session['id'],)
        )
        conn.commit()
        #Fetch the details of this request
        cur.execute('SELECT * from project_schema.blockrequests where requestid=%s;', (id,))
        r=cur.fetchone()
        senderid = r[1]
        blockid = r[2]
        approvalcount=r[3]
        
        if approvalcount==2:
            #If approvedcount reaches 3: 1. Insert sender to userblock with isjoined=true or 2. change to join if already followed the block
            cur.execute(
                    'INSERT INTO project_schema.userblocks(userid, blockid, isjoined) VALUES (%s, %s, true) on conflict(userid, blockid) do update set isjoined=true;',
                    (senderid, blockid,)
            )
            conn.commit()
        #Update approvedcount
        cur.execute('UPDATE project_schema.blockrequests SET approvedcount=approvedcount+1 where requestid=%s;', (id,))
        conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('viewrequests', msg=msg))

# Show user's friends
@app.route('/friends/', methods=['GET', 'POST'])
def friends():
    if 'loggedin' in session:
        msg=''
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT u.userid, username FROM project_schema.userfriends uf, project_schema.users u where uf.userid2=u.userid and userid1=%s;"
            ,(session['id'],)
        )
        friends=cur.fetchall()
        cur.close()
        conn.close()
        return render_template('friends.html', friends=friends, msg=msg)
    return redirect(url_for('login'))

# Send a friend requests
@app.route('/sendfriendrequest/', methods=['GET', 'POST'])
def sendfriendrequest():
    msg=''
    form=FriendRequestForm()
    
    conn = get_db_connection()
    cur = conn.cursor()
    # Fetch users that are not friend
    cur.execute("SELECT userid, username FROM project_schema.users u where not exists(select * from project_schema.friendrequests f where ((u.userid=f.receiverid and senderid=%s) or (u.userid=f.senderid and receiverid=%s)) and f.requeststatus!='rejected') and not exists(select * from project_schema.userfriends uf where u.userid=userid1 and userid2=%s) and u.userid!=%s ORDER BY u.userid;"
                ,(session['id'], session['id'], session['id'], session['id'], ))
    notfriend=cur.fetchall()
    # Fetch user's previous requests
    cur.execute("SELECT receiverid, requeststatus from project_schema.friendrequests where senderid=%s"
                ,(session['id'],))
    myrequests=cur.fetchall()
    cur.close()
    conn.close()
    
    # Get user id and name for form
    users=[(b[0], str(b[0])+' '+b[1]) for b in notfriend]
    form.users.choices=users
    
    #Insert into friend request if valid
    if form.validate_on_submit():
        userid = form.users.data
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO project_schema.friendrequests(senderid, receiverid, requeststatus) VALUES (%s, %s, 'pending')", (session['id'],userid,))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('sendfriendrequest'))
    elif request.method == 'POST':
            msg='Invalid request'
    return render_template('sendfriendrequest.html', form=form, myrequests=myrequests, msg=msg)

# View received friend requests
@app.route('/viewfriendrequest/', methods=['GET', 'POST'])
def viewfriendrequest():
    msg=''
    conn = get_db_connection()
    cur = conn.cursor()
    # View only pending requests
    cur.execute("select f.requestid, u.userid, username from project_schema.users u, project_schema.friendrequests f where u.userid=f.senderid and f.receiverid=%s and f.requeststatus='pending';"
                ,(session['id'],))
    friendrequests=cur.fetchall()
    msg="You have "+str(len(friendrequests))+" friend request(s)"
    cur.close()
    conn.close()
    
    return render_template('viewfriendrequest.html', requests=friendrequests, msg=msg)

# Respond to a friend request
@app.route('/respond/<id>/<respond>/', methods=['GET', 'POST'])
def respond(id, respond):
    conn = get_db_connection()
    cur = conn.cursor()
    # Accept
    if respond=='accept':
        cur.execute(
            'INSERT INTO project_schema.userfriends(userid1, userid2) VALUES ((select senderid from project_schema.friendrequests where requestid=%s), (select receiverid from project_schema.friendrequests where requestid=%s));',
            (id, id,)
        )
        conn.commit()
        cur.execute(
            'INSERT INTO project_schema.userfriends(userid1, userid2) VALUES ((select receiverid from project_schema.friendrequests where requestid=%s), (select senderid from project_schema.friendrequests where requestid=%s));',
            (id, id,)
        )
        conn.commit()
        cur.execute(
            "update project_schema.friendrequests set requeststatus='accepted' where requestid=%s",
            (id,)
        )
        conn.commit()
    # Reject
    else:
        cur.execute(
            "update project_schema.friendrequests set requeststatus='rejected' where requestid=%s",
            (id, session['id'],)
        )
        conn.commit()
        
    cur.close()
    conn.close()
    return redirect(url_for('viewfriendrequest'))

# View user's neighbors
@app.route('/neighbors/', methods=['GET', 'POST'])
def neighbors():
    if 'loggedin' in session:
        msg=''
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT u.userid, username FROM project_schema.userneighbors un, project_schema.users u where un.userid2=u.userid and userid1=%s;"
            ,(session['id'],)
        )
        neighbors=cur.fetchall()
        cur.close()
        conn.close()
        return render_template('neighbors.html', neighbors=neighbors, msg=msg)
    return redirect(url_for('login'))

# Adding a user(block member) as neighbor 
@app.route('/addneighbor/', methods=['GET', 'POST'])
def addneighbor():
    msg=''
    form=FriendRequestForm()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT u.userid, u.username, blockid FROM project_schema.users u, project_schema.userblocks ub where u.userid=ub.userid and ub.isjoined=true and not exists(select * from project_schema.userneighbors un where u.userid=userid1 and userid2=%s) and (ub.blockid=(select blockid from project_schema.userblocks where userid=%s and isjoined=true)) and u.userid!=%s ORDER BY u.userid;"
                ,(session['id'], session['id'], session['id'],))
    notneighbor=cur.fetchall()
    users=[(b[0], str(b[0])+' '+b[1]) for b in notneighbor]
    form.users.choices=users
    if form.validate_on_submit():
        userid = form.users.data
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO project_schema.userneighbors(userid1, userid2) VALUES (%s, %s)", (session['id'],userid,))
        conn.commit()
        cur.execute("INSERT INTO project_schema.userneighbors(userid1, userid2) VALUES (%s, %s)", (userid, session['id'],))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('neighbors'))
    elif request.method == 'POST':
            msg='invalid post'
    return render_template('addneighbor.html', form=form, msg=msg)
    
# View other user's profile
@app.route('/viewprofile/<id>', methods=['GET'])
def viewprofile(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
            'SELECT * FROM project_schema.users where userid=%s;',
            (id,)
    )
    # Profile
    profile = cur.fetchone()
    cur.execute(
            'SELECT * FROM project_schema.useractivity where userid=%s;',
            (id,)
    )
    # Login
    logintime = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('viewprofile.html', profile=profile, logintime=logintime)

@app.route('/about/')
def about():
    return render_template('about.html')