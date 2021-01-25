import tkinter as tk

from tkinter import *
from tkinter.filedialog import askopenfilename

from lib.__imports__ import (
    pathlib,environ,loads,sys,asyncio,popen
)
from lib.requests import HTTPRequest
from subprocess import Popen, PIPE, call

PATH = pathlib.join(environ['USERPROFILE'], ".transferpi")
CONFIGPATH = pathlib.join(PATH, "config.json")

response = None
keys = [
    "filename",
    "url",
    "token",
    "time",
    "md5",
    "private",
    
]

try:
    with open(pathlib.join(PATH,'config.json'),'r') as file:
        config = loads(file.read())
except:
    print ("Config not found !")

async def add_file(args):    
    request = HTTPRequest(
        'post',
        config['server_config']['local']['host'],
        config['server_config']['local']['port'],
        '/file/new',
        json = {
            "file":args['filename'],
            "private":args['p'],
            "md5check": not args['nomd5']
        }
    )
    try:
        await request.make_request()
    except ConnectionRefusedError:
        return 'Connection refused start the tunnel first.'

    if request.headers.status_code == '200':
        return request.get_json()

    return False

class FileCard(object):
    def __init__(self,master,response):
        self.response = response

        self._master = master
        self.master = Toplevel(master)
        self.master.geometry(f"+{300}+{300}")
        self.master.overrideredirect(True)

        self.frm_b1 = tk.Frame(self.master,height=2)
        self.frm_ttl = tk.Frame(self.master)
        self.frm_b2 = tk.Frame(self.master,height=2)
        self.frm_main = tk.Frame(self.master,width=15,relief = tk.GROOVE)
        
        self.txt_ttl = tk.Label(self.frm_ttl,text='File Added Successfully',height=1,width=60)
        self.txt_ttl.pack(side=tk.LEFT,fill=tk.X)
        self.txt_ttl.bind("<B1-Motion>", self.drag)
        
        self.btn_cls = Button(
            self.frm_ttl,
            text='❌',
            height=1,
            width=2,
            relief = tk.GROOVE,
            command=self.on_closing
        )
        self.btn_cls.pack(side=tk.RIGHT)

        labels = []
        for key in reversed(keys):
            w = Text(self.master, height=1, borderwidth=0,width=55)
            w.insert(1.0, f' {key} {" "*(10-len(key))} {response[key]}')
            w.pack()
            w.configure(state="disabled")
            w.configure(inactiveselectbackground=w.cget("selectbackground"))

            labels.append(
                w
            )
        
        for label in labels:
            label.pack(side=tk.BOTTOM)

        self.frm_b1.pack(side=tk.TOP)
        self.frm_ttl.pack(side=tk.TOP)
        self.frm_b2.pack(side=tk.TOP)
        self.frm_main.pack(side=tk.BOTTOM)

    def on_closing(self,):
        self.master.destroy()
        return

    def drag(self,event):
        self.master.geometry(f"+{event.x_root}+{event.y_root}")

class AddFile(object):
    def __init__(self,master,file):
        self._master = master
        self.master = Toplevel(master)
        self.master.geometry(f"+{300}+{300}")
        self.master.overrideredirect(True)

        self.file = file
        *_,self.file_name = pathlib.split(file)

        self.frm_b1 = tk.Frame(self.master,height=2)
        self.frm_ttl = tk.Frame(self.master)
        self.frm_b2 = tk.Frame(self.master,height=2)
        self.frm_btn = tk.Frame(self.master,width=15,relief = tk.GROOVE)
        
        self.txt_ttl = tk.Label(self.frm_ttl,text='Add File',height=1,width=35)
        self.txt_ttl.pack(side=tk.LEFT)
        self.txt_ttl.bind("<B1-Motion>", self.drag)

        self.btn_cls = Button(
            self.frm_ttl,
            text='❌',
            height=1,
            width=2,
            relief = tk.GROOVE,
            command=self.cleanup
        )
        self.btn_cls.pack(side=tk.RIGHT)
    
        self.lbl_fn = Label( 
            self.frm_btn, 
            text=self.file_name, 
            relief = tk.FLAT,
            width=20,
            height=5
        )
        self.lbl_fn.pack(side=tk.LEFT)
        
        # CheckBoxes
        self.val_pvt = IntVar()
        self.btn_pvt = Checkbutton(
            self.frm_btn,
            text='Private',
            width=15,
            height=1,
            justify=LEFT,
            variable=self.val_pvt
        )
        self.btn_pvt.pack()

        self.val_lcl = IntVar()
        self.btn_lcl = Checkbutton(
            self.frm_btn,
            text='Local',
            width=15,
            height=1,
            justify=LEFT,
            variable=self.val_lcl
        )
        self.btn_lcl.pack()

        self.val_md5 = IntVar()
        self.btn_md5 = Checkbutton(
            self.frm_btn,
            text='NoMD5',
            width=15,
            height=1,
            justify=LEFT,
            variable=self.val_md5
        )
        self.btn_md5.pack()
        
        self.btn_add = Button( 
            self.frm_btn, 
            text='Add', 
            relief = tk.GROOVE,
            command=self.add
        )
        self.btn_add.pack()

        self.frm_b1.pack(side=tk.TOP)
        self.frm_ttl.pack(side=tk.TOP)
        self.frm_b2.pack(side=tk.TOP)
        self.frm_btn.pack(side=tk.BOTTOM)

    def add(self,):
        args = {
            "p":bool(self.val_pvt.get()),
            "f":False,
            "nomd5":bool(self.val_md5.get()),
            "filename":self.file
        }
        globals()['response'] = asyncio.run(add_file(args))
        self.cleanup()

    def drag(self,event):
        self.master.geometry(f"+{event.x_root}+{event.y_root}")

    def cleanup(self):
        self.master.destroy()

