#!/usr/bin/env python3

import time

from lib.web import App,Request
from lib.tunnel import Manager
from lib.headers import Header
from lib.utils import text_response, json_response, send_file

from lib.__imports__ import (
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
# tunnel_manager = Manager(config=CONFIG,handle=app.handle_request)

@app.route("/")
def index(request):
    return text_response("Fileserver 1.0.0")

@app.route("/<string:name>/<int:ID>")
def app_(request:Request,name,ID):
    return json_response({
        "name":name,
        "id":ID
    })

# try:
#     asyncio.run(tunnel_manager.init())
# except ConnectionError:
#     print ("Could not start tunnel, Remote server is not running")

app_thread = Thread(target=app.serve,kwargs={
    "host":CONFIG['server_config']['local']['host'],
    "port":CONFIG['server_config']['local']['port']
})
# tun_thread = Thread(target=tunnel_manager.serve,)

# tun_thread.start()
app_thread.start()

# tun_thread.join()
app_thread.join()