from sys import exit, argv
from webbrowser import open as browser

from lib.web import App,Request
from lib.utils import json_response 

from lib.__imports__ import (
    Thread,
    pathlib,environ,popen,
    loads,dumps
)

from tkinter import Tk, Label, Button
from tkinter import PhotoImage
from subprocess import Popen, PIPE, call

doc = """Transfer Pi v0.0.13
manage [options]  : open manager window
set [key=value]   : modify config.json 
    [type=type]     ex. tpi-manage set server_config:local:port=8081 type=int
host [act=value]  : add and remove hosts from allowed list [ add | remove | get]
                    ex. tpi-manage host add=host_public_key
config [options]  : prints current config
login [options]   : open login browser window 
"""

info = """|------------------------------------|
|           Transfer Pi              |
|------------------------------------|
| * CLI Version 0.0.1                |
| * Tunnel Version 0.0.1             |
| * Fileserver Version 0.0.1         |
|------------------------------------|"""

_PATH = pathlib.join(environ['USERPROFILE'], ".transferpi")
_CONFIGPATH = pathlib.join(_PATH, "config.json")
_TYPESETTINGS = {
    'dict': dict,
    'list': list,
    'int': int,
    'str': str,
    'float': float
}

single_args = ['config', 'info', 'login', 'manage']

class Manager:
    _running_fs = False
    _running_tn = False

    def __init__(self, master):
        self.master = master

        self.col_service = Label(master, text="Service")
        self.col_start = Label(master, text="Start / Stop")
        self.col_status = Label(master, text="Status")

        self.lbl_fs = Label(master, text="Fileserver")
        self.status_fs = Label(master, text="not running")
        self.btn_fs_service = Button(
            master, text="Start", command=self.start_fs)

        self.lbl_tn = Label(master, text="Tunnel")
        self.status_tn = Label(master, text="not running")
        self.btn_tn_service = Button(
            master, text="Start", command=self.start_tn)

        self.col_service.grid(row=1, column=0, padx=3, pady=3)
        self.lbl_fs.grid(row=2, column=0, padx=3, pady=3)
        self.lbl_tn.grid(row=3, column=0, padx=3, pady=3)

        self.col_start.grid(row=1, column=1, padx=3, pady=3)
        self.btn_fs_service.grid(row=2, column=1, padx=3, pady=3)
        self.btn_tn_service.grid(row=3, column=1, padx=3, pady=3)

        self.col_status.grid(row=1, column=2, padx=3, pady=3)
        self.status_fs.grid(row=2, column=2, padx=3, pady=3)
        self.status_tn.grid(row=3, column=2, padx=3, pady=3)

    def start_fs(self):
        if self._running_fs:
            call(['taskkill', '/F', '/T', '/PID',  str(self.proc_fs.pid)])
            self.btn_fs_service['text'] = 'start'
            self.status_fs['text'] = 'not running'
        else:
            self.proc_fs = Popen(['tpi-fileserver', '>', pathlib.join(_PATH, "logs\\server_out.temp")],
                                 stdout=PIPE, stdin=PIPE, shell=True)
            self.btn_fs_service['text'] = 'stop'
            self.status_fs['text'] = 'running'
        self._running_fs = ~ self._running_fs

    def start_tn(self):
        if self._running_tn:
            call(['taskkill', '/F', '/T', '/PID',  str(self.proc_tn.pid)])
            self.btn_tn_service['text'] = 'start'
            self.status_tn['text'] = 'not running'
        else:
            self.proc_tn = Popen(
                ['tpi-tunnel', '>', pathlib.join(_PATH, "logs\\tunnel_out.temp")], stdout=PIPE, stdin=PIPE, shell=True)
            self.btn_tn_service['text'] = 'stop'
            self.status_tn['text'] = 'running'
        self._running_tn = ~ self._running_tn

    def on_closing(self,):
        if self._running_fs:
            call(['taskkill', '/F', '/T', '/PID',  str(self.proc_fs.pid)])
        if self._running_tn:
            call(['taskkill', '/F', '/T', '/PID',  str(self.proc_tn.pid)])
        self.master.destroy()

def runManager(*args):
    root = Tk()
    root.title("Transfer Pi")
    icon = PhotoImage(file=pathlib.join(_PATH, "data\\logo.png"))
    root.iconphoto(False, icon)
    manager = Manager(root)
    root.protocol("WM_DELETE_WINDOW", manager.on_closing)
    root.mainloop()

def parseArgs(argv):
    if not len(argv):
        exit(print(doc))
    else:
        action, *options = argv
        if not len(options) and action not in single_args:
            exit(print(f"Please Provide Options For {action}"))
        return action, options


def handleServices(action: str, services: list):
    for service in services:
        popen(f"sudo systemctl {action} tpi-{service}").read()


def loadConfig():
    config = dict()
    try:
        config = loads(open(_CONFIGPATH, "r").read())
    except:
        exit(print("Error, Config File Not Found"))
    return config


def handlerConfig(_, option):
    config = loadConfig()
    option, typesetting, *_ = option
    path, value = option.split("=")
    *path, key = path.split(":")
    _config = config
    for p in path:
        try:
            _config = _config[p]
        except:
            exit(print(f"Key Not Found, {p}"))
    *_, typesetting = typesetting.split("=")
    _config[key] = _TYPESETTINGS[typesetting](value)
    open(_CONFIGPATH, "w+").write(dumps(config))


def handlerHost(_, option):
    option, *_ = option
    action, *key = option.split("=")
    config = loadConfig()
    if action == 'get':
        print("* Allowed Hosts")
        for host in config['allowed_hosts']:
            print(f"|__ {host}")
    elif action == 'add':
        config['allowed_hosts'] += key
        config['allowed_hosts'] = list(set(config['allowed_hosts']))
        open(_CONFIGPATH, "w+").write(dumps(config))
    elif action == 'remove':
        try:
            config['allowed_hosts'].remove(*key)
            open(_CONFIGPATH, "w+").write(dumps(config))
        except:
            pass


def _printConfig(config: dict, level: int):
    for key, value in config.items():
        if isinstance(value, dict):
            print(f"{' '*level*4}{key} : {'{'}")
            _printConfig(value, level+1)
            print(f"{' '*level*4}{'{'}")
        else:
            print(f"{' '*level*4}{key} : {value}")


def printConfig(*args):
    config = loadConfig()
    print("{")
    _printConfig(config, 1)
    print("}")


def printInfo(*args):
    print(info)


def handleLogin(*args):
    app = App()
    @app.route("/save_config")
    async def index(request:Request):
        with open(_CONFIGPATH,'w+') as file:
            config = str(await request.content,encoding='utf-8')
            file.write(config)
        
        return json_response(data={
            'message':'Config saved succesfully'
        })

    browser("http://transferpi.tk/login")
    print("* Press Ctrl + C to exit after saving config")
    try:
        app.serve(**{
            "host":"localhost",
            "port":2121
        })
    except KeyboardInterrupt:
        exit()


handlers = {
    "start": handleServices,
    "restart": handleServices,
    "stop": handleServices,
    "set": handlerConfig,
    "host": handlerHost,
    "config": printConfig,
    "info": printInfo,
    "login": handleLogin,
    "manage": runManager,
}


def main(action: str, options: list):
    handlers[action](action, options)


if __name__ == "__main__":
    main(*parseArgs(argv[1:]))