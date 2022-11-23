'''
    uue aasta vastuvõtja 5.0
    {} markuse tarkvara

    server-side code

    (c) copyright 2021
    licensed under GNU General Public License v3
    (GPL3)

    read COPYING for more information
'''

#
# run these commands before attempting to run the script:
#
# pip install flask
# pip install mutagen
# pip install waitress
#

import os, datetime, subprocess, sys

from flask import Flask, request, abort, render_template, send_file
from mutagen.easyid3 import EasyID3
from random import randint

root = os.getcwd()

version = 5.0
app = Flask(__name__, template_folder=root)

# read config file
config = open("Config.ini", "r", encoding="UTF-8").readlines()
setup_id = 0

# set to true if you are using this in a live stream
is_live = True

# countdown type
cdn_type = 0
# name that is used when counting down to someone's birthday
cdn_name = "John Doe"
# year, when somebody was born
birthyear = 1970

# info text, displayed at the bottom left of the screen
infotext_title = ""
infotext = ""

# idle texts
# these are displayed above the time till the next year for 30 seconds, each on 30 second intervals
idletext = []
# what time of day to count down to
# numbers below 24 are a day before countdown date
# numbers 24 and above are one the countdown date
# e.g. [24, 0, 0, 0] would be midnight of target date
# format: [H, M, S, Ms]
midnight = [24, 0, 0, 0]
# countdown to which day (format: [D, M])
janone = [1, 1]
# logo setup
#
# show_logo
# if set to true, a watermark will be displayed in the bottom right
# corner, if set to false, no logo will be displayed
#
show_logo = True
# logofile
# choose which image file to display in the bottom right corner
# default image is markus' software js logo
logofile = "jsoftware.png"

# default port number: current year + 1
serverport = int(datetime.datetime.now().date().strftime("%Y")) + 1
#serverport = 80
# host address set to 0.0.0.0, so that other devices can access this site on the local network
serverhost = "0.0.0.0"

# load settings from config file
for line in config:
    data = line.strip().replace("\t", "")
    if data == "[IdleText]":
        setup_id = 1
    elif data == "[TargetTime]":
        setup_id = 2
    elif data == "[Watermark]":
        setup_id = 3
    elif data == "[InfoText]":
        setup_id = 4
    elif data == "[Server]":
        setup_id = 5
    elif data == "[Countdown]":
        setup_id = 6
    if setup_id == 1:
        if data[:4] == "Idle":
            idletext.append(data[6:])
    elif setup_id == 2:
        if data[:7] == "DateDay":
            janone[0] = int(data[8:])
        elif data[:9] == "DateMonth":
            janone[1] = int(data[10:])
        elif data[:9] == "TimeHours":
            midnight[0] = int(data[10:])
        elif data[:8] == "TimeMins":
            midnight[1] = int(data[9:])
        elif data[:8] == "TimeSecs":
            midnight[2] = int(data[9:])
        elif data[:10] == "TimeMillis":
            midnight[3] = int(data[11:])
    elif setup_id == 3:
        if data[:4] == "Show":
            if data[5] == "0":
                show_logo = False
        elif data[:4] == "file":
            logofile = data[5:]
    elif setup_id == 4:
        if data[:5] == "Title":
            infotext_title = data[6:]
        elif data[:7] == "Details":
            infotext = data[8:]
    elif setup_id == 5:
        if data[:4] == "Port":
            if not data[5:] == "auto":
                serverport = int(data[6:])
        if data[:4] == "Host":
            if not data[5:] == "auto":
                serverhost = data[6:]
        if data[:4] == "Root":
            if not data[5:] == "auto":
                root = data[6:]
    elif setup_id == 6:
        if data[:4] == "Type":
            cdn_type = int(data[5:])
        elif data[:12] == "BirthdayName":
            cdn_name = data[13:]
        elif data[:12] == "BirthdayYear":
            birthyear = int(data[13:])
config = None
if show_logo:
    disp_logo = "block"
else:
    disp_logo = "none"

janone[1] -= 1

msgs = []
special = []
songs = []
backgrounds = []


tagline = "Head uut aastat!"
#subtag = str(int(datetime.datetime.now().date().strftime("%Y")) + 1)
subtag = str(int(datetime.datetime.now().date().strftime("%Y")))
towhat = "Uue aastani"

