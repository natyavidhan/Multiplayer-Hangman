import socket
import json


class Network:
    def __init__(self, name, ip):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = ip.split(":")
        self.host = ip[0]
        self.port = int(ip[1])
        self.addr = (self.host, self.port)
        self.name = name
        self.user = self.connect()

    def connect(self):
        self.client.connect(self.addr)
        self.client.send(str.encode(self.name))
        data = self.client.recv(2048).decode()
        return data

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            response = self.client.recv(2048).decode()
            return response
        except socket.error as e:
            return str(e)
