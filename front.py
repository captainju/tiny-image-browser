#!/usr/bin/python3

import configparser

from tinydb import TinyDB, where
from flask import Flask, render_template, Response, request, json, send_from_directory
from functools import wraps


app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

IMAGE_FOLDER = config['DEFAULT']["image_folder"]
THUMB_FOLDER = config['DEFAULT']["thumb_folder"]
MEDIUM_FOLDER = config['DEFAULT']["medium_folder"]

db = TinyDB(config['DEFAULT']["db_file"])


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == 'secret'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


@app.route("/")
@requires_auth
def index():
    return render_template('index.html')


@app.route("/images.json")
@requires_auth
def imagesjson():
    albums = request.values.getlist('albums')
    test_func = lambda c: c in [float(i) for i in albums]
    result = sorted(db.search(where('album').test(test_func)), key=lambda a: a["time"], reverse=True)
    return Response(json.dumps(result), mimetype='application/json')


@app.route("/albums.json")
@requires_auth
def albumsjson():
    result = []
    for entity in sorted(db.all(), key=lambda a: a["album"], reverse=True):
        if entity["album"] not in result:
            result.append(entity["album"])
    return Response(json.dumps(result), mimetype='application/json')


@app.route("/images/thumb/<filename>")
@requires_auth
def imagesthumb(filename):
    return send_from_directory(THUMB_FOLDER, filename)


@app.route("/images/medium/<filename>")
@requires_auth
def imagesmedium(filename):
    return send_from_directory(MEDIUM_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)
