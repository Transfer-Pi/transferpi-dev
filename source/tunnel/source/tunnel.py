from .__imports__ import asyncio,dumps,loads
from .headers import Header

class Tunnel:
    r:asyncio.StreamReader = None
    w:asyncio.StreamWriter = None
    def __init__(self,config:dict,session:dict,i:int):
        self.config = config
        self.session = session
        self.i = i

    async def open_tunnel(self,):
        self.r,self.w = await asyncio.open_connection(
            host=self.config['host'],
            port=self.config['port'],
        )

class Manager:
    __rnrn = slice(0,-4)
    def __init__(self,config:dict):
        self.config = config
        self.loop = asyncio.get_event_loop()

    async def init(self,):
        header = Header()
        header.method = "INIT"
        header.path = '/tunnel'
        header.protocol = 'TPI/1.1'
        header.content_type = "application/json"
        header.host = 'tunnel.create'
        header.data = dumps(
            {
                "username":  self.config['subdomain'],
                "key":  self.config['account_keys']['private']
            }
        )
        header.content_length = len(header.data)
        req = header.encode_request().encode()

        r,w = await asyncio.open_connection(
            host='localhost',#self.config['server_config']['remote']['host'],
            port=8081#self.config['server_config']['remote']['port'],
        )

        w.write(req)
        res_header = (await r.readuntil(b'\r\n\r\n')).decode()[self.__rnrn]
        res_header = Header().parse_response(res_header)

        self.session = loads((await r.read()).decode())
        await w.drain()
        w.close() 

    def serve(self,):
        pass
        