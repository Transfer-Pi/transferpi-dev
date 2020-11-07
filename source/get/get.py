from sys import exit, stdout
from os import path as pathlib, popen, environ
from argparse import ArgumentParser
from requests import get, post
from json import loads
from time import time


parser = ArgumentParser()
parser.add_argument("token", help="File Path Or Name", type=str)
parser.add_argument(
    "-H", "--host", help="host/sender's username", type=str, default=0)
parser.add_argument(
    "-o", '--output', help='output file name', type=str, default=0)
parser.add_argument(
    "--force", help="download and update existing file", type=bool, default=False)
parser.add_argument(
    "--local", help="set this true when sharing file locally", type=bool, default=False)


"""
App Config

linux/unix : ⭕
windows    : ✔️
mac        : ⭕
"""

_PATH = pathlib.join(environ['USERPROFILE'], ".transferpi")
_URL = None

try:
    _CONFIG = loads(open(pathlib.join(_PATH, "config.json"), "r").read())
except:
    exit(print("Config File Not Fouund !"))


def main(args):
    if args.host:
        _URL = (
            f"http://" + args.host + "." +
            _CONFIG['server_config']['remote']['host'] + ':' +
            _CONFIG['server_config']['remote']['port'].__str__() +
            "/file/" + args.token
        )
    else:
        _URL = f"{_CONFIG['server_config']['web']['host']}/token/{args.token}"

    response = get(
        _URL,
        stream=True,
        headers={
            "Authentication": _CONFIG['account_keys']['public']
        }
    )

    if response.status_code == 200:
        print(f"[*] Starting Donwnload : {response.headers['Filename']}")
        content_length = int(response.headers['Content-Length'])
        downloaded = 0
        bar_size = 50
        step_size = content_length // bar_size  # Fix bar rendering for smaller objects
        start_time = time()
        _file = pathlib.abspath(response.headers['Filename'])
        with open(_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=_CONFIG['server_config']['local']['chunk_size']):
                file.write(chunk)
                downloaded += _CONFIG['server_config']['local']['chunk_size']
                width = (downloaded // step_size) - 1
                bar = "[*] |"+"▉"*width + " " * (bar_size - width) + '| '
                stdout.write(u"\u001b[1000D" + bar)
                stdout.flush()

        stdout.write(u"\u001b[1000D" + "[*] |" + "▉" * bar_size + '|\t')
        stdout.flush()
        stdout.write("\n")

        print(
            f"[*] Fetched {content_length//(1024*1024)} Mbs in {str(time()-start_time)[:8]} Seconds")
        print(f'[*] Cheking MD5')

        _, md5, *_ = popen(f"CertUtil -hashfile {_file} MD5").read().split("\n")
        if md5 == response.headers['Md5'] == md5:
            print("[*] Check Successful.")
            print(
                f"[*] Downloaded {response.headers['Filename']} Successfully.")
        else:
            print("[*] Check Failed.")
            print(f'[*] Downloaded {downloaded/(1024*1024)} Mb')
            main(args)
    elif response.status_code == 521:
        print("Server Down For Maintainence, Please Wait.")
    else:
        print(response.json()['message'])


if __name__ == "__main__":
    args = parser.parse_args()
    main(args)
