import os
from flask import Flask, redirect, request, render_template, jsonify
import random
import models as dbHandler
app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route("/Home", methods=['GET'])
def returnFirst():
    if request.method == 'GET':
        return render_template('home.html')

#staff page
@app.route('/staff', methods=['POST', 'GET'])
def home():
    if request.method=='POST':
        username = request.form['username']
        password = request.form['password']
        dbHandler.insertUser(username, password)
        users = dbHandler.retrieveUsers()
        return render_template('staff.html', users=users)
    else:
        return render_template('staff.html')

#adding staff to as an admin to a database on the admin page
@app.route("/admin", methods = ['POST','GET'])
def staffinfo():
    if request.method =='GET':
        return render_template('admin.html')
    if request.method =='POST':
        firstName = request.form.get('firstName', default="Error")
        surname = request.form.get('surname', default="Error")
        homeLocation = request.form.get('homeLocation', default="Error")
        dateofbirth = request.form.get('dateofbirth', default="Error")
        username = request.form.get('username', default="Error")
        password = request.form.get('password', default="Error")

        print("Added staff member:"+firstName)
        try:
            conn = sqlite3.connect(DATABASE)
            cur = conn.cursor()
            cur.execute("INSERT INTO staffinfo ('firstName', 'surname', 'dateofbirth', 'homeLocation', 'username', 'password')\
                        VALUES (?,?,?,?,?)",(firstName, surname, dateofbirth, homeLocation, username, password) )

            conn.commit()
            msg = "Record successfully added"
        except:
            conn.rollback()
            msg = "error in insert operation"
        finally:
            conn.close()
            return msg


if __name__ == "__main__":
    app.run(debug=True)
