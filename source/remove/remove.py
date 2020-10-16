from os import path as pathlib,popen
from argparse import ArgumentParser
from requests import delete
from requests.exceptions import ConnectionError
from json import loads
from sys import exit


parser = ArgumentParser()
parser.add_argument("token",help="Token",type=str)

"""
App Config

linux/unix : ✔️
windows    : ⭕
mac        : ⭕
"""

_USERNAME,_ = popen("whoami").read().split("\n") 
_PATH       = pathlib.join("/home/",_USERNAME,".transferpi")

try: _CONFIG = loads(open(pathlib.join(_PATH,"config.json"),"r").read())
except: exit(print("Config File Not Fouund !"))


def main(args):
    url = f"http://localhost:{_CONFIG['server_config']['local']['port']}/file/{args.token}"
    try:
        response = delete(
            url=url,
            headers={"Authentication":_CONFIG['account_keys']['private']}
        )
    except ConnectionError:
        exit(print ("Error, Fileserver Not Running"))
    print (response.json()['message'])

if __name__ == "__main__":
    main(parser.parse_args())