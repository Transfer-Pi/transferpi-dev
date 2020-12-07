#!/usr/bin/env python3

import time

from source import App,Request
from source.tunnel import Manager
from source.utils import HTTP,mime_type,send_file
from source.headers import Header

from source.__imports__ import (
    Thread,asyncio,
    pathlib,environ,stat,
    loads,dumps
)

"""
App Config

linux/unix : ⭕
windows    : ✔️
mac        : ⭕
"""

header_data_types = {
    'content_length': int,
    "chunk_size": int
}

PATH = pathlib.join(environ['USERPROFILE'],'.transferpi')
try:
    with open(pathlib.join(PATH,'config.json'),'r') as file:
        CONFIG = loads(file.read())
except:
    print ("Config not found !")


app = App()
http = HTTP()
tunnel_manager = Manager(config=CONFIG,handle=app.handle_request)

file_path = "E:\Downloads\[AnimeRG] Bleach (Complete Series) EP 001-366 [480p] [Dual-Audio] [Batch] [x265] [10-bit] [pseudo]\Season 15 (Gotei 13 Invading Army)\[AnimeRG] Bleach - 321 - Showdown of Mutual Self, Ikkaku vs. Ikkaku! [480p] [x265] [pseudo].mkv"


@app.route("/")
def index(request):
    return http.text_response('Fileserver Running !')

@app.route("/<string:name>/<int:ID>")
def app_(request:Request,name,ID):
    return http.json_response({
        "name":name,
        "id":ID
    })

@app.route("/file")
def file_sender(request:Request):
    return send_file(file_path,request)

try:
    asyncio.run(tunnel_manager.init())
except ConnectionError:
    print ("Could not start tunnel, Remote server is not running")

app_thread = Thread(target=app.serve,kwargs={
    "host":CONFIG['server_config']['local']['host'],
    "port":CONFIG['server_config']['local']['port']
})
# tun_thread = Thread(target=tunnel_manager.serve,)

# tun_thread.start()
app_thread.start()

# tun_thread.join()
app_thread.join()