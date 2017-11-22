import os
from flask import Flask, redirect, request, render_template, jsonify, make_response, escape, session
import random
import sqlite3 as sql
from bcrypt import hashpw, gensalt
import sys
app = Flask(__name__)

DATABASE = "database.db"
app.secret_key = 'fj590Rt?h40gg'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route("/Home", methods=['GET'])
def returnHome():
    if request.method == 'GET':
        return render_template('home.html', title="Homepage", admin=checkIsAdmin())

# staff page
@app.route('/Staff/Login', methods=['POST', 'GET'])
def returnLogin():
    if request.method == 'POST':
        username = request.form.get('username', default="Error").lower()
        password = request.form.get('password', default="Error")
        try:
            conn = sql.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("SELECT username, password, usertype FROM tblStaff WHERE username=?;", [username])
            data = cur.fetchone()
            pw = data[1]
            username = data[0]
            usertype = data[2]
        except sql.ProgrammingError as e:
            print("Error in operation," + str(e))
        finally:
            conn.close()
        if (encrypt(password, pw) == pw):
            session['username'] = username
            session['password'] = password
            session['usertype'] = usertype
            resp = make_response(render_template('login.html', msg='Logged in as '+username, username = username, admin = checkIsAdmin()))
            print(str(username) + " has logged in")
            return "successful"
        else:
            print("Failed to log in, incorrect password.")
            return "unsuccessful"
    else:
        return render_template('login.html', title="Log In", admin=checkIsAdmin())

# adding staff to database on the admin page
@app.route("/Admin/AddStaff", methods=['POST', 'GET'])
def returnAddStaff():
    if request.method == 'GET':
        if checkIsAdmin():
            return render_template('admin/addstaff.html', title="Admin", admin=True)
        else:
            return redirect("/Home")
    elif request.method == 'POST':
        firstName = request.form.get('firstName', default="Error")
        surname = request.form.get('surname', default="Error")
        username = surname + firstName[0]
        username = username.lower()
        response = checkIfUserExists(username)
        if (response.split(":")[0] == "True"):
            username = username + response.split(":")[1]
        password = request.form.get('password', default="Error")
        password = encrypt(password)
        email = request.form.get('email', default="Error").lower()
        usertype = request.form.get('usertype', default="Error")

        print("Adding staff member:" + username)

        try:
            conn = sql.connect(DATABASE)
            cur = conn.cursor()

            cur.execute("INSERT INTO tblStaff ('username', 'password', 'email', 'usertype', 'firstname', 'surname')\
                        VALUES (?,?,?,?,?,?)", (username, password, email, usertype, firstName, surname))
            conn.commit()
            msg = "Record successfully added"
            print("Added staff member:" + username)
        except:
            conn.rollback()
            msg = "Error in insert operation"
            print("Failed to add staff member:" + username)
        finally:
            conn.close()
            return msg

def checkIsAdmin():
    usertype = ""
    if 'usertype' in session:
        usertype = escape(session['usertype'])
    if usertype == "Admin":
        return True
    else:
        return False

def checkIfUserExists(username):
    try:
        conn = sql.connect(DATABASE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM tblStaff WHERE username=?;", [username])
        data = cur.fetchall()
    except:
        print('there was an error', data)
        data = ""
    finally:
        conn.close()
        if (len(data) > 0):
            return "True:{}".format(len(data) + 1)
        else:
            return "False"

@app.route("/eventForm", methods = ['POST', 'GET'])
def returnEventForm():
    if request.method == 'GET':
        return render_template('eventForm.html')
    if request.method == 'POST':
        eventDate = request.form.get('eventDate', default="error")
        postcode = request.form.get('postcode', default="error")
        eventRegion = request.form.get('eventRegion', default="error")
        peopleNum = request.form.get('peopleNum', default="error")
        tourNum = request.form.get('tourNum', default="error")
        ageRange = request.form.get('ageRange', default="error")
        comments = request.form.get('comments', default="error")
        try:
            conn = sqlite3.connect(DATABASE)
            cur = con.cursor()
            cur.execute("INSERT INTO eventForm ('eventDate', 'postcode', \
            'eventRegion', 'peopleNum', 'tourNum', 'ageRange', 'comments')\
                        VALUES (?,?,?,?,?,?,?)",(eventDate, postcode, eventRegion, \
                        peopleNum, tourNum, ageRange, comments) )
            conn.commit()
            msg = "Record successfully added"
        except:
            conn.rollback()
            msg = "Error in insert operation"
        finally:
            conn.close()

#http://dustwell.com/how-to-handle-passwords-bcrypt.html Date Accessed 20/11/2017
def encrypt(data, salt=gensalt()):
    return hashpw(bytes(data, 'utf-8'), salt)

if __name__ == "__main__":
    app.run(debug=True)
