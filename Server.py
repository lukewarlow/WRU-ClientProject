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


if __name__ == "__main__":
    app.run(debug=True)
