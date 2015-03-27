#!/usr/bin/python3

import configparser

from bottle import route, run, view
from bottle import static_file
from tinydb import TinyDB


config = configparser.ConfigParser()
config.read('config.ini')

IMAGE_FOLDER = config['DEFAULT']["image_folder"]
THUMB_FOLDER = config['DEFAULT']["thumb_folder"]

db = TinyDB(config['DEFAULT']["db_file"])


@route('/')
@view('views/main.tpl')
def index():
    context = {'title': 'hello'}
    return dict(context)


@route('/images/<filename>')
def send_image(filename):
    return static_file(filename, root=THUMB_FOLDER, mimetype='image/jpg')


@route('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='./static')


run(host='localhost', port=8080)
