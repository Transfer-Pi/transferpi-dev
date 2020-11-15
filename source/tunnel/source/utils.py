from .__imports__ import (
                socket as s,dumps,loads,pathlib
            )

from .headers import Header

class Stream(object):
    def readStreamWithoutContentSize(self,stream: s.socket, timeout: float = 1) -> str:
        data = stream.recv(4)
        stream.settimeout(timeout)

        try:
            while True:
                data += stream.recv(4)
        except s.error:
            stream.settimeout(None)
        return data

    def readHeader(self,stream):
        start = stream.recv(4)
        while start[-4:] != '\r\n\r\n'.encode():
            try:
                start += stream.recv(1)
            except stream.error as e:
                print(f"[ERROR] {e}")
        return str(start[:-4], encoding="utf8"), start

    def pump(self,x: s.socket, y: s.socket, chunk_size: int, timeout: int = 1, _timeout=None) -> bool:
        """
        x : read from
        y : send to
        """
        x.settimeout(_timeout)
        y.send(x.recv(chunk_size))
        x.settimeout(timeout)
        try:
            while (bit := x.recv(chunk_size)):
                y.send(bit)
        except s.error:
            pass
        x.settimeout(None)


class HTTP:
    def text_response(self=None,message:str='')->str:
        header = Header() 
        header.status = "HTTP/1.1 200 OK"
        header.access_control_allow_origin = "*"
        header.connection = "Keep-Alive"
        header.content_type = "text/html; charset=utf-8"
        header.keep_alive: "timeout=1, max=999"
        header.data = message
        header.content_length = len(header.data)
        return header.encode_response().encode()

    def json_response(self=None,data:dict={})->str:
        header = Header() 
        header.status = "HTTP/1.1 200 OK"
        header.access_control_allow_origin = "*"
        header.connection = "Keep-Alive"
        header.content_type = "application/json; charset=utf-8"
        header.keep_alive: "timeout=1, max=999"
        header.data = dumps(data)
        header.content_length = len(header.data)
        return header.encode_response().encode()

    def http_response(self=None,data='',message:str='',status_code:int=200):
        header = Header() 
        header.status = f"HTTP/1.1 {status_code} {message}"
        header.access_control_allow_origin = "*"
        header.connection = "Keep-Alive"
        header.content_type = "application/json; charset=utf-8"
        header.keep_alive: "timeout=1, max=999"
        header.data = dumps(data) if isinstance(data,dict) else data
        header.content_length = len(header.data)
        return header.encode_response().encode()

    def render_template(self=None,path:str="./"):
        path = pathlib.abspath(path)
        header = Header() 
        try:
            with open(path,"r") as template:
                header.data = template.read()
                header.status = f"HTTP/1.1 200 OK"
        except:
            header.data = dumps({
                "message":f"Template {path} Not Found !"
            })
            header.status = f"HTTP/1.1 404 Not Found!"
        header.access_control_allow_origin = "*"
        header.connection = "Keep-Alive"
        header.content_type = "text/html; charset=utf-8"
        header.keep_alive: "timeout=1, max=999"
        header.content_length = len(header.data)
        return header.encode_response().encode()