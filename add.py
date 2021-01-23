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

helpx = """
tpi-add filename [options]

filename : Name of file to add in sharing queue

[options]
--nomd5
--p : Add file to private queue 
--f : Force add file to queue, overwrite existing entry.     
"""

args = {
    "p":False,
    "f":False,
    "nomd5":False
}

for arg in sys.argv[1:]:
    if arg.startswith("--"):
        args[arg[2:]] = True
    elif arg.startswith("-"):
        key,val = arg[1:].split("=")
        args[key] = val
    else:
        args['filename'] = arg

path   = pathlib.join(environ['USERPROFILE'],'.transferpi')
try:
    with open(pathlib.join(path,'config.json'),'r') as file:
        config = loads(file.read())
except:
    print ("Config not found !")

keys = [
    "filename",
    "url",
    "token",
    "time",
    "md5",
    "private",
    
]

async def main():
    if 'filename' not in args:
        return helpx + '\nPlease provide filename.'

    file = pathlib.abspath(args['filename'])
    if not pathlib.isfile(file):
        return 'File does not exist'
    
    request = HTTPRequest(
        'post',
        config['server_config']['local']['host'],
        config['server_config']['local']['port'],
        '/file/new',
        json = {
            "file":file,
            "private":args['p'],
            "md5check": not args['nomd5']
        }
    )
    try:
        await request.make_request()
    except ConnectionRefusedError:
        return 'Connection refused start the tunnel first.'

    if request.headers.status_code == '200':
        data = request.get_json()
        for key in keys:
            print (f"* {key}{' '*(12 - len(key))}: {data[key]}")
    print ('\a')
    return False

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    if exit_code:
        print (exit_code)
    