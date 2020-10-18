import time

from os import environ,path as pathlib,popen
from sys import exit
from json import loads

from flask import Flask,request,send_file,make_response,render_template
from flask_cors import CORS

from random import choice
from datetime import datetime as dt
from hashlib import md5
from requests import post

import jsondb
import logger


_PATH   = pathlib.join(environ['HOME'],".transferpi")
_LOGGER = logger.Logger(out=pathlib.join(_PATH,"logs","server_logs.txt"))

try:_CONFIG = loads(open(pathlib.join(_PATH,"config.json"),"r").read())
except:exit(print("Error, Config File Not Found !"))

app = Flask(__name__,template_folder=pathlib.join(_PATH,"data","templates"))
CORS(app=app)

CONN = jsondb.Cursor(path=pathlib.join(_PATH,"data"),logger=_LOGGER)
CONN.createDB("TPI")

DB = CONN.TPI
DB._logger = _LOGGER
DB.createTable("tokens","token")
DB.createTable("files","file")

CHARS = ["1","2","3","4","5","6","7","8","9","0","q","w","e","r","t","y","u","i","o","p","a","s","d","e","f","i","j","k","l","Q","W","E","R","T","Y","U","I","O","P","A","S","D","F","G","H","J","K","L","Z","X","C","V","B","N","M"]

class FileManager:
    """
    REST Object to manage file related resources
    """

    def __init__(self,cursor:jsondb.Database):
        self['GET'] = self.GET
        self['POST'] = self.POST
        self['PUT'] = self.PUT
        self['DELETE'] = self.DELETE

        self._CURSOR = cursor

    def __getitem__(self,key):
        return self.__dict__[key]

    def __setitem__(self,key,value):
        self.__dict__[key] = value

    def __token(self,l:int=6)->str:
        return "".join([choice(CHARS) for i in range(l)])        

    def GET(self,request:request,token:str):
        if token == "GET_TOKENS":
            if request.host_url.split("//")[1][:-1] == f"localhost:{_CONFIG['server_config']['local']['port']}":
                return {"tokens":self._CURSOR.tokens.fetchAll()}
            else:
                return {
                    "message":"Not Allowed !",
                    "status":False
                },405
        if (rec := self._CURSOR.tokens.fetchOne(token)):
            if not rec.type:
                if 'Authentication' not in request.headers:
                    return {
                        "message":"Autherization Error",
                        "status":False
                    },401
                if request.headers['Authentication'] not in _CONFIG['sharing']['private']['allowed_hosts']:
                    return {
                        "message":"Not Allowed",
                        "status":False
                    },405

            if pathlib.isfile(rec.file):
                response = make_response(send_file(rec.file))
                response.headers["Content-Disposition"] = (
                        f'attachment; filename={rec.filename}'
                    )
                response.headers['Filename'] = rec.filename
                response.headers['Md5'] = rec.md5
                return response
            else:
                return {
                        "message":"File Does Not Exist !",
                        "status":False
                },404
        else:
            return {
                    "message":"File Not Found !",
                    "status":False
                },404

    def POST(self,request:request,*args,**kwargs)->dict:
        data = request.get_json()
        md5_sum = md5(data['file'].encode()).hexdigest()
        token = None

        if (rec := self._CURSOR.files.fetchOne(md5_sum)):
            return self._CURSOR.tokens.fetchOne(rec.token)()
        
        if data['type']:
            try:
                token = post(
                    url =_CONFIG['server_config']['web']['host'] + '/token/NEW',
                    json ={},
                    headers={
                        "Authentication":_CONFIG['subdomain'] + ':' +_CONFIG['account_keys']['private']
                    }
                )
            except:
                return {"message":"Connection Error"},500

            if token.status_code == 200:
                token = token.json()['token']
            else: 
                return token.json(),token.status_code
        else:
            token = self.__token(4)

        self._CURSOR.files.insertOne(jsondb.Record(
            token=token,
            file = md5_sum
        ))

        data['filename'] = data['file'].split("/")[-1]
        data['token'] = token
        data['time']= dt.now().strftime("%Y-%m-%d %X")
        data['md5'],*_ = popen(f"md5sum {data['file']}").read().split(" ")       
        data['url'] = f"https://transferpi.tk/token/{token}"
        self._CURSOR.tokens.insertOne(jsondb.Record(**data))
        return data

    def PUT(self,request:request,*args,**kwargs):        
        return "PUT"

    def DELETE(self,request:request,token:str,*args,**kwargs):
        if token == "ALL":
            if self._CURSOR.tokens.deleteAll():
                if self._CURSOR.files.deleteAll():
                    return {
                        "message":"Table Emptied Sucessfully"
                    }
                else:
                    return {
                        "message":"Error deleting table : Files"
                    }
            else:
                return {
                    "message":"Error deleting table : Tokens"
                }
                            

        if (token_rec := self._CURSOR.tokens.fetchOne(token)):
            try:
                file_rec = self._CURSOR.files.fetchOne(md5(token_rec.file.encode()).hexdigest()) 
                token_rec.destroy()
                file_rec.destroy()
                return {"message":"File Removed From Sharing List"}
            except:
                token_rec.write()
                file_rec.write()
                return {"message":"Cannot Remove File"}
        else:
            return {"message":"File Not In Sharing List"}

FILE_MANAGER = FileManager(DB)


@app.route("/file/<string:token>",methods=['GET','POST','PUT','DELETE'])
def file(token):
    if request.method != 'GET' and ('Authentication' not in request.headers or request.headers['Authentication'] != _CONFIG['account_keys']['private']):
        return {"message":"Autherization Error"},401
    return FILE_MANAGER[request.method](request,token)

@app.route("/static/<string:_dir>/<string:_file>")
def serve_static(_dir,_file):
    _file = pathlib.join(_PATH,"data","templates","static",_dir,_file)
    return send_file(_file)


@app.route("/",methods=['GET'])
def index():
    if request.host_url.split("//")[1][:-1] == f"localhost:{_CONFIG['server_config']['local']['port']}":
        return render_template("index.html")
    else:
        return send_file(pathlib.join(_PATH,"data","home.jpg"))


if __name__ == "__main__":
    app.run(
            host=_CONFIG['server_config']['local']['host'],
            port=_CONFIG['server_config']['local']['port'],
            debug=True
        )

