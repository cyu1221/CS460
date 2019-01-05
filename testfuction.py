import flask
from flask import Flask, Response, request, render_template, redirect, url_for
from flaskext.mysql import MySQL
import flask.ext.login as flask_login


# for image uploading
from werkzeug import secure_filename
import os, base64

mysql = MySQL()
app = Flask(__name__)
app.secret_key = 'super secret string'  # Change this!

# These will need to be changed according to your creditionals
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = '19970224lin123'
app.config['MYSQL_DATABASE_DB'] = 'photoshare1'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# begin code used for login
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

conn = mysql.connect()
cursor = conn.cursor()
cursor.execute("SELECT u.uid, u.email FROM user u")
R = cursor.fetchall()
for x in range(0, len(R)):
    S= (R[x],x)
    print S
print(R[2])
cursor.execute("SELECT uid  FROM user WHERE email='{0}'".format('71@bu.edu'))
T = cursor.fetchone()[0]
print(T)

cursor.execute("SELECT u.uid  FROM user u, album a WHERE a.uid=u.uid")
T1 = cursor.fetchone()
print T1


if '{'or'}' in "{acccc@}":
    print("HHH")
else:
    print('not found')

cursor.execute("SELECT COUNT(uid)  FROM user")
t2 = cursor.fetchone()[0]
print t2

list1=('fff','666','233','ntr')
list2=('34f','666','66234','ntt')

print [l for l in list1 if l in list2]


def getAllElementsInSencodList(firstList, secondList):
    list_c = [a for a in firstList if a in secondList]
    return list_c


def getIntersection(uinList):
    while len(uinList) > 1:
        list_a = []
        list_b = []
        list_a = uinList.pop()
        list_b = uinList.pop()
        list_c = getAllElementsInSencodList(list_a, list_b)
        if len(list_c) > 0:
            uinList.append(list_c)
    return uinList[0]

print getIntersection([[1,2,3,4,5],[2,3,4,5],[5,4,7,8],[3,4,5,6,7]])
