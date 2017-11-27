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
        return render_template('home.html', title="Homepage", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn())

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
            resp = make_response(render_template('login.html', username = username, admin = checkIsAdmin(), isloggedin=checkIsLoggedIn()))
            print(str(username) + " has logged in")
            return "successful"
        else:
            print("Failed to log in, incorrect password.")
            return "unsuccessful"
    else:
        return render_template('login.html', title="Log In", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn())

@app.route("/Staff/EventForm", methods = ['POST', 'GET'])
def returnEventForm():
    if request.method == 'GET':
        return render_template('eventForm.html', title="Event Form", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn())
    elif request.method == 'POST':
        eventDate = request.form.get('eventDate', default="error")
        postcode = request.form.get('postcode', default="error")
        eventRegion = request.form.get('eventRegion', default="error")
        comments = request.form.get('comments', default="error")
        print(request.form)
        try:
            conn = sql.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO tblEvent ('eventDate', 'postcode', \
            'eventRegion', 'comments')\
                        VALUES (?,?,?,?)",(eventDate, postcode, eventRegion, comments))
            conn.commit()
            msg = "Record successfully added"
        except sql.ProgrammingError as e:
            print("Error in operation," + str(e))
            conn.rollback()
            msg = "Error in insert operation"
        finally:
            print(msg)
            conn.close()
            return msg;

@app.route("/Staff/TournamentForm", methods = ['POST', 'GET'])
def returnTourForm():
    if request.method == 'GET':
        return render_template('tourForm.html', title="Tournament Form", admin=checkIsAdmin(), isloggedin=checkIsLoggedIn())
    elif request.method == 'POST':
        eventDate = request.form.get('eventDate', default="error")
        postcode = request.form.get('postcode', default="error")
        peopleNum = request.form.get('peopleNum', default="error")
        ageCategory = request.form.get('ageRange', default="error")
        genderRatio = request.form.get('genderRatio', default="error")
        eventID = ""
        try:
            conn = sql.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("SELECT ID FROM tblEvent WHERE eventDate=? AND postcode=?;", [eventDate, postcode])
            eventID = cur.fetchone()[0]
        except sql.ProgrammingError as e:
            print("Error in operation," + str(e))
        finally:
            conn.close()

        try:
            conn = sql.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO tblTournament ('peopleNum', 'ageCategory', 'genderRatio', 'eventID')\
                        VALUES (?,?,?,?)",(peopleNum, ageCategory, genderRatio, eventID))
            conn.commit()
            msg = "Record successfully added"
        except:
            conn.rollback()
            msg = "Error in insert operation"
        finally:
            conn.close()
            return msg

# adding staff to database on the admin page
@app.route("/Admin/AddStaff", methods=['POST', 'GET'])
def returnAddStaff():
    if request.method == 'GET':
        if checkIsAdmin():
            return render_template('admin/addstaff.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn())
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

        print("Adding staff member: " + username)

        try:
            conn = sql.connect(DATABASE)
            cur = conn.cursor()

            cur.execute("INSERT INTO tblStaff ('username', 'password', 'email', 'usertype', 'firstname', 'surname')\
                        VALUES (?,?,?,?,?,?)", (username, password, email, usertype, firstName, surname))
            conn.commit()
            msg = "User {} successfully added".format(username)
            print("Added staff member: " + username)
        except:
            conn.rollback()
            msg = "Error in insert operation"
            print("Failed to add staff member: " + username)
        finally:
            conn.close()
            return msg

@app.route("/Admin/DeleteStaff", methods=['POST', 'GET'])
def returnDeleteStaff():
    if request.method == 'GET':
        if checkIsAdmin():
            return render_template('admin/deletestaff.html', title="Admin", admin=True, isloggedin=checkIsLoggedIn())
        else:
            return redirect("/Home")
    elif request.method == 'POST':
        username = request.form.get('username', default="Error")
        username = username.lower()
        # usertype = ""
        #
        # try:
        #     conn = sql.connect(DATABASE)
        #     cur = conn.cursor()
        #     cur.execute("SELECT usertype FROM tblStaff WHERE username=?;", [username])
        #     usertype = cur.fetchone()[0]
        # except sql.ProgrammingError as e:
        #     print("Error in operation," + str(e))
        # finally:
        #     conn.close()

        try:
            conn = sql.connect(DATABASE)
            cur = conn.cursor()

            cur.execute("DELETE FROM tblStaff WHERE username=?;", [username]);
            conn.commit()
            msg = "User {} successfully deleted".format(username)
            print("Deleted staff member:" + username)
        except:
            conn.rollback()
            msg = "Error in insert operation"
            print("Failed to delete staff member:" + username)
        finally:
            conn.close()
            return msg


@app.route("/Logout", methods=['POST'])
def logout():
    session['username'] = ""
    session['password'] = ""
    session['usertype'] = ""
    return redirect("/Home")

def checkIsLoggedIn():
    usertype = ""
    if 'usertype' in session:
        usertype = escape(session['usertype'])
    if usertype == "Admin" or usertype == "Staff":
        return True
    else:
        return False

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

#http://dustwell.com/how-to-handle-passwords-bcrypt.html Date Accessed 20/11/2017
def encrypt(data, salt=gensalt()):
    return hashpw(bytes(data, 'utf-8'), salt)

if __name__ == "__main__":
    app.run(debug=True)
