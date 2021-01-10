from lib.__imports__ import (
    pathlib,environ,loads,sys,asyncio,popen
)
from lib.requests import HTTPRequest


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
        for item in data:
            print (f"{item['filename']} {item['token']}")

    print ('\a')
    return False

if __name__ == "__main__":
    if (exit_code := asyncio.run(main())):
        print (exit_code)
    