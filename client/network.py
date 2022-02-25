import socket
import json


class Network:
    def __init__(self, name, ip):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip=ip.split(":")
        self.host = ip[0]
        self.port = ip[1]
        self.addr = (self.host, self.port)
        self.user = self.connect()
        self.name = name 

    '''
    Connect to the server and print the message received
    :return: The server's response to the client's connection request.
    '''
    def connect(self):
        self.client.connect(self.addr)
        data = self.client.recv(2048).decode()
        self.client.send(str.encode(f"{self.name}"))
        # print(data)
        return data

    def send(self, data):
        '''
        Send data to the client
        
        :param data: The data to send to the server
        :return: The response from the server.
        '''
        try:
            self.client.send(str.encode(data))
            response = self.client.recv(2048).decode()
            return response
        except socket.error as e:
            return str(e)
    
    def loadData(self, data:str) -> dict:
        data=data.split("||")
        data_ = {}
        for i in data:
            i=i.split(":")
            data_[i[0]]=i[1]
        return data_
    
    def packData(self, data:dict) -> str:
        data_ = ""
        for i in data.keys():
            data_ += f"{i}:{data[i]}||"
        return data_[:-2]
    
    def getSelf(self):
        playerStr = self.send("get||self")
        return self.loadData(playerStr)
        