from .__imports__ import asyncio,dumps,loads,ThreadPoolExecutor
from .headers import Header

class Tunnel:
    reader:asyncio.StreamReader = None
    writer:asyncio.StreamWriter = None
    __rnrn = slice(0,-4)
    def __init__(
            self,
            config:dict,
            session:dict,
            loop:asyncio.ProactorEventLoop,
            i:int,
        ):
        self.config = config
        self.session = session
        self.loop = loop
        self.i = i

    async def open_tunnel(self,):
        self.reader,self.writer = await asyncio.open_connection(
            host="localhost",#self.config['host'],
            port=8081#self.config['port'],
        )
        header = Header()
        header.method = "CREATE"
        header.path = '/tunnel'
        header.protocol = 'TPI/1.1'
        header.host = "create.tunnel"
        header.content_type = "application/json"
        header.data = dumps({
            "i":self.i
            # "username": self._config['subdomain'],
            # "id": self._id,
            # "session": self._session['key']
        })
        header.content_length = len(header.data)
        self.writer.write(header.encode_request().encode())
        
        try:
            header = await self.reader.readexactly(1)
        except asyncio.IncompleteReadError:
            pass
        except ConnectionError:
            return 0
        except OSError:
            return 0
        else:
            header += await self.reader.readuntil(separator=b'\r\n\r\n')
            header = Header().parse_request(str(header[self.__rnrn],encoding='utf-8'))
            return 0

    def run(self,):
        while True:
            asyncio.run(self.open_tunnel())

    
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

    def serve(
            self,
        ):
        tunnels = [
            (
                Tunnel,
                {
                    "i":i,
                    "config":self.config,
                    "session":self.session,
                    "loop":self.loop
                }
            )
            for 
                i
            in  
                range(self.config['server_config']['local']['n_pools'])
        ]
        
        def run_thread(arg):
            tunnel,kwargs = arg
            tunnel(**kwargs).run()

        with ThreadPoolExecutor(max_workers=8) as executer:
            executer.map(
                run_thread,
                tunnels
            )
        
        