#!/usr/bin/python3

import os
import time
import configparser

from tinydb import TinyDB, where
import PIL.Image as Image


config = configparser.ConfigParser()
config.read('config.ini')

IMAGE_FOLDER = config['DEFAULT']["image_folder"]
THUMB_FOLDER = config['DEFAULT']["thumb_folder"]

SIZE_H = config['DEFAULT']["size.h"]
SIZE_W = config['DEFAULT']["size.h"]

db = TinyDB(config['DEFAULT']["db_file"])

db.purge_tables()

exif_date_time_codes = [0x9003, 0x9004, 0x0132]  # cf PIL.ExifTags


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
                        db.insert({"filename": fileName, "time": time.mktime(time_struct)})
                else:
                    print("no date time for " + fileName)


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


def generatethumb(filename, force=False):
    if os.path.isfile(os.path.join(IMAGE_FOLDER, filename)):
        if not os.path.isfile(os.path.join(THUMB_FOLDER, filename)) or force:
            try:
                im = Image.open(os.path.join(IMAGE_FOLDER, filename))
                size = (int(SIZE_W), int(SIZE_H))
                im.thumbnail(size)
                im.save(os.path.join(THUMB_FOLDER, filename), "JPEG")
            except IOError:
                print("cannot create thumbnail for", filename)


storeimagelist(IMAGE_FOLDER)

print(db.count(where('filename') != ""))

for entry in db.all():
    datetime = entry["time"]
    generatethumb(entry["filename"])