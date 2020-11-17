from .__imports__ import (
                socket as s,dumps,loads,sleep
            )
from .headers import Header
from .utils import HTTP,Stream

class Tunnel:
    def __init__(self, _id: int, config: dict, session: dict,logger):
        self._id = _id
        self._config = config
        self._session = session
        self._stream = Stream()
        self._logger = logger
        self._createRemoteTunnel()

    def _createRemoteTunnel(self, recon=0):
        try:
            self.tunnel = s.socket(s.AF_INET, s.SOCK_STREAM)
            self.tunnel.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
            self.tunnel.settimeout(None)
            self.tunnel.connect((
                self._config['server_config']['remote']['host'],
                self._config['server_config']['remote']['port']
            ))

            header = Header()
            header.method = "CREATE"
            header.path = '/'
            header.protocol = 'TPI/1.1'
            header.host = "create.tunnel"
            header.content_type = "application/json"
            header.data = dumps({
                "username": self._config['subdomain'],
                "id": self._id,
                "session": self._session['key']
            })
            header.content_length = len(header.data)
            self.tunnel.sendall(header.encode_request().encode())
            header,_ = self._stream.readHeader(self.tunnel,)
            header = Header().parse_request(header)
            self.session = loads(
                str(self._stream.readStreamWithoutContentSize(self.tunnel), encoding="utf-8"))
            if self.session['status']:
                self._logger.success(f"Tunnel Connected With Id {self._id}")
            else:
                self._logger.error(self.session['message'])

        except:
            sleep(1)
            self._logger.error(f'Error Connectiong To Host Retrying ...')
            self.tunnel.close()
            self._createRemoteTunnel(recon=recon+1)

    def _createLocalTunnel(self,):
        try:
            self.local = s.socket(s.AF_INET, s.SOCK_STREAM)
            self.local.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
            self.local.settimeout(1)
            self.local.connect((
                self._config['server_config']['local']['host'],
                self._config['server_config']['local']['port']
            ))
        except:
            self._logger.error('Error Connecting Fileserver Retrying...')
            self.local.close()
            sleep(1)
            self._createLocalTunnel()

    def forward(self,):
        self._createLocalTunnel()
        try:
            self._stream.pump(self.tunnel, self.local,
                 self._config['server_config']['local']['chunk_size'], _timeout=30)
            self._stream.pump(self.local, self.tunnel,
                 self._config['server_config']['local']['chunk_size'], _timeout=30)
        except s.timeout:
            pass
        self.local.close()
        self.tunnel.close()
        self._createRemoteTunnel()
        return 1

class Manager(object):
    def __init__(self,):
        pass