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
tpi-remove token

token : token to be removed from the list / ALL to empty the queue
"""

path   = pathlib.join(environ['USERPROFILE'],'.transferpi')
try:
    with open(pathlib.join(path,'config.json'),'r') as file:
        config = loads(file.read())
except:
    print ("Config not found !")

async def main():
    if len(sys.argv) < 2:
        return "Please provide token"

    _,token = sys.argv
    request = HTTPRequest(
        'delete',
        config['server_config']['local']['host'],
        config['server_config']['local']['port'],
        '/file/'+token
    )
    try:
        await request.make_request()
    except ConnectionRefusedError:
        return 'Connection refused please start the server.'

    if request.headers.status_code == '200':
        data = request.get_json()
        print (data['message'])
    print ('\a')
    return False

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    if exit_code:
        print (exit_code)
    