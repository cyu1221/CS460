######################################
# author ben lawson <balawson@bu.edu>
# Edited by: Baichuan Zhou (baichuan@bu.edu) and Craig Einstein <einstein@bu.edu>
#
######################################
# Some code adapted from 
# CodeHandBook at http://codehandbook.org/python-web-application-development-using-flask-and-mysql/
# and MaxCountryMan at https://github.com/maxcountryman/flask-login/
# and Flask Offical Tutorial at  http://flask.pocoo.org/docs/0.10/patterns/fileuploads/
# see links for further understanding
###################################################
import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login


# for image uploading
from werkzeug import secure_filename
import os, base64, time, datetime, random

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'the string that you can not guess'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '19970224lin123'
app.config['MYSQL_DATABASE_DB'] = 'photoshare1'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

class User(flask_login.UserMixin):
    def __init__(self):
        self.username = "User"

class Anonymous(flask_login.AnonymousUserMixin):
    def __init__(self):
        self.username = 'Guest'


# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.user = User
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT email FROM User")
user = cursor.fetchall()


def getUserList():
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM User")
    return cursor.fetchall()





@login_manager.user_loader
def user_loader(email):
    user = getUserList()
    if not (email) or email not in str(user):
        return
    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    user = getUserList()
    email = request.form.get('email')
    if not (email) or email not in str(user):
        return
    user = User()
    user.id = email
    cursor = mysql.connect().cursor()
    cursor.execute("SELECT password FROM User WHERE email = '{0}'".format(email))
    data = cursor.fetchall()
    pwd = str(data[0][0])
    user.is_authenticated = request.form['password'] == pwd
    return user

def getUserNameFromEmail(email):
	cursor = conn.cursor()
	cursor.execute("SELECT fname, lname  FROM User WHERE email = '{0}'".format(email))
	T = cursor.fetchone()
	T = [str(item) for item in T]
	return T

'''
A new page looks like this:
@app.route('new_page_name')
def new_page_function():
	return new_page_html
'''


@app.route('/login', methods=['POST'])
def login():
    cursor = conn.cursor()
    email = flask.request.form.get('email')
    # check if email is registered
    if cursor.execute("SELECT password FROM User WHERE email = '{0}'".format(email)):
        data = cursor.fetchall()
        pwd = str(data[0][0])
        if flask.request.form['password'] == pwd:
            user = User()
            user.id = email
            flask_login.login_user(user)  # okay login in user
            return flask.redirect(flask.url_for('protected'))  # protected is a function defined in this file
    # information did not match
    return render_template('welcome.html', message='Sorry,email or password is wrong. Please try again, or create a account')


@app.route('/logout')
def logout():
    flask_login.logout_user()
    return render_template('welcome.html', message='Logged out')


@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template('unauth.html')


# you can specify specific methods (GET/POST) in function header instead of inside the functions as seen earlier
@app.route("/register", methods=['GET'])
def register():
    return render_template('register.html', supress='True')


@app.route("/register", methods=['POST'])
def register_user():
    try:
        email = request.form.get('email')
        password = request.form.get('password')
        fname = request.form.get('firstname')
        lname = request.form.get('lastname')
        hometown = request.form.get('hometown')
        gender = request.form.get('gender')
        DOB = request.form.get('birthday')
    except:
        print( "couldn't find all tokens")
        # this prints to shell, end users will not see this (all print statements go to shell)
        return flask.redirect(flask.url_for('register'))
    cursor = conn.cursor()
    test = isEmailUnique(email)
    if test:
        print(cursor.execute("INSERT INTO user (GENDER, EMAIL, PASSWORD, DOB, HOMETOWN, FNAME, LNAME) VALUES ('{0}', '{1}','{2}', '{3}', '{4}', '{5}', '{6}')".format(gender, email,password,DOB,hometown, fname, lname)))
        conn.commit()
        # log user in
        user = User()
        user.id = email
        flask_login.login_user(user)
        return render_template('welcome.html', name=email, message='Account Created!')
    else:
        print("couldn't find all tokens")
        return flask.redirect(flask.url_for('register'))


def getUserPhotos(uid):
    cursor = conn.cursor()
    cursor.execute("SELECT data, pid, caption FROM Photo WHERE uid = '{0}'".format(uid))
    return cursor.fetchall()  # NOTE list of tuples, [(imgdata, pid), ...]


