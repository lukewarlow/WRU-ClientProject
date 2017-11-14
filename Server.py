import os
from flask import Flask, redirect, request, render_template, jsonify
import random
app = Flask(__name__)

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

@app.route("/Home", methods=['GET'])
def returnFirst():
    if request.method == 'GET':
        return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
