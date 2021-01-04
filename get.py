from lib.__imports__ import (
    pathlib,loads,environ,sys,asyncio,popen,time
)
from lib.requests import HTTPRequest


"""
App config

windows : +
linux   : -
mac os  : -
"""

"""
tpi-get token [options]

filename : Name of file to add in sharing queue

[options]
-o  : output filename
-h  : hostname  
-l  : localhost
--ov : Force add file to queue, overwrite existing entry.     
"""

args = {
    "o":False,
    "h":False,
    "ov":False,
    "l":False
}

for arg in sys.argv[1:]:
    if arg.startswith("--"):
        args[arg[2:]] = True
    elif arg.startswith("-"):
        key,val = arg[1:].split("=")
        args[key] = val
    else:
        args['token'] = arg

path   = pathlib.join(environ['USERPROFILE'],'.transferpi')
try:
    with open(pathlib.join(path,'config.json'),'r') as file:
        config = loads(file.read())
except:
    print ("Config not found !")
    exit()

async def main():
    if 'token' not in args:
        return 'Please provide token.'

    url = ''
    request:HTTPRequest = None
    if args['h']:
        url = f"{args['h']}.{config['server_config']['remote']['host']}"
        request = HTTPRequest(
                'get',
                url,
                config['server_config']['remote']['port'],
                '/file/'+args['token'],
                stream=True,
                headers={
                    "authentication":config['account_keys']['public'] if args['h'] else None
                }
            )
    elif args['l']:
        host,port = args['l'].split(":")
        request = HTTPRequest(
                'get',
                host,
                port,
                '/file/'+args['token'],
                stream=True,
                headers={
                    "authentication":config['account_keys']['public'] if args['h'] else None
                }
            )
    else:
        request = HTTPRequest(
            'get',
            f"{config['server_config']['web']['host']}",
            config['server_config']['remote']['port'],
            '/' + args['token']
        )
        await request.make_request()
        if request.headers.status_code == '302':
            _,url = request.headers.location.split("//")
            url,*_ = url.split("/")
        else:
            return "Error, Token not found"

        request = HTTPRequest(
                'get',
                url,
                config['server_config']['remote']['port'],
                '/file/'+args['token'],
                stream=True,
                headers={
                    "authentication":config['account_keys']['public'] if args['h'] else None
                }
            )

    await request.make_request()    
    if request.headers.status_code == '200':
        if request.headers.content_length:
            content_length = int(request.headers.content_length)
            chunk_size = 512
            left_over = content_length % chunk_size
            chunks = (content_length // chunk_size) + 1
            filename = args['o'] if args['o'] else request.headers.filename
            file_path = pathlib.abspath(filename) 

            bullet = '•'
            bar_length = 25
            total = 0
            chunks_per_bar = content_length / bar_length

            start = time.time()
            print (f"[{bullet}] Downloading {filename}")
            with open(file_path,'wb') as file:
                for i in range(chunks):
                    file.write(await request.reader.read(chunk_size))
                    total += chunk_size
                    bar = int(total / chunks_per_bar)
                    sys.stdout.write(f"\r[{bullet}] [{bullet*bar}{' '*(bar_length-bar+1)}] {int(100*(total/content_length))}%")

                file.write(await request.reader.read(left_over))
                total += left_over
                bar = int(total / chunks_per_bar)
                sys.stdout.write(f"\r[{bullet}] [{bullet*bar}{' '*(bar_length-bar)}] 100%\n")

            total_time = time.time() - start
            print (f"[{bullet}] Downloaded {(total/(1024)):2f} in {total_time:2f} seconds")

            if request.headers.md5 != 'NOCHECK':
                print (f"[{bullet}] Checking MD5")
                _, md5,*_ = popen( f"CertUtil -hashfile \"{file_path}\" MD5").read().split("\n")
                if request.headers.md5 == md5:
                    print (f"[{bullet}] Checking succesfull")
                else:
                    print (f"[{bullet}] MD5 does not match")
    elif request.headers.status_code == '404':
        return 'File token not found'

    return False

if __name__ == "__main__":
    if (exit_code := asyncio.run(main())):
        print (exit_code)
    