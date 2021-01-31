#!/usr/bin/env python3
from logger import Logger

from source.headers import Header
from source.utils import Stream
from source.tunnel import Tunnel
from source.__imports__ import (
    ThreadPoolExecutor,
    socket as s,
    pathlib, environ, sys,getpid,
    loads, dumps
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


PATH = pathlib.join(environ['HOME'], ".transferpi")
LOGGER = Logger(out=pathlib.join(PATH, "logs", "tunnel_logs.txt"))

try:
    CONFIG = loads(open(pathlib.join(PATH, "config.json"), "r").read())
except:
    exit(print("Error, Config Found !"))

def create_worker(kwargs):
    tunnel = Tunnel(**kwargs)
    while True:
        try:
            tunnel.forward()
        except KeyboardInterrupt:
            break
    return 0

def auth():
    header = Header()
    header.method = "INIT"
    header.path = '/'
    header.protocol = 'TPI/1.1'
    header.content_type = "application/json"
    header.host = 'tunnel.create'
    header.data = dumps(
        {"username":  CONFIG['subdomain'],
            "key":  CONFIG['account_keys']['private']}
    )
    header.content_length = len(header.data)
    tunnel = s.socket(s.AF_INET, s.SOCK_STREAM)
    tunnel.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    tunnel.settimeout(None)
    tunnel.connect((
        CONFIG['server_config']['remote']['host'],
        CONFIG['server_config']['remote']['port']
    ))

    tunnel.sendall(header.encode_request().encode())
    header, _ = Stream.readHeader(None, tunnel,)
    header = Header().parse_response(header)
    session = loads(
        str(tunnel.recv(int(header.content_length)), encoding="utf-8"))
    tunnel.close()
    return session

def main():
    print(
        f"* Remote Host       : { CONFIG['server_config']['remote']['host']}")
    print(
        f"* Remote Port       : { CONFIG['server_config']['remote']['port']}")
    print(f"* Subdomain         : { CONFIG['subdomain']}")
    print(f"* Machine Url       : " + "http://" +
          CONFIG['subdomain'] + '.' + CONFIG['server_config']['remote']['host'] + ':' + str(CONFIG['server_config']['remote']['port']))
    print(
        f"* Number Of Threads : { CONFIG['server_config']['local']['n_pools']}")

    print("* Authenticating Account")
    try:
        session = auth()
    except ConnectionRefusedError:
        exit(print("* Remote Host Not Running At The Time."))
    if session['status']:
        print("* Authentication Successful")
        with ThreadPoolExecutor(max_workers=CONFIG['server_config']['local']['n_pools']) as executer:
            thread_config = [
                {
                    "_id": i,
                    "config": CONFIG,
                    "session": session['session'],
                    "logger": LOGGER
                }
                for i in range(CONFIG['server_config']['local']['n_pools'])
            ]
            res = executer.map(create_worker, thread_config)
            for i in res:
                print(i)
    else:
        exit(LOGGER.error(session['message']))

if __name__ == "__main__":
    with open(pathlib.join(PATH,"logs","tn.pid"),"w+") as PID:
        PID.write(getpid().__str__())
    main()
