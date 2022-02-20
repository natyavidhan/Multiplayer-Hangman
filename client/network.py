import socket
import json


class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        config = json.load(open("config.json"))
        self.host = config["host"]
        self.port = config["port"]
        self.addr = (self.host, self.port)
        self.user = self.connect()

    '''
    Connect to the server and print the message received
    :return: The server's response to the client's connection request.
    '''
    def connect(self):
        self.client.connect(self.addr)
        data = self.client.recv(2048).decode()
        print(data)
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