class Manager:
    _running_fs = False
    proc_fs = None

    def __init__(self, master):
        self.master = master
        self.master.geometry(f"+{10}+{10}")

        self.frm_b1 = tk.Frame(self.master,height=2)
        self.frm_ttl = tk.Frame(self.master)
        self.frm_b2 = tk.Frame(self.master,height=2)
        self.frm_btn = tk.Frame(self.master)
        
        self.txt_ttl = tk.Label(self.frm_ttl,text='Transfer Pi',height=1,width=28)
        self.txt_ttl.pack(side=tk.LEFT)
        self.txt_ttl.bind("<B1-Motion>", self.drag)

        self.btn_cls = Button(
            self.frm_ttl,
            text='❌',
            height=1,
            width=2,
            relief = tk.GROOVE,
            command=self.on_closing
        )

        self.btn_cls.pack(side=tk.RIGHT)
    
        self.btn_fs_service = Button( 
            self.frm_btn, 
            text="Start Server", 
            command=self.start_fs, 
            relief = tk.GROOVE,
            width=15,
            height=3
        )
        self.btn_fs_service.pack(side=tk.LEFT)

        self.btn_file = Button(
            self.frm_btn,
            text='Add File',
            command=self.load_file,
            relief = tk.GROOVE,
            width=15,
            height=3
        )
        self.btn_file.pack()
        
        self.frm_b1.pack(side=tk.TOP)
        self.frm_ttl.pack(side=tk.TOP)
        self.frm_b2.pack(side=tk.TOP)
        self.frm_btn.pack(side=tk.BOTTOM)

    def load_file(self,):
        file = askopenfilename()
        if file:
            self.add = AddFile(self.master,file)
            self.master.wait_window(self.add.master)
        
        response = globals()['response']
        if response:
            self.card = FileCard(self.master,response)
            self.master.wait_window(self.card.master)

    def drag(self,event):
        self.master.geometry(f"+{event.x_root}+{event.y_root}")

    def start_fs(self):
        if self._running_fs:
            with open(pathlib.join(PATH,"service\\tunnel.pid")) as pid:
                call(['taskkill', '/F', '/T', '/PID',  pid.read()])
            self.btn_fs_service['text'] = 'start'
        else:
            self.proc_fs = Popen(['tpi-tunnel', '>', pathlib.join(PATH, "logs\\server_out.temp")],
                                 stdout=PIPE, stdin=PIPE, shell=True)
            self.btn_fs_service['text'] = 'stop'
        self._running_fs = ~ self._running_fs

    def on_closing(self,):
        if self._running_fs:
            call(['taskkill', '/F', '/T', '/PID',  str(self.proc_fs.pid)])
        self.master.destroy() 

def main(*args):
    root = Tk()
    root.overrideredirect(True)
    root.title("Transfer Pi")
    icon = PhotoImage(file=pathlib.join(PATH, "data\\logo.png"))
    root.iconphoto(False, icon)

    manager = Manager(root)
    root.protocol("WM_DELETE_WINDOW", manager.on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()