def getUserIdFromEmail(email):
    cursor = conn.cursor()
    cursor.execute("SELECT uid  FROM User WHERE email = '{0}'".format(email))
    return cursor.fetchone()[0]

def getUserEmailFromId(id):
    cursor = conn.cursor()
    cursor.execute("SELECT email from user where uid = '{0}'".format(id))
    return cursor.fetchone()[0]

def isEmailUnique(email):
    # use this to check if a email has already been registered
    cursor = conn.cursor()
    if cursor.execute("SELECT email  FROM User WHERE email = '{0}'".format(email)):
        # this means there are greater than zero entries with that email
        return False
    else:
        return True


# end login code

'some basic function for later function'
def get_album_list_with_uid(userid):
    cursor= conn.cursor()
    cursor.execute("SELECT a.name From album a WHERE a.uid='{0}'".format(userid))
    list_of_album = cursor.fetchall()
    album = []
    while(len(list_of_album)>0):
        album+= list_of_album[0]
        list_of_album = list_of_album[1:]
    return album
    print ("get_album_list_with_uid active")
    print (album)
    '''return a list of album name '''

def get_album_id_with_aname_uid(aname,userid):
    cursor = conn.cursor()
    cursor.execute("SELECT aid FROM album WHERE name='{0}' AND uid='{1}'".format(aname,userid))
    list_id = cursor.fetchone()[0]
    return list_id
    ''' return the album id for given album name and user id '''

def friend_list(uid1):
    cursor = conn.cursor()
    cursor.execute("SELECT uid2 From friendship WHERE uid1 = '{0}'".format(uid1))
    friend_id = cursor.fetchall()
    print(friend_id)
    F = []
    for i in friend_id:
        cursor.execute("SELECT fname, lname FROM User WHERE uid = '{0}'".format(i[0]))
        F+=(cursor.fetchall())
    print(F)
    return F
    '''return a name list of user's friends'''

def user_activity():
    cursor = conn.cursor()
    cursor.execute("select uid from user")
    uid_list = [i[0] for i in cursor.fetchall()]
    score_result = []
    for uid in uid_list:
        cursor.execute("select pid from photo where uid = '{0}'".format(uid))
        pid_list = [i[0] for i in cursor.fetchall()]
        pid_number = len(pid_list)
        comments_number = 1
        for pid in pid_list:
            cursor.execute("select COUNT(*) from comment where pid = '{0}'".format(pid))
            comments_number += int(cursor.fetchone()[0])
        score_result.append((uid, comments_number*pid_number))
    score_result.sort(key = lambda x:x[1], reverse=True)
    result = list(map(lambda x:getUserEmailFromId(x[0]), score_result))
    f_name_l_name_result = list(map(lambda x:' '.join(getUserNameFromEmail(x)), result))
    return f_name_l_name_result
    
def friend_of_friend(uid):
    cursor=conn.cursor()
    cursor.execute("SELECT uid2 FROM friendship WHERE uid1='{0}'".format(uid))
    user_friend = [i[0] for i in cursor.fetchall()]
    friend_friends = []
    score_result = []
    for friend in user_friend:
        cursor.execute("SELECT uid2 FROM friendship WHERE uid1='{0}'".format(friend))
        friend_friends.append([i[0] for i in cursor.fetchall()])
    for i in friend_friends:
        for j in i:
            if j in user_friend:
                continue
            cursor.execute("SELECT uid2 FROM friendship WHERE uid1='{0}'".format(j))
            temp = [k[0] for k in cursor.fetchall()]
            score_result.append((j, len(set(user_friend)&set(temp))))
    score_result = score_result[:10]
    score_result.sort(key=lambda x:x[1], reverse=True)
    return_result = list(map(lambda x:getUserEmailFromId(x[0]), score_result))
    return list(set(return_result))
    ''' return a list of email that have most common friend'''

def num_like(pid):
    cursor=conn.cursor()
    cursor.execute("SELECT COUNT(uid) FROM liketable WHERE pid='{0}'".format(pid))
    num = cursor.fetchone()[0]
    return num
    ''' return a number of likes of a photo '''

def user_like(pid):
    cursor=conn.cursor()
    cursor.execute("SELECT u.email From user u WHERE u.uid= (SELECT uid FROM liketable WHERE pid='{0}')".format(pid))
    list = cursor.fetchall()
    return list
    ''' return a list of user email'''