if cdn_type == 1:
    tagline = "Head jõululaupäeva!"
    towhat = "Jõululaupäevani"
    subtag = "🎅"
    if janone == [0, -1]:
        janone = [24, 11]
elif cdn_type == 2:
    tagline = "Häid jõulupühi!"
    towhat = "Jõulupühadeni"
    subtag = "🎅"
    if janone == [0, -1]:
        janone = [25, 11]
elif cdn_type == 3:
    tagline = "Palju õnne, " + cdn_name + "!"
    towhat = "Sünnipäevani"
    subtag = str(int(datetime.datetime.now().date().strftime("%Y")) - birthyear)
elif cdn_type == 4:
    tagline = "Head lipupäeva!"
    towhat = "Lipupäevani"
elif cdn_type == 5:
    tagline = "Head iseseisvuspäeva!"
    towhat = "Iseseisvuspäevani"
    subtag = str(int(datetime.datetime.now().date().strftime("%Y")) - birthyear)
elif cdn_type == 6:
    tagline = "Head sõbrapäeva!"
    towhat = "Sõbrapäevani"
    subtag = "❤️"
    if janone == [0, -1]:
        janone = [14, 1]
elif cdn_type == 7:
    tagline = "Toredaid kevadpühi!"
    towhat = "Suure reedeni"
    subtag = "🐇"
elif cdn_type == 8:
    tagline = "Algas kevadine pööripäev!"
    towhat = "Kevadise pööripäevani"
    subtag = "🌼"
elif cdn_type == 9:
    tagline = "Algas talvine pööripäev!"
    towhat = "Talvise pööripäevani"
    subtag = "❄️"
elif cdn_type == 10:
    tagline = "Toredat ja ohutut jaani!"
    towhat = "Jaanipäevani"
    subtag = "🔥"
    if janone == [0, -1]:
        janone = [25, 5]
elif cdn_type == 11:
    tagline = "Head võidupüha!"
    towhat = "Võidupühani"
    subtag = "🇪🇪"
    if janone == [0, -1]:
        janone = [24, 5]
elif cdn_type == 12:
    tagline = "Head püha Patricku päeva!"
    towhat = "Püha Patricku päevani"
    subtag = "🍀"
    if janone == [0, -1]:
        janone = [17, 2]
elif cdn_type == 13:
    tagline = "Head usupuhastuspüha!"
    towhat = "Usupuhastuseni"
    subtag = "🎃"
    if janone == [0, -1]:
        janone = [31, 9]
else:
    if janone == [0, -1]:
        janone = [1, 0]
if janone == [0, -1]:
    print("Seda tüüpi sündmuse puhul peate käsitsi kuupäeva (ja kellaaja) määrama. Muutke faili 'Config.ini' vastavalt.")
# this finds artist/album info for songs
def find_ID3(filename):
    try:
        audio = EasyID3("media/songs/" + filename)
    except:
        return filename.replace(".mp3", "")
    try:
        return audio["artist"][0] + " - " + audio["title"][0] + " (" + audio["album"][0] + ")"
    except:
        try:
            return audio["artist"][0] + " - " + audio["title"][0]
        except:
            try:
                return audio["title"][0]
            except:
                try:
                    return audio["artist"][0] + " - " + filename.replace(".mp3", "")
                except:
                    return filename.replace(".mp3", "")
    return "Pala -1"

def event_column(i, splist, exclude):
    new = []
    for j, event in enumerate(splist):
        if not j == exclude: new.append(event.split("-")[i])
    return new

