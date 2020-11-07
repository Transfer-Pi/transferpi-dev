#!/usr/bin/env python3
from datetime import datetime
from json import loads, dumps
from socket import error as _error
from concurrent.futures import ThreadPoolExecutor
from sys import exit
from time import sleep
from os import environ, path as pathlib
from logger import Logger

import socket as s
import sys

"""
App Config

linux/unix : ⭕
windows    : ✔️
mac        : ⭕
"""

header_data_types = {
    'content_length': int,
    "chunk_size": int
}


_PATH = pathlib.join(environ['USERPROFILE'], ".transferpi")
_LOGGER = Logger(out=pathlib.join(_PATH, "logs", "tunnel_logs.txt"))

try:
    _CONFIG = loads(open(pathlib.join(_PATH, "config.json"), "r").read())
except:
    exit(print("Error, Config Found !"))


def http_message(message: str) -> str:
    header = Header()
    header.status = "HTTP/1.1 200 OK"
    header.access_control_allow_origin = "*"
    header.connection = "Keep-Alive"
    header.content_type = "text/html; charset=utf-8"
    header.keep_alive: "timeout=1, max=999"
    header.data = message
    header.content_length = len(header.data)
    return str(header).encode()


def readStreamWithoutContentSize(stream: s.socket, timeout: float = 1) -> str:
    data = stream.recv(8)
    stream.settimeout(timeout)

    try:
        while True:
            data += stream.recv(8)
    except s.error:
        stream.settimeout(None)

    return data


def readHeader(stream):
    start = stream.recv(4)
    while start[-4:] != '\r\n\r\n'.encode():
        try:
            start += stream.recv(1)
        except stream.error as e:
            print(f"[ERROR] {e}")
    return str(start[:-4], encoding="utf8"), start


def pump(x: s.socket, y: s.socket, chunk_size: int, timeout: int = 1, _timeout=None) -> bool:
    """
    x : read from
    y : send to
    """
    x.settimeout(_timeout)
    y.send(x.recv(chunk_size))
    x.settimeout(timeout)
    try:
        while (bit := x.recv(chunk_size)):
            y.send(bit)
    except s.error:
        pass
    x.settimeout(None)


class Header:
    def __init__(self, **kwargs):
        self.data = ""
        self.access_control_allow_origin = "*"
        self.connection = None
        self.content_length = None
        self.content_type = None
        self.keep_alive = None
        self.status = None
        self.host = None
        self.chunk_size = None
        self.filename = None
        self.server = "TPI1.0.0"
        self.content_encoding = None
        self.location = None
        self.content_disposition = None
        self.x_sendfile = None
        self.date = str(datetime.now())
        for i in kwargs:
            self.__dict__[i] = kwargs[i]

    def __str__(self,):
        header = self.status+"\r\n"
        for h in self.__dict__:
            if h not in ["status", "data", "encode"] and self.__dict__[h]:
                header += f"{h.replace('_','-').title()}: {self.__dict__[h]}\r\n"
        return header+"\r\n" + self.data

    def __repr__(self,):
        return self.__str__()

    def encode(self):
        return self.__str__().encode()


class ParseHeader:
    def __init__(self, header):
        self.string = header
        header = header.split("\r\n")
        method, status = header.pop(0).split(" ")[:2]
        self.status = int(status)
        self.method = method
        self.path = None
        self.access_control_allow_origin = "*"
        self.connection = None
        self.content_length = None
        self.content_type = None
        self.keep_alive = None
        self.chunk_size = None
        self.filename = None
        self.server = None
        self.content_encoding = None
        self.content_disposition = None
        self.location = None
        self.date = None

        for i in header:
            key, val = i.split(": ")
            self.__dict__[key.lower().replace("-", "_")] = val
        self.__settypes__()

    def __getitem__(self, key):
        try:
            return self.__dict__[key]
        except:
            raise KeyError

    def __settypes__(self,):
        for i in header_data_types:
            if self.__dict__[i]:
                self.__dict__[i] = header_data_types[i](self.__dict__[i])

    def __str__(self,):
        return self.string

    def __repr__(self):
        return self.string


