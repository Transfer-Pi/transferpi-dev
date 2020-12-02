from .__imports__ import datetime

header_data_types = {
	'content_length':int,
    'chunk_size':int
}

class Header:
    def __init__(self):
        self.method = None
        self.path = None
        self.access_control_allow_origin = "*"
        self.connection = None
        self.content_length = None
        self.content_type = None
        self.keep_alive = None
        self.status = None
        self.chunk_size = None
        self.filename = None
        self.server = None
        self.content_encoding = None
        self.location = None
        self.date = None		
        self.host = None
        self.data = None

    def __getitem__(self,key)->str:
        return self.__dict__[key]

    def __setitem__(self,key:str,value:str):
        self.__dict__[key] = value

    def __delitem__(self,key):
        del self.__dict__[key]  

    def __str__(self)->str:
        return self.__encode__()

    def encode_request(self,)->str:
        header = f'{self.method} {self.path} {self.protocol}\r\n' 
        for key,val in self.__dict__.items():
            if not key.startswith("__") and key not in ['method','path','protocol','data'] and val:
                header += f"{key.replace('_','-').title()}: {val}\r\n"
        return header+"\r\n" + ( self.data if self.data else '')
        
    def encode_response(self)->str:
        header = f'{self.status}\r\n' 
        for key,val in self.__dict__.items():
            if not key.startswith("__") and val and key != 'data':
                header += f"{key.replace('_','-').title()}: {val}\r\n"
        return header+"\r\n" + ( self.data if self.data else '')

    def parse_request(self,header):
        self.__raw__ = header
        self.__encode__ = self.encode_request
        req,*header = header.split('\r\n')
        self.method,self.path,self.protocol = req.split(" ")
        for line in header:
            try:
                key,val = line.split(': ')
                self.__dict__[key.lower()] = val
            except:
                pass
        return self
        
    def parse_response(self,header):
        self.__raw__ = header
        self.__encode__ = self.encode_response
        self.status,*header = header.split('\r\n')
        for line in header:
            key,val = line.split(': ')
            self.__dict__[key] = val
        return self