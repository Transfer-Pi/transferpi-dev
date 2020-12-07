from .__imports__ import datetime

header_data_types = {
	'content_length':int,
    'chunk_size':int
}

class RequestHeader(object):
    __skip = ['method','path','protocol']
    def __init__(self,):
        self.method = 'GET'
        self.path = '/'
        self.protocol = 'HTTP/1.1'
        self.host = 'localhost'
        self.connection = 'keep-alive'
        self.cache_control = 'max-age=0'
        self.dnt = '1'
        self.upgrade_insecure_requests = '1'
        self.user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
        self.accept = '*/*'
        self.accept_encoding = 'gzip, deflate, br'
        self.accept_language = 'en-US,en;q=0.9,hi;q=0.8'
        self.content_type = 'text/plain'

    def __getitem__(self,key)->str:
        return self.__dict__[key]

    def __setitem__(self,key:str,value:str):
        self.__dict__[key] = value

    def __delitem__(self,key):
        del self.__dict__[key]  

    def __str__(self)->str:
        return str(self.__encode__(),encoding='utf-8')

    def encode(self,)->str:
        header = f'{self.method} {self.path} {self.protocol}\r\n' 
        for key,val in self.__dict__.items():
            if not key.startswith("__") and key not in self.__skip:
                header += f"{key.replace('_','-').title()}: {val}\r\n"
        return header.encode()

    def parse(self,header):
        self.__raw__ = header
        self.__encode__ = self.encode
        req,*header = header.split('\r\n')
        self.method,self.path,self.protocol = req.split(" ")
        for line in header:
            try:
                key,val = line.split(': ')
                self.__dict__[key.lower().replace("-","_")] = val
            except:
                pass
        return self

class ResponseHeader(object):
    """
    Fix dynamic date formating
    """
    def __init__(self,):
        self.access_control_allow_origin = '*'
        self.connection = 'Keep-Alive'
        self.content_length = 0
        self.content_type = 'text/html; charset=utf-8'
        self.keep_alive = 'timeout=5, max=997'
        self.server = 'TPI1.0'
        # self.date = 'Mon, 18 Jul 2016 16:06:00 GMT'
        # self.last_modified = 'Mon, 18 Jul 2016 02:36:04 GMT'

    def __getitem__(self,key)->str:
        return self.__dict__[key]

    def __setitem__(self,key:str,value:str):
        self.__dict__[key] = value

    def __delitem__(self,key):
        del self.__dict__[key]  

    def __str__(self)->str:
        return str(self.__encode__(),encoding='utf-8')

    def __truediv__(self,data:str):
        return self.encode() + b'\r\n' + data.encode()

    def encode(self)->str:
        header = f'{self.status}\r\n' 
        for key,val in self.__dict__.items():
            if not key.startswith("__") and key != 'status':
                header += f"{key.replace('_','-').title()}: {val}\r\n"
        return header.encode()

    def parse(self,header):
        self.__raw__ = header
        self.__encode__ = self.encode
        self.status,*header = header.split('\r\n')
        for line in header:
            key,val = line.split(': ')
            self.__dict__[key] = val
        return self

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