class JSON:
    def __init__(self, data):
        self._data = data
        for i in data:
            if type(data[i]) == dict:
                self.__dict__[i] = JSON(data[i])
            else:
                self.__dict__[i] = data[i]

    def __str__(self):
        return self._data.__str__()

    def __repr__(self):
        return self._data.__repr__()


class Tunnel:
    def __init__(self, _id: int, config: dict, session: dict):
        self._id = _id
        self._config = config
        self._session = session
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
            header.status = "CREATE /tunnel HTTP/1.1"
            header.host = "create.tunnel"
            header.content_type = "application/json"
            header.data = dumps({
                "username": self._config['subdomain'],
                "id": self._id,
                "session": self._session['_id']
            })
            header.content_length = len(header.data)
            self.tunnel.sendall(str(header).encode())

            header = ParseHeader(readHeader(self.tunnel,)[0])
            self.session = loads(
                str(readStreamWithoutContentSize(self.tunnel), encoding="utf-8"))
            if self.session['status']:
                _LOGGER.success(f"Tunnel Connected With Id {self._id}")
            else:
                _LOGGER.error(self.session['message'])

        except:
            sleep(1)
            _LOGGER.error(f'Error Connectiong To Host Retrying ...')
            self.tunnel.close()
            self._createRemoteTunnel(recon=recon+1)

    def _createLocalTunnel(self,):
        try:
            self.local = s.socket(s.AF_INET, s.SOCK_STREAM)
            self.local.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
            self.local.settimeout(1)
            self.local.connect((
                "localhost",
                self._config['server_config']['local']['port']
            ))
        except:
            _LOGGER.error('Error Connecting Fileserver Retrying...')
            self.local.close()
            sleep(1)
            self._createLocalTunnel()

    def forward(self,):
        self._createLocalTunnel()
        try:
            pump(self.tunnel, self.local,
                 _CONFIG['server_config']['local']['chunk_size'], _timeout=30)
            pump(self.local, self.tunnel,
                 _CONFIG['server_config']['local']['chunk_size'], _timeout=30)
        except s.timeout:
            pass

        self.local.close()
        self.tunnel.close()
        self._createRemoteTunnel()
        return 1


def createTunnel(kwargs):
    tunnel = Tunnel(**kwargs)
    while True:
        try:
            tunnel.forward()
        except KeyboardInterrupt:
            exit(0)
    exit(0)


def init():
    header = Header()
    header.status = "INIT /tunnel HTTP/1.1"
    header.host = "create.tunnel"
    header.content_type = "application/json"
    header.data = dumps(
        {"username": _CONFIG['subdomain'], "key": _CONFIG['account_keys']['private']})
    header.content_length = len(header.data)

    tunnel = s.socket(s.AF_INET, s.SOCK_STREAM)
    tunnel.setsockopt(s.SOL_SOCKET, s.SO_REUSEADDR, 1)
    tunnel.settimeout(None)
    tunnel.connect((
        _CONFIG['server_config']['remote']['host'],
        _CONFIG['server_config']['remote']['port']
    ))

    tunnel.sendall(str(header).encode())
    header = ParseHeader(readHeader(tunnel,)[0])
    session = loads(
        str(readStreamWithoutContentSize(tunnel), encoding="utf-8"))

    return session


def main():
    print(f"* Remote Host : {_CONFIG['server_config']['remote']['host']}")
    print(f"* Subdomain  : {_CONFIG['subdomain']}")
    print(f"* Remote Port : {_CONFIG['server_config']['remote']['port']}")
    print(
        f"* Number Of Pools : {_CONFIG['server_config']['local']['n_pools']}")

    print("* Authenticating Account")
    session = init()
    if session['status']:
        print("* Authentication Successful")
        with ThreadPoolExecutor(max_workers=_CONFIG['server_config']['local']['n_pools']) as executer:
            thread_config = [{"_id": i, "config": _CONFIG, "session": session['session']}
                             for i in range(_CONFIG['server_config']['local']['n_pools'])]
            res = executer.map(createTunnel, thread_config)
            for i in res:
                print(i)
    else:
        exit(_LOGGER.error(session['message']))


if __name__ == "__main__":
    main()