def exist_tag():
    cursor=conn.cursor()
    cursor.execute("SELECT hashtag FROM tag")
    tags = cursor.fetchall()
    return tags
    '''return a list of exist tag'''

def popular_tag():
    cursor = conn.cursor()
    cursor.execute("SELECT hashtag From associate GROUP BY hashtag ORDER BY COUNT(pid) DESC LIMIT 10")
    tag_list = cursor.fetchall()
    return tag_list
    '''return a list of most popular tag'''

# tags are split base on comma
def split_tag(tags):
    u = str(tags)
    tag_list = u.split(',')
    return tag_list

def you_may_also_like():
    cursor = conn.cursor()
    cursor.execute("SELECT data from photo") 
    photo_datas = [i[0] for i in cursor.fetchall()]
    return photo_datas[:5]


@app.route("/profile", methods=['GET'])
@flask_login.login_required
def protected():
    email = flask_login.current_user.id
    uid = getUserIdFromEmail(email)
    friend_of_friends = friend_of_friend(uid)
    friends_id = [getUserIdFromEmail(i) for i in friend_of_friends]
    recommendedPhotos = you_may_also_like()
    return render_template('profile.html', name = email, albums=get_album_list_with_uid(uid), friends=friend_list(uid), friend_of_friends = friend_of_friends, friends_id = friends_id,\
        recommendedPhotos = recommendedPhotos)


# begin photo uploading code
# photos uploaded using base64 encoding so they can be directly embeded in HTML 
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/uploadfile/<album_name>', methods=['GET', 'POST'])
@flask_login.login_required
def upload_file(album_name):
    if request.method == 'POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        aid = get_album_id_with_aname_uid(album_name,uid)
        imgfile = request.files['photo']
        caption = request.form.get('caption')
        tag = request.form.get('word')
        photo_data = base64.standard_b64encode(imgfile.read())
        cursor = conn.cursor()
        cursor.execute("INSERT INTO photo (caption, data,aid,uid) VALUES ('{0}', '{1}', '{2}','{3}' )".format(caption, photo_data,aid,uid))
        conn.commit()
        query = "SELECT pid FROM photo where caption = '{0}' AND data = '{1}' AND aid = '{2}' AND uid = '{3}'".format(caption, photo_data,aid,uid)
        cursor.execute(query)
        pid_result = cursor.fetchall()
        all_tag = [i[0] for i in exist_tag()]
        if tag not in all_tag:
            create_tag(tag)
        cursor.execute("INSERT INTO associate (pid, hashtag) VALUES ('{0}','{1}')".format(pid_result[-1][0], tag))
        conn.commit()
        return render_template('profile.html', name=flask_login.current_user.id, message='Photo uploaded!',photos=getUserPhotos(uid))
    # The method is GET so we return a  HTML form to upload the a photo.
    else:
        return render_template('welcome.html')


# end photo uploading code



# create album function in profile.html
#Can we add album with same name for same user?
#assume not allow
@app.route('/create_album', methods=['GET','POST'])
@flask_login.login_required
def createalbum():
    if request.method == 'POST':
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        albumname = request.form.get('album_name')
        if albumname == " ":
            return flask.redirect(flask.url_for('protected'))
        created_albumn=get_album_list_with_uid(user_id)
        if albumname in created_albumn:
            return flask.redirect(flask.url_for('protected'))
        cursor.execute("INSERT INTO album(Name, uid) VALUES('{0}','{1}')".format(albumname, user_id))
        conn.commit()
        return flask.redirect(flask.url_for('protected'))
    else:
        return flask.redirect(flask.url_for('protected'))

# add friend function in profile.html
#cannot add himself, or already friends
@app.route('/results', methods = ['POST', 'GET'])
@flask_login.login_required
def results():
	if request.method == 'POST':
		friendsEmail = request.form.get('friendsEmail')
		credentials = getUserNameFromEmail(friendsEmail)
		friend_id = getUserIdFromEmail(friendsEmail)
		return render_template('profile.html', credentials=credentials, friend_id=friend_id)
	else:
		return flask.redirect(flask.url_for('protected'))

@app.route('/add_friend', methods = ['POST'])
@flask_login.login_required
def add_friend():
	friend_id = request.form.get('friend_id')
	user_id = getUserIdFromEmail(flask_login.current_user.id)
	cursor = conn.cursor()
	cursor.execute("INSERT INTO friendship (uid1, uid2) VALUES ('{0}', '{1}')".format(user_id, friend_id))
	conn.commit()
	return flask.redirect(flask.url_for('protected'))


