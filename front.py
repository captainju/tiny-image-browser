#!/usr/bin/python3

import configparser

from tinydb import TinyDB, where
from flask import Flask, render_template, Response, request, json, send_from_directory


app = Flask(__name__)

config = configparser.ConfigParser()
config.read('config.ini')

IMAGE_FOLDER = config['DEFAULT']["image_folder"]
THUMB_FOLDER = config['DEFAULT']["thumb_folder"]
MEDIUM_FOLDER = config['DEFAULT']["medium_folder"]

db = TinyDB(config['DEFAULT']["db_file"])


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/images.json")
def imagesjson():
    albums = request.values.getlist('albums')
    test_func = lambda c: c in [float(i) for i in albums]
    result = sorted(db.search(where('album').test(test_func)), key=lambda a: a["time"], reverse=True)
    return Response(json.dumps(result), mimetype='application/json')


@app.route("/albums.json")
def albumsjson():
    result = []
    for entity in sorted(db.all(), key=lambda a: a["album"], reverse=True):
        if entity["album"] not in result:
            result.append(entity["album"])
    return Response(json.dumps(result), mimetype='application/json')


@app.route("/images/thumb/<filename>")
def imagesthumb(filename):
    return send_from_directory(THUMB_FOLDER, filename)


@app.route("/images/medium/<filename>")
def imagesmedium(filename):
    return send_from_directory(MEDIUM_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=True)