def reload():
    # load special messages
    specialmsgs = open("media/specialmessages.txt", "r", encoding="UTF-8").read().strip().split(";")
    for specialmsg in specialmsgs:
        sections = specialmsg.replace("\n", "").split("-")
        # check for randomization
        if not sections[3].replace("//", "") == sections[3]:
            splitted_section = sections[3].split("//")
            sections[3] = splitted_section[randint(0, len(splitted_section) - 1)]
        msgs.append([[sections[0], sections[1], sections[2], "0"], sections[3]])

    # load special events
    specialevents = open("media/specialevents.txt", "r", encoding="UTF-8").read().strip().split(";")
    for j, specialevent in enumerate(specialevents):
        sections = specialevent.replace("\n", "").replace("\ufeff", "").split("-")
        # check for randomization
        for i in range(3, 6):
            # /// allows for randomized events to be repeated
            # // does not allow repeats
            #
            # you can mix and match each one, but keep in mind
            # /// gets splitted and chosen first and then inside
            # that we split it by // again (which is why there's
            # 2 if statements instead of if and elif)
            if not sections[i].replace("///", "") == sections[i]:
                splitted_section = sections[i].split("///")
                sections[i] = splitted_section[randint(0, len(splitted_section) - 1)]
            if not sections[i].replace("//", "") == sections[i]:
                splitted_section = sections[i].split("//")
                sections[i] = splitted_section[randint(0, len(splitted_section) - 1)]
                while sections[i] in event_column(i, specialevents, j):
                    sections[i] = splitted_section[randint(0, len(splitted_section) - 1)]


        isvideo = "false"
        if not sections[3].replace("***", "") == sections[3]:
            isvideo = "background"
        elif not sections[3].replace("**", "") == sections[3]:
            isvideo = "true"
        special.append([[sections[0], sections[1], sections[2], "0"], isvideo, sections[3].replace("***", "").replace("**", ""), sections[4], sections[5]])

    # load songs and metadata
    songfiles = os.listdir("media/songs")
    for songfile in songfiles:
        if songfile.endswith(".mp3"):
            songs.append([songfile, find_ID3(songfile)])

    # load background images
    for image in sorted(os.listdir("media/backgrounds")):
        if not "desktop.ini" in image:
            backgrounds.append(image)


reload()


# main page rendering
@app.route("/", methods=["GET"])
def index():
    permission = "display: block;"
    test = "false"
    if "noinput" in request.args:
        permission = "display: none;"
    if "test" in request.args:
        test = "true"
    print("------------------")
    print("Veebilehe töötlemine ja saatmine seadmele: " + request.remote_addr)
    page = render_template("reference.html", permission=permission, msgs=msgs, special=special, songs=songs, backgrounds=backgrounds, nimg=len(backgrounds), nsong=len(songs), it=infotext, itt=infotext_title, idletext=idletext, janone=janone, midnight=midnight, logodisp=disp_logo, logofile=logofile, tagline=tagline, towhat=towhat, subtag=subtag, test=test)
    return page

# give access to multimedia files, forbid access to anything else
# supported file formats:
# music: mp3
# video: mp4, webm
# images: png, jpeg, svg, webp
# other: ico
@app.route("/<path:req_path>")
def file(req_path):
    abs_path = os.path.join(root, req_path)
    if not os.path.exists(abs_path):
        print("Ei leitud: " + abs_path.replace(root, ""))
        return abort(404)
    if os.path.isfile(abs_path) and abs_path.lower().endswith(".mp3") or abs_path.lower().endswith(".png") or abs_path.lower().endswith(".jpeg") or abs_path.lower().endswith(".ico") or abs_path.lower().endswith(".jpg") or abs_path.lower().endswith(".gif") or abs_path.lower().endswith(".jpe") or abs_path.lower().endswith(".bmp") or abs_path.lower().endswith(".svg") or abs_path.lower().endswith(".webm") or abs_path.lower().endswith(".mp4") or abs_path.lower().endswith(".webp"):
        if abs_path.lower().endswith("stopfail.png") and is_live:
            subprocess.call([r'C:\mas\end_stream.bat'])
            print("Otseülekanne lõpetati. Sulge server...")
            sys.exit(0)
        print("Faili saatmine: " + abs_path.replace(root, ""))
        return send_file(abs_path)
    else:
        print("Juurdepääs keelatud: " + abs_path.replace(root, ""))
        return abort(403)
    return render_page_string(out)

@app.errorhandler(404)
def notfound_error(e):
    return render_template("errors/404.html"), 404

@app.errorhandler(403)
def forbidden_error(e):
    return render_template("errors/403.html"), 403

if __name__ == "__main__":
    print("     --- Uue aasta vastuvõtja " + str(version) + " ---     ")
    from waitress import serve
    print("Juurkaust: " + root)
    print("Edastamine veebiaadressile: http://" + serverhost + ":" + str(serverport) + "/")
    print("Kohalik veebiaadress: http://127.0.0.1:" + str(serverport) + "/")
    print("Serveri sulgemiseks vajutage Ctrl + C")
    print("\n------------------\nLogi:")
    serve(app, host=serverhost, port=serverport)
    print("\nHead aega!\n")
