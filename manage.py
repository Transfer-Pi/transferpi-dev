from os import path as pathlib,environ

import tkinter as tk

from tkinter import *
from tkinter.filedialog import askopenfilenames
from subprocess import Popen, PIPE, call

PATH = pathlib.join(environ['USERPROFILE'], ".transferpi")
CONFIGPATH = pathlib.join(PATH, "config.json")

class AddFile(object):
    def __init__(self,master,file=''):
        self.master = Toplevel(master)
        self.master.geometry(f"+{20}+{20}")
        self.master.overrideredirect(True)

        self.frm_b1 = tk.Frame(self.master,height=2)
        self.frm_ttl = tk.Frame(self.master)
        self.frm_b2 = tk.Frame(self.master,height=2)
        self.frm_btn = tk.Frame(self.master)
        
        self.txt_ttl = tk.Label(self.frm_ttl,text='Add File',height=1,width=28)
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
    
        self.btn_fs_service = Button( 
            self.frm_btn, 
            text="Start Server", 
            relief = tk.GROOVE,
            width=15,
            height=3
        )
        self.btn_fs_service.pack(side=tk.LEFT)

        self.btn_file = Button(
            self.frm_btn,
            text='Add Files',
            relief = tk.GROOVE,
            width=15,
            height=3
        )
        self.btn_file.pack()
        
        self.frm_b1.pack(side=tk.TOP)
        self.frm_ttl.pack(side=tk.TOP)
        self.frm_b2.pack(side=tk.TOP)
        self.frm_btn.pack(side=tk.BOTTOM)

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

        self.btn_cls = Button(self.frm_ttl,text='❌',height=1,width=2,relief = tk.GROOVE,command=self.on_closing)
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
            text='Add Files',
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
        # files = askopenfilenames()
        self.add = AddFile(self.master)
        self.master.wait_window(self.add.master)

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
