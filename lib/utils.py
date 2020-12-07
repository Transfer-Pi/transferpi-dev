from .__imports__ import (
            dumps,loads,pathlib,stat
        )

from .headers import Header,ResponseHeader
from .mime_types import raw_text

def text_response(
        text:str,
        status_code:int=200,
        message:str='OK'
    )->str:
    response = ResponseHeader()
    response.status = f'HTTP/1.1 {status_code} {message}'
    response.content_length = len(text)
    response.content_type = 'text/plain; charset=utf-8'
    return response / text

def json_response(
        data:dict,
        status_code:int=200,
        message:str='OK'
    )->str:
    data = dumps(data)
    response = ResponseHeader()
    response.status = f'HTTP/1.1 {status_code} {message}'
    response.content_length = len(data)
    response.content_type = 'application/json; charset=utf-8'
    return response / data


def send_file(file:str,request):
    fname = file.split("\\")[-1]    
    head = Header()
    header = Header() 
    header.status = "HTTP/1.1 200 OK"
    header.access_control_allow_origin = "*"
    header.connection = "Keep-Alive"
    head.content_type = 'application/octet-stream'
    header.keep_alive: "timeout=1, max=999"
    header.content_disposition = f'attachment; filename="{fname}"'
    header.content_length = stat(file).st_size
    
    with open(file,"rb") as file_stream:
        request.writer.write(header.encode_response().encode())
        while (send_bit:=file_stream.read(512)):
            request.writer.write(send_bit)
    request.writer.close()
    return False

mime_type = dict((
    row.split("\t")
        for
    row
        in 
    raw_text.split("\n")
))