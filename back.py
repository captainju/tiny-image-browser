#!/usr/bin/python3

import os
import time
from datetime import date
import configparser

from tinydb import TinyDB, where
import PIL.Image as Image


config = configparser.ConfigParser()
config.read('config.ini')

IMAGE_FOLDER = config['DEFAULT']["image_folder"]
THUMB_FOLDER = config['DEFAULT']["thumb_folder"]
MEDIUM_FOLDER = config['DEFAULT']["medium_folder"]

THUMB_SIZE_H = config['DEFAULT']["thumb.size.h"]
THUMB_SIZE_W = config['DEFAULT']["thumb.size.w"]

MEDIUM_SIZE_H = config['DEFAULT']["medium.size.h"]
MEDIUM_SIZE_W = config['DEFAULT']["medium.size.w"]

db = TinyDB(config['DEFAULT']["db_file"])

db.purge_tables()

exif_date_time_codes = [0x9003, 0x9004, 0x0132]  # cf PIL.ExifTags


def getdatetimefromexif(imgpath):
    if os.path.isfile(imgpath):
        try:
            im = Image.open(imgpath)
            for exif_date_time_code in exif_date_time_codes:
                try:
                    exifdata = im._getexif()
                    if exifdata is not None:
                        return time.strptime(exifdata[exif_date_time_code].replace("/", ":"), "%Y:%m:%d %H:%M:%S")
                except KeyError:
                    None
        except OSError:
            None

    return None


def storeimagelist(path):
    if os.path.isdir(path):
        listdir = os.listdir(path)
        file_nb = 0
        for fileName in listdir:
            file_nb += + 1
            if file_nb % 100 == 0:
                print(str(file_nb) + " / " + str(len(listdir)))
            if os.path.isfile(os.path.join(path, fileName)):
                time_struct = getdatetimefromexif(os.path.join(path, fileName))
                if time_struct is not None:
                    existing_entry = db.get(where('filename') == fileName)
                    if existing_entry is None:
                        albumdate = date(time_struct.tm_year, time_struct.tm_mon, time_struct.tm_mday)
                        db.insert({"filename": fileName, "time": time.mktime(time_struct), "album": time.mktime(albumdate.timetuple())})
                        generatethumb(fileName, True)
                        generatemedium(fileName, True)
                else:
                    print("no date time for " + fileName)


def generatethumb(filename, force=False):
    if os.path.isfile(os.path.join(IMAGE_FOLDER, filename)):
        if not os.path.isfile(os.path.join(THUMB_FOLDER, filename)) or force:
            try:
                im = Image.open(os.path.join(IMAGE_FOLDER, filename))
                size = (int(THUMB_SIZE_W), int(THUMB_SIZE_H))
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(os.path.join(THUMB_FOLDER, filename), "JPEG", quality=90)
            except IOError:
                print("cannot create thumbnail for", filename)


def generatemedium(filename, force=False):
    if os.path.isfile(os.path.join(IMAGE_FOLDER, filename)):
        if not os.path.isfile(os.path.join(MEDIUM_FOLDER, filename)) or force:
            try:
                im = Image.open(os.path.join(IMAGE_FOLDER, filename))
                size = (int(MEDIUM_SIZE_W), int(MEDIUM_SIZE_H))
                im.thumbnail(size, Image.ANTIALIAS)
                im.save(os.path.join(MEDIUM_FOLDER, filename), "JPEG", quality=90)
            except IOError:
                print("cannot create medium for", filename)


storeimagelist(IMAGE_FOLDER)

print(db.count(where('filename') != ""))
