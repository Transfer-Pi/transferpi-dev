from os import path as pathlib,popen,get_terminal_size
from requests import get
from requests.exceptions import ConnectionError
from json import loads
from sys import exit



"""
App Config

linux/unix : ✔️
windows    : ⭕
mac        : ⭕
"""

_USERNAME,_ = popen("whoami").read().split("\n") 
_PATH = pathlib.join("/home/",_USERNAME,".transferpi")
_TYPES = ['private','open']

try:_CONFIG = loads(open(pathlib.join(_PATH,"config.json"),"r").read())
except:exit(print("Config File Not Fouund !"))


def main():
    try:        
        response = get(
            f"http://localhost:{_CONFIG['server_config']['local']['port']}/file/GET_TOKENS",
            headers={
                    "Authentication":_CONFIG['account_keys']['private']
                }
            )
    except ConnectionError:
        exit(print ("Error, Fileserver Not Running"))
        
    if response.status_code == 200:
        response = loads(response.text)
        col,_ = get_terminal_size()
        _t = (col*15)//100 - 3
        _f = (col*76)//100 - 3
        print ('-'*(col-3))
        print (f"| Token{' '*(_t-5)}File{' '*(_f-4)}Type{' '*(col-_t-_f-10)}|")
        print ('-'*(col-3))
        for token in response['tokens']:
            print (f"| {token['token']}{' '*(_t-len(token['token']))}{token['filename']}{' '*(_f-len(token['filename']))}{_TYPES[token['type']]}{' '*(col-_t-_f-10)}|")
        print ('-'*(col-3))
    elif response.status_code == 401:
        print ("Authentication Error (´ー`)")

if __name__ == "__main__":
    main()