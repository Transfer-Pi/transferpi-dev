from lib.__imports__ import (
    pathlib,environ,loads,sys,asyncio,popen
)
from lib.requests import HTTPRequest
from os import get_terminal_size

"""
App config

windows : +
linux   : -
mac os  : -
"""

"""
tpi-list
"""

path   = pathlib.join(environ['USERPROFILE'],'.transferpi')

top_left = '┏'
top_right = '┓'
bottom_left = '┗'
bottom_right = '┛'
hr = '━'
vr = '┃'
cross = '╋'
t_left = '┣'
t_right = '┫'
t_down = '┻'
t_up = '┳'

col,row = get_terminal_size()
col -= 2
row_0 = int(col*(3/4)) - 2
row_1 = int(col*(1/4)) - 2

def format_row(filename,token,*args,**kwargs):

    return f"{vr} {token}{' '*(row_1-len(token))}{vr} {filename}{' '*(row_0-len(filename))}{vr}"

try:
    with open(pathlib.join(path,'config.json'),'r') as file:
        config = loads(file.read())
except:
    print ("Config not found !")

async def main():
    request = HTTPRequest(
        'get',
        config['server_config']['local']['host'],
        config['server_config']['local']['port'],
        '/file/GET_TOKENS'
    )
    try:
        await request.make_request()
    except ConnectionRefusedError:
        return 'Connection refused please start the server.'

    if request.headers.status_code == '200':
        data = request.get_json()['tokens']
        print (f"{top_left}{hr*(row_1+1)}{t_up}{hr*(row_0+1)}{top_right}")
        print (format_row(filename='Filename',token='Token'))
        
        print (f"{t_left}{hr*(row_1+1)}{cross}{hr*(row_0+1)}{t_right}")
        for item in data:
            print (format_row(**item))
        print (f"{bottom_left}{hr*(row_1+1)}{t_down}{hr*(row_0+1)}{bottom_right}")

    print ('\a')
    return False

if __name__ == "__main__":
    if (exit_code := asyncio.run(main())):
        print (exit_code)
    