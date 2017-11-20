import os
from flask import Flask, redirect, request, render_template, jsonify, make_response, escape, session
import random
import models as dbHandler
import sqlite3
app = Flask(__name__)

DATABASE = "database.db"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route("/Home", methods=['GET'])
def returnHome():
    if request.method == 'GET':
        return render_template('home.html', title="Homepage", admin=checkIsAdmin())

@app.route("/EventForm", methods=['POST', 'GET'])
def returnEventForm():
    # if request.method == 'GET':
    #     return render_template('eventForm.html')
    if request.method == 'GET':
        return render_template('eventForm.html', title="Event Form", admin=checkIsAdmin())
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
            cur.execute("INSERT INTO eventForm ('eventDate', 'postcode', 'eventRegion', 'peopleNum', 'tourNum', 'ageRange', 'comments')\
                        VALUES (?,?,?,?,?,?,?)", (eventDate, postcode, eventRegion, peopleNum, tourNum, ageRange, comments))
            conn.commit()
            msg = "Record successfully added"
        except:
            conn.rollback()
            msg = "Error in insert operation"
        finally:
            conn.close()

# staff page
@app.route('/Staff', methods=['POST', 'GET'])
def returnStaff():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        dbHandler.insertUser(username, password)
        users = dbHandler.retrieveUsers()
        return render_template('staff.html', users=users, title="Staff Log In", admin=checkIsAdmin())
    else:
        return render_template('staff.html', title="Staff Log In", admin=checkIsAdmin())

# adding staff to database on the admin page
@app.route("/Admin", methods=['POST', 'GET'])
def returnAdmin():
    if request.method == 'GET':
        return render_template('admin.html', title="Admin", admin=True)
    if request.method == 'POST':
        firstName = request.form.get('firstName', default="Error")
        surname = request.form.get('surname', default="Error")
        username = surname + firstName[0]
        username = username.lower()
        response = checkIfUserExists(username)
        if (response.split(":")[0] == "True"):
            username = username + response.split(":")[1]
        password = request.form.get('password', default="Error")
        usertype = request.form.get('usertype', default="Error")

        print("Added staff member:" + firstName)

        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO tblStaff ('username', 'password', 'usertype', 'firstname', 'surname')\
                        VALUES (?,?,?,?,?)", (username, password, usertype, firstName, surname))

            conn.commit()
            msg = "Record successfully added"
        except:
            conn.rollback()
            msg = "error in insert operation"
        finally:
            conn.close()
            return msg

def checkIsAdmin():
    return True

def checkIfUserExists(username):
    try:
        conn = sqlite3.connect(DATABASE)
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


if __name__ == "__main__":
    app.run(debug=True)