# leaving comments function both register or visitor can leave comment
@app.route('/leaving_comments', methods=['GET', 'POST'])
def comments():
    pid = request.form.get('pid')
    if request.method=='POST':
        uid = getUserIdFromEmail(flask_login.current_user.id)
        string = request.form.get('comment')
        cursor=conn.cursor()
        cursor.execute("INSERT INTO comment(content,uid,pid) VALUES ('{0}','{1})','{2}')".format(string, uid,pid))
        conn.commit()
        return flask.redirect(flask.url_for('hello'))
    else:
        return flask.redirect(flask.url_for('hello'))

# like function for only register users
@app.route('/like', methods=['GET', 'POST'])
@flask_login.login_required
def like():
    pid = request.form.get('pid')
    if request.method=='POST':
        if flask_login.current_user.username == "Guest":
            return redirect(flask.url_for('hello'))
        uid = getUserIdFromEmail(flask_login.current_user.id)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO liketable(uid, pid) VALUES('{0}','{1}')".format(uid,pid))
        conn.commit()
        return flask.redirect(flask.url_for('hello'))
    else:
        return flask.redirect(flask.url_for('hello'))

# recommend friends for user
@app.route('/recommend_friend', methods=['GET','POST'])
@flask_login.login_required
def recommend_friend():
    return


# create tag
# not same tag allowed
# one tag each time
# tag start with #
# no deletion allowed after created
def create_tag(new_tag):
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tag (hashtag) VALUES('{0}')".format(new_tag))
    conn.commit()


#only user can add tag
@app.route('/add_tag',methods=['GET','POST'])
@flask_login.login_required
def add_tag_to_photo():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method=='POST':
        pid = request.values.get('pid')
        tag = request.form.get('word')
        all_tag = [i[0] for i in exist_tag()]
        cursor = conn.cursor()
        if tag not in all_tag:
            create_tag(tag)
        query = "SELECT hashtag from associate where pid = '{0}'".format(pid)
        cursor.execute(query)
        pid_tag_list = [i[0] for i in cursor.fetchall()]
        if tag in pid_tag_list:
            return flask.redirect(request.referrer, code=302)
        cursor.execute("INSERT INTO associate (pid, hashtag) VALUES ('{0}','{1}')".format(pid, tag))
        conn.commit()
        return flask.redirect(request.referrer, code=302)
    else:
        return flask.redirect(request.referrer, code=302)

# search from user album that contain this tag
# only one tag is allowed
@app.route('/search_myphoto_from_tag', methods=['GET','POST'])
@flask_login.login_required
def search_myphoto_by_tag():
    uid = getUserIdFromEmail(flask_login.current_user.id)
    if request.method =='POST':
        hashtag = request.form.get('search_tag')
        cursor=conn.cursor()
        cursor.execute("SELECT p.pid, p.data FROM photo p, associate a WHERE a.hashtag='{0}' AND p.pid = a.pid AND p.uid='{1}'".format(hashtag,uid))
        base_list = cursor.fetchall()
        pid_list = [i[0] for i in base_list]
        photos_data = [i[1] for i in base_list]
        username_list = []
        comments_list = []
        likes_list = []
        user_likes_list = []
        for pid in pid_list:
            cursor.execute("SELECT email FROM user WHERE uid IN (SELECT uid FROM photo WHERE pid = '{0}')".format(pid))
            username_list.append(cursor.fetchall()[0][0])
            cursor.execute("SELECT content, uid FROM comment where pid = '{0}' ORDER BY doc DESC".format(pid))
            temp_comments = []
            for i in cursor.fetchall():
                if getUserEmailFromId(i[1]) == "admin@my.com":
                    temp_comments.append("annoymous" + ":" + i[0])
                else:
                    temp_comments.append(getUserEmailFromId(i[1]) + ":" + i[0])
            #temp_comments = ["annoymous" + ":" +i[0] if  for i in cursor.fetchall()]
            comments_list.append(temp_comments)
            cursor.execute("SELECT uid from liketable where pid = '{0}'".format(pid))
            temp_user_likes = list(set([getUserEmailFromId(i[0]) for i in cursor.fetchall()]))
            likes_list.append(len(temp_user_likes))
            user_likes_list.append(temp_user_likes)
        return render_template('welcome.html', message = 'Here is photo', photos = photos_data, userNames = username_list, pid = pid_list, comments = comments_list, likes=likes_list, usersLiked=user_likes_list)
        #return render_template('profile.html', search_tags= photo_list)
    else:
        return render_template('welcome.html', message='No Photo Found')
        #return render_template('profile.html', message= 'No Photo Found')
