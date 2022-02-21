import socket
from _thread import *
import sys
import random
import json
import time
from uuid import uuid4

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server = "localhost"
port = 5555
server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))
except socket.error as e:
    print(str(e))
s.listen(10)

print("Waiting for a connection")

players = {}
match = False
wordList = open("words.txt", "r").read().split("\n")


def threaded_client(conn, addr):
    global players

    word = random.choice(wordList)
    guesses = []
    done = False
    guessedWord = ""
    tries = 6
    timer = time.time()
    totalTime = 0
    id = str(uuid4())
    players[str(
        addr)] = f"id:{id}||name:{addr}||tries:{tries}||guesses:{json.dumps(guesses)}||guessedWord:{guessedWord}||done:{done}||timer:{timer}||totalTime:{totalTime}"
    conn.send(str.encode(players[str(addr)]))
    print(word)
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode("utf-8")
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                reply = reply.split("||")
                if reply[0] == "get":
                    conn.send(str.encode(players[str(addr)]))
                elif reply[0] == "getAll":
                    conn.send(str.encode(str(players)))
                elif reply[0] == "guess":
                    if int(players[str(addr)].split("||")[2].split(":")[1]) > 0 and players[str(addr)].split("||")[5].split(":")[1] != "True":
                        reply[1] = reply[1].lower()[0]
                        guesses.append(reply[1])
                        if reply[1] not in word:
                            tries -= 1
                        guessedWord = ""
                        for letter in word:
                            if letter in guesses:
                                guessedWord += letter
                            else:
                                guessedWord += "_"
                        
                        if tries == 0:
                            done = True
                        if guessedWord == word:
                            done = True
                            totalTime = time.time() - timer
                    player = players[str(
                        addr)] = f"id:{id}||name:{addr}||tries:{tries}||guesses:{json.dumps(guesses)}||guessedWord:{guessedWord}||done:{done}||timer:{timer}||totalTime:{totalTime}"
                    conn.send(str.encode(player))
                

        except Exception as e:
            print(e)
            break

    print("Connection Closed")
    conn.close()
    players.pop(str(addr))


while True:
    if not match:
        conn, addr = s.accept()
        print("Connected to: ", addr)
        start_new_thread(threaded_client, (conn, addr))
