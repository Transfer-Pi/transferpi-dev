#!/usr/bin/env python3

from source import App
from source.tunnel import Manager
from source.utils import HTTP

from source.__imports__ import (
    ThreadPoolExecutor,asyncio,
    pathlib,environ,
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

tunnel_manager = Manager(config=CONFIG)
asyncio.run(tunnel_manager.init())

@app.route("/")
def index(request):
    return http.text_response('Hello, World !')

def serve(app:App):
    app.serve()

with ThreadPoolExecutor(max_workers=2) as executer:
    apps = [app,tunnel_manager]
    for res in executer.map(serve,apps):
        pass