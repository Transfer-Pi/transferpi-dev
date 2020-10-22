from sys import exit,argv
from os import environ,popen,path as pathlib
from json import dumps, loads

doc = """Transfer Pi v0.0.13

start [service]   : starts provided service [ fileserver | tunnel ]
restart [service] : restarts provided service [ fileserver | tunnel ]
stop [service]    : stops provided service [ fileserver | tunnel ]
set [key=value]   : to modify config.json 
    [type=type]     ex. tpi-manage set server_config:local:port=8081 type=int
host [act=value]  : to add and remove hosts from allowed list [ add | remove | get]
                    ex. tpi-manage host add=host_public_key
config [options]  : prints current config [ print ]
"""                 

info = """|------------------------------------|
|           Transfer Pi              |
|------------------------------------|
| * CLI Version 0.0.1                |
| * Tunnel Version 0.0.1             |
| * Fileserver Version 0.0.1         |
|------------------------------------|"""

_PATH       = pathlib.join(environ['HOME'],".transferpi")
_CONFIGPATH = pathlib.join(_PATH,"config.json")
try:_CONFIG = loads(open(_CONFIGPATH,"r").read())
except:exit(print("Error, Config File Not Found"))

_TYPESETTINGS = {
    'dict':dict,
    'list':list,
    'int':int,
    'str':str,
    'float':float
}


single_args = ['config','info']
def parseArgs(argv):
    if not len(argv):
        exit(print (doc))
    else:
        action,*options = argv
        if not len(options) and action not in single_args:
            exit(print(f"Please Provide Options For {action}"))
        return action,options

def handleServices(action:str,services:list):
    for service in services:
        popen(f"service tpi-{service} {action}").read();

def handlerConfig(_,option):
    option,typesetting,*_ = option
    path,value = option.split("=")
    *path,key = path.split(":")
    config  = _CONFIG
    for p in path:
        try: config = config[p]
        except: exit(print (f"Key Not Found, {p}"))
    *_,typesetting = typesetting.split("=")
    config[key] = _TYPESETTINGS[typesetting](value)
    open(_CONFIGPATH,"w+").write(dumps(config))

def handlerHost(_,option):
    option,*_ = option
    action,*key = option.split("=")
    
    if action == 'get':
        print ("* Allowed Hosts")
        for host in _CONFIG['allowed_hosts']:print(f"|__ {host}")
    elif action == 'add':
        _CONFIG['allowed_hosts'] += key
        _CONFIG['allowed_hosts'] = list(set(_CONFIG['allowed_hosts']))
        open(_CONFIGPATH,"w+").write(dumps(_CONFIG))
    elif action == 'remove':
        try:
            _CONFIG['allowed_hosts'].remove(*key)
            open(_CONFIGPATH,"w+").write(dumps(_CONFIG))
        except:
            pass

def _printConfig(config:dict,level:int):
    for key,value in config.items():
        if isinstance(value,dict):
            print (f"{' '*level*4}{key} : {'{'}")
            _printConfig(value,level+1)
            print (f"{' '*level*4}{'{'}")
        else:
            print (f"{' '*level*4}{key} : {value}")

def printConfig(*args):
    print ("{")
    _printConfig(_CONFIG,1)
    print ("}")

def printInfo(*args):
    print (info)

handlers = {
    "start":handleServices,
    "restart":handleServices,
    "stop":handleServices,
    "set":handlerConfig,
    "host":handlerHost,
    "config":printConfig,
    'info':printInfo
}

def main(action:str,options:list):
    handlers[action](action,options)

if __name__ == "__main__":
    main(*parseArgs(argv[1:]))