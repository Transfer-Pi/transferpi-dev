#!/usr/bin/env python3

import time
import jsondb
import logger
import re

from random import choice
from hashlib import md5
from datetime import datetime as dt

from lib.web import App,Request
from lib.requests import HTTPRequest
from lib.tunnel import Manager
from lib.headers import Header
from lib.utils import text_response, json_response, send_file

from lib.__imports__ import (
    Thread,asyncio,
    pathlib,environ,stat,popen,
    loads,dumps,
    getpid
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
LOGGER = logger.Logger(out=pathlib.join(PATH, "logs", "server_logs.txt"))

try:
    with open(pathlib.join(PATH,'config.json'),'r') as file:
        CONFIG = loads(file.read())
except:
    print ("Config not found !")

chars = [
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", 
    "q", "w", "e", "r", "t", "y", "u", "i", "o", "p", 
    "a", "s", "d", "e", "f", "i", "j", "k", "l", "Q", 
    "W", "E", "R", "T", "Y", "U", "I", "O", "P", "A", 
    "S", "D", "F", "G", "H", "J", "K", "L", "Z", "X", 
    "C", "V", "B", "N", "M"
]

class FileManager:
    """
    REST Object to manage file related resources
    """
    
    urlxre = re.compile("\d.\d.\d.\d")

    def __init__(self, cursor: jsondb.Database,config:dict):
        self.cursor = cursor
        self.config = config

        self['GET'] = self.GET
        self['POST'] = self.POST
        self['PUT'] = self.PUT
        self['DELETE'] = self.DELETE

    def __getitem__(self, key):
        return self.__dict__[key]

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __token__(self, l: int = 6) -> str:
        return "".join([choice(chars) for i in range(l)])

    async def GET(self, request: Request, token: str):
        if token == "GET_TOKENS":
            if request.header.host.split("/")[0].split(":")[0] == "localhost":
                return json_response({"tokens": self.cursor.tokens.fetchAll()})
            else:
                return json_response({
                    "message": "Not Allowed !",
                    "status": False
                },status_code=405)

        if (rec := self.cursor.tokens.fetchOne(token)):
            if rec.private:
                if 'authentication' not in request.header:
                    return json_response({
                        "message": "Autherization Error",
                        "status": False
                    }, status_code =401)
                if request.header.authentication not in self.config['allowed_hosts']:
                    return json_response({
                        "message": "Not Allowed",
                        "status": False
                    },status_code= 405, message='Not Allowed')

            if pathlib.isfile(rec.file):
                if self.urlxre.match(request.header.host):
                    if rec.local:
                        headers = {
                        "content_disposition" : f'attachment; filename={rec.filename}',
                        "filename" : rec.filename,
                        "md5" : rec.md5
                        }
                        
                        response = await send_file(
                                rec.file,
                                request,
                                headers=headers,
                                chunk_size=10240
                            )
                        return response       
                    else:
                        return json_response({
                            "message":"File not open for local sharing",
                            "status":False
                        },status_code=401)

                headers = {
                    "content_disposition" : f'attachment; filename={rec.filename}',
                    "filename" : rec.filename,
                    "md5" : rec.md5
                }
                
                response = await send_file(
                        rec.file,
                        request,
                        headers=headers
                    )
                return response
            else:
                return json_response({
                    "message": "File Does Not Exist !",
                    "status": False
                },status_code= 404)
        else:
            return json_response({
                "message": "File Not Found !",
                "status": False
            }, status_code=404)

    async def POST(self, request: Request, *args, **kwargs) -> dict:
        data = await request.get_json()
        md5_sum = md5(data['file'].encode()).hexdigest()
        token = None

        if (rec := self.cursor.files.fetchOne(md5_sum)):
            return  json_response(self.cursor.tokens.fetchOne(rec.token)())

        if data['private']:
            token = self.__token__(4)
        else:
            token = HTTPRequest(
                method='post',
                host='transferpi.tk',
                port=80,
                path='/token/new',
                json={

                },
                headers={
                    "authentication": self.config['subdomain'] + ':' + self.config['account_keys']['private']
                }
            )
            await token.make_request()
            if token.headers.status_code == '200':
                token = token.get_json()['token']
            else:
                return json_response(
                    token.get_json(), 
                    status_code=token.headers.status_code
                )

        self.cursor.files.insertOne(jsondb.Record(
            token=token,
            file=md5_sum
        ))
        
        *_,data['filename'] = pathlib.split(data['file'])
        data['token'] = token
        data['time'] = dt.now().strftime("%Y-%m-%d %X")
        _, data['md5'],*_ = popen( f"CertUtil -hashfile \"{data['file']}\" MD5").read().split("\n") if data['md5check'] else (None,'NOCHECK',None)
        del data['md5check']
        data['url'] = f"http://transferpi.tk/{token}"
        self.cursor.tokens.insertOne(jsondb.Record(**data))
        return json_response(data)

    async def PUT(self, request: Request, *args, **kwargs):
        return "PUT"

    async def DELETE(self, request: Request, token: str, *args, **kwargs):
        if token == "ALL":
            if self.cursor.tokens.deleteAll():
                if self.cursor.files.deleteAll():
                    return json_response({
                        "message": "Table Emptied Sucessfully"
                    })
                else:
                    return json_response({
                        "message": "Error deleting table : Files"
                    })
            else:
                return json_response({
                    "message": "Error deleting table : Tokens"
                })
        
        
        if (token_rec := self.cursor.tokens.fetchOne(token)):
            try:
                file_rec = self.cursor.files.fetchOne(
                    md5(token_rec.file.encode()).hexdigest())
                token_rec.destroy()
                file_rec.destroy()
                return json_response({"message": "File Removed From Sharing List"})
            except:
                token_rec.write()
                file_rec.write()
                return json_response({"message": "Cannot Remove File"})
        else:
            return json_response({"message": "File Not In Sharing List"})

app = App()
conn = jsondb.Cursor(path=pathlib.join(PATH), logger=LOGGER)
tunnel_manager = Manager(config=CONFIG,handle=app.handle_request)

conn.createDB("TOKENS")
db:jsondb.Database = conn.TOKENS

db.createTable("tokens","token")
db.createTable("files","file")

file_manager = FileManager(db,CONFIG)

@app.route("/")
async def index(request):
    return text_response("Fileserver 1.0.0")

@app.route("/file/<string:token>")
async def handle_files(request:Request,token:str):
    func = file_manager[request.header.method]
    return  await func(request,token)

@app.route("/<string:name>/<int:idd>")
async def name_id(request:Request,name,idd):
    return json_response({
        "name":name,
        "id":idd
    })

@app.route("/save_config/<string:config>")
async def save_config(request:Request,config):
    return text_response("Saved")


if __name__ == "__main__":

    with open(pathlib.join(PATH,"service","tunnel.pid"),"w+") as file:
        file.write(str(getpid()))

    try:
        asyncio.run(tunnel_manager.init())
    except ConnectionError:
        print ("Could not start tunnel, Remote server is not running")

    tun_thread = Thread(target=tunnel_manager.serve,)
    app_thread = Thread(target=app.serve,kwargs={
        "host":"0.0.0.0",#CONFIG['server_config']['local']['host'],
        "port":CONFIG['server_config']['local']['port']
    })

    tun_thread.start()
    app_thread.start()

    with open(pathlib.join(PATH,'service','tunnel.pid'),"w+") as file:
        file.write(str(getpid()))

    tun_thread.join()
    app_thread.join()