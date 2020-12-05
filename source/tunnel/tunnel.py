#!/usr/bin/env python3

import time

from source import App,Request
from source.tunnel import Manager
from source.utils import HTTP
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

asyncio.run(tunnel_manager.init())

@app.route("/")
def index(request):
    return http.text_response('Fileserver Running !')

@app.route("/app")
def app_server(request:Request):
    return http.json_response({
        "name":"viraj patel"
    })

file_path = "E:\Downloads\[AnimeRG] Bleach (Complete Series) EP 001-366 [480p] [Dual-Audio] [Batch] [x265] [10-bit] [pseudo]\Season 15 (Gotei 13 Invading Army)\[AnimeRG] Bleach - 321 - Showdown of Mutual Self, Ikkaku vs. Ikkaku! [480p] [x265] [pseudo].mkv"

async def send_file(request:Request):
    print (request.header.encode_request())
    fname = file_path.split("\\")[-1]    
    head = Header()
    header = Header() 
    header.status = "HTTP/1.1 200 OK"
    header.access_control_allow_origin = "*"
    header.connection = "Keep-Alive"
    head.content_type = 'application/octet-stream'
    header.keep_alive: "timeout=1, max=999"
    header.content_disposition = f'attachment; filename="{fname}"'
    header.content_length = stat(file_path).st_size
    request.writer.write(header.encode_response().encode())
    
    with open(file_path,"rb") as file_stream:
        while (send_bit:=file_stream.read(512)):
            request.writer.write(send_bit)
    await request.writer.drain()
    request.writer.close()

@app.route("/file")
def file_sender(request:Request):
    request.loop.create_task(send_file(request))
    return False

def serve(app:App):
    app.serve()

app_thread = Thread(target=app.serve,kwargs={
    "host":CONFIG['server_config']['local']['host'],
    "port":CONFIG['server_config']['local']['port']
})
tun_thread = Thread(target=tunnel_manager.serve,)

tun_thread.start()
app_thread.start()

tun_thread.join()
app_thread.join()