# return a list of photo id

# search from all album, show in home page
@app.route('/search_allphoto_from_tag', methods=['GET', 'POST'])
# index out of range
def search_allphoto_by_tag():
    if request.method == 'POST':
        tags = request.form.get('search_tag')
        tag_list = split_tag(tags)
        long_list=[]
        while(len(tag_list)>0):
            hashtag = tag_list[0]
            tag_list = tag_list[1:]
            cursor = conn.cursor()
            cursor.execute("SELECT p.data, p.pid FROM photo p, associate a WHERE a.hashtag='{0}' AND p.pid = a.pid".format(hashtag))
            long_list += cursor.fetchall()
        photos_data = [i[0] for i in long_list]
        pid_list = [i[1] for i in long_list]
        username_list = []
        comments_list = []
        likes_list = []
        user_likes_list = []
        for pid in pid_list:
            cursor.execute("SELECT email FROM user WHERE uid IN (SELECT uid FROM photo WHERE pid = '{0}')".format(pid))
            username_list.append(cursor.fetchall()[0][0])
            cursor.execute("SELECT content, uid FROM comment where pid = '{0}' ORDER BY doc DESC".format(pid))
            temp_comments = []
            for i in cursor.fetchall():
                if getUserEmailFromId(i[1]) == "admin@my.com":
                    temp_comments.append("annoymous" + ":" + i[0])
                else:
                    temp_comments.append(getUserEmailFromId(i[1]) + ":" + i[0])
            #temp_comments = ["annoymous" + ":" +i[0] if  for i in cursor.fetchall()]
            comments_list.append(temp_comments)
            cursor.execute("SELECT uid from liketable where pid = '{0}'".format(pid))
            temp_user_likes = list(set([getUserEmailFromId(i[0]) for i in cursor.fetchall()]))
            likes_list.append(len(temp_user_likes))
            user_likes_list.append(temp_user_likes)
        return render_template('welcome.html', message = 'Here is photo', photos = photos_data, userNames = username_list, pid = pid_list, comments = comments_list, likes=likes_list, usersLiked=user_likes_list)
    else:
        return render_template('welcome.html', message='No Photo Found')

def getAllElementsInSencodList(firstList, secondList):
    list_c = [a for a in firstList if a in secondList]
    return list_c

def getIntersection(uinList):
    while (len(uinList) > 1):
        list_a = []
        list_b = []
        list_a = uinList.pop()
        list_b = uinList.pop()
        list_c = getAllElementsInSencodList(list_a, list_b)
        if len(list_c) > 0:
            uinList.append(list_c)
    return uinList[0]



@app.route("/photos/delete_album/<album_name>", methods=['GET','POST'])
@flask_login.login_required
def delete_album(album_name):
    if request.method =="GET":
        uid = getUserIdFromEmail(flask_login.current_user.id)
        aid = get_album_id_with_aname_uid(album_name, uid)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Album WHERE aid = '{0}'".format(aid))
        conn.commit()
        return render_template('welcome.html')
    else:
        return render_template('welcome.html')

@app.route("/photos/<album_name>", methods=['GET'])
@flask_login.login_required
def show_photos(album_name):
    user_id = getUserIdFromEmail(flask_login.current_user.id)
    a_id = get_album_id_with_aname_uid(album_name, user_id)
    cursor = conn.cursor()
    query = "SELECT data, pid FROM photo where uid = '{0}' AND aid = '{1}'".format(user_id, a_id)
    cursor.execute(query)
    base_result = cursor.fetchall()
    photo_data_list = []
    pid_list = []
    for element in base_result:
        photo_data_list.append(element[0])
        pid_list.append(element[1])
    tag_list = []
    for i in pid_list:
        query = "SELECT hashtag from associate where pid = '{0}'".format(i)
        cursor.execute(query)
        temp = cursor.fetchall()
        tag_list.append([i[0] for i in temp])
    return render_template('photos.html', album_name = album_name, message='Photo uploaded!', photos = photo_data_list, pids = pid_list, tags = tag_list)

@app.route("/upload/<album_name>", methods=['GET', 'POST'])
@flask_login.login_required
def upload_photos(album_name):
    return render_template("upload.html", album = album_name)

@app.route("/add_comment", methods=["POST"])
def add_comment():
    if flask_login.current_user.username == "Guest":
        user_id = getUserIdFromEmail("admin@my.com")
        comment = request.form.get("comment")
        pid = request.form.get("picture_id")
        timestamp = timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        cursor = conn.cursor()
        cursor.execute("SELECT uid from photo where pid = '{0}'".format(pid))
        query  = "INSERT INTO comment (uid, pid, doc, content) VALUES ('{0}', '{1}', '{2}', '{3}')".format(user_id, pid, timestamp, comment)
        cursor.execute(query)
        conn.commit()
    elif flask_login.current_user.username == "User":
        user_id = getUserIdFromEmail(flask_login.current_user.id)
        comment = request.form.get("comment")
        pid = request.form.get("picture_id")
        timestamp = timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
        cursor = conn.cursor()
        cursor.execute("SELECT uid from photo where pid = '{0}'".format(pid))
        if user_id == cursor.fetchall()[0][0]:
            return flask.redirect(flask.url_for('hello'))
            #return flask.redirect()
        query  = "INSERT INTO comment (uid, pid, doc, content) VALUES ('{0}', '{1}', '{2}', '{3}')".format(user_id, pid, timestamp, comment)
        cursor.execute(query)
        conn.commit()
    return flask.redirect(flask.url_for('hello'))


@app.route('/photos/tags/<tag_name>', methods=["GET", 'POST'])
@flask_login.login_required
def get_tag_picture(tag_name):
    cursor = conn.cursor()
    user_id = getUserIdFromEmail(flask_login.current_user.id)
    query = "SELECT p.pid FROM photo p, associate a WHERE a.hashtag='{0}' AND p.pid = a.pid AND p.uid='{1}'".format(tag_name, user_id)
    cursor.execute(query)
    pid_list = [i[0] for i in cursor.fetchall()]
    photo_data_list = []
    for pid in pid_list:
        query = "SELECT data FROM photo WHERE pid = '{0}'".format(pid)
        cursor.execute(query)
        photo_data_list.append(cursor.fetchone()[0])
    return render_template("photos.html", photos = photo_data_list, pids = pid_list)


def find_most_popular_tag():
    cursor = conn.cursor()
    query = "SELECT hashtag FROM associate GROUP BY  hashtag HAVING COUNT(hashtag) = ( SELECT COUNT(hashtag) as great from associate GROUP BY hashtag ORDER BY great desc limit 1)"
    cursor.execute(query)
    tag_list = [i[0] for i in cursor.fetchall()]
    return tag_list

@app.route("/public_tags/<tag_name>", methods=['GET', 'POST'])
def get_public_tag_picture(tag_name):
    if request.method == 'GET':
        cursor = conn.cursor()
        query = "SELECT pid from associate where hashtag = '{0}'".format(tag_name)
        cursor.execute(query)
        pid_list = [i[0] for i in cursor.fetchall()]
        photos_data = []
        for pid in pid_list:
            cursor.execute("SELECT data from photo where pid = '{0}'".format(pid))
            photos_data.append(cursor.fetchone()[0])
        username_list = []
        comments_list = []
        likes_list = []
        user_likes_list = []
        for pid in pid_list:
            cursor.execute("SELECT email FROM user WHERE uid IN (SELECT uid FROM photo WHERE pid = '{0}')".format(pid))
            username_list.append(cursor.fetchall()[0][0])
            cursor.execute("SELECT content, uid FROM comment where pid = '{0}' ORDER BY doc DESC".format(pid))
            temp_comments = []
            for i in cursor.fetchall():
                if getUserEmailFromId(i[1]) == "admin@my.com":
                    temp_comments.append("annoymous" + ":" + i[0])
                else:
                    temp_comments.append(getUserEmailFromId(i[1]) + ":" + i[0])
            #temp_comments = ["annoymous" + ":" +i[0] if  for i in cursor.fetchall()]
            comments_list.append(temp_comments)
            cursor.execute("SELECT uid from liketable where pid = '{0}'".format(pid))
            temp_user_likes = list(set([getUserEmailFromId(i[0]) for i in cursor.fetchall()]))
            likes_list.append(len(temp_user_likes))
            user_likes_list.append(temp_user_likes)
        return render_template('welcome.html', message = 'Here is photo', photos = photos_data, userNames = username_list, pid = pid_list, comments = comments_list, likes=likes_list, usersLiked=user_likes_list)
    else:
        return render_template('welcome.html', message='No Photo Found')

@app.route("/photo_search_by_tags", methods=['GET','POST'])
def photo_search_by_tags():
    if request.method == 'POST':
        cursor = conn.cursor()
        search_tags = request.form.get('search_tag').split(" ")
        pid_lists = []
        for tag in search_tags:
            query = "SELECT pid from associate where hashtag = '{0}'".format(tag)
            cursor.execute(query)
            pid_lists.append([i[0] for i in cursor.fetchall()])
        pid_list = list(reduce(lambda x,y:set(x)&set(y), pid_lists))
        photos_data = []
        for pid in pid_list:
            cursor.execute("SELECT data from photo where pid = '{0}'".format(pid))
            photos_data.append(cursor.fetchone()[0])
        username_list = []
        comments_list = []
        likes_list = []
        user_likes_list = []
        for pid in pid_list:
            cursor.execute("SELECT email FROM user WHERE uid IN (SELECT uid FROM photo WHERE pid = '{0}')".format(pid))
            username_list.append(cursor.fetchall()[0][0])
            cursor.execute("SELECT content, uid FROM comment where pid = '{0}' ORDER BY doc DESC".format(pid))
            temp_comments = []
            for i in cursor.fetchall():
                if getUserEmailFromId(i[1]) == "admin@my.com":
                    temp_comments.append("annoymous" + ":" + i[0])
                else:
                    temp_comments.append(getUserEmailFromId(i[1]) + ":" + i[0])
            #temp_comments = ["annoymous" + ":" +i[0] if  for i in cursor.fetchall()]
            comments_list.append(temp_comments)
            cursor.execute("SELECT uid from liketable where pid = '{0}'".format(pid))
            temp_user_likes = list(set([getUserEmailFromId(i[0]) for i in cursor.fetchall()]))
            likes_list.append(len(temp_user_likes))
            user_likes_list.append(temp_user_likes)
        return render_template('welcome.html', message = 'Here is photo', photos = photos_data, userNames = username_list, pid = pid_list, comments = comments_list, likes=likes_list, usersLiked=user_likes_list)
    else:
        return render_template('welcome.html', message='No Photo Found')

@app.route("/search_by_comment", methods=['GET', 'POST'])
def search_by_comment():
    if request.method == 'POST':
        comment = request.form.get("tag_name")
        cursor = conn.cursor()
        query = "SELECT uid from comment where content = '{0}'".format(comment)
        cursor.execute(query)
        user_list = [getUserEmailFromId(i[0]) for i in cursor.fetchall()]
        return render_template("user.html", userlists = user_list)
    else:
        return render_template('welcome.html', message='No user Found')

@app.route("/add_like", methods=['GET', 'POST'])
@flask_login.login_required
def add_like():
    cursor = conn.cursor()
    pid = request.values.get("picture_id")
    user_id = getUserIdFromEmail(flask_login.current_user.id)
    timestamp = timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')
    query = "INSERT INTO liketable (uid, pid, doc) VALUES ('{0}', '{1}', '{2}')".format(user_id, pid, timestamp)
    cursor.execute(query)
    conn.commit()
    return flask.redirect(flask.url_for('hello'))


@app.route("/showphotos", methods=['GET'])
def showPhotos():
    photo_path = '/static/1.jpg'
    return render_template("testshowphoto.html", photopath = photo_path)

@app.route("/delete_photo", methods=["POST"])
@flask_login.login_required
def delete_photo():
    pid = request.form.get("pid")
    cursor = conn.cursor()
    query = "delete from photo where pid = '{0}'".format(pid)
    cursor.execute(query)
    conn.commit()
    return flask.redirect(request.referrer, code=302)

# default page
@app.route('/', methods=['GET'])
def hello():
    tag_list = find_most_popular_tag()
    activeUsers = user_activity()
    return render_template('welcome.html', message='Welecome to Photoshare', mostPopularTags=tag_list, activeUsers=activeUsers)


if __name__ == "__main__":
    # this is invoked when in the shell  you run
    # $ python app.py
    app.run(port=5000, debug=True)
