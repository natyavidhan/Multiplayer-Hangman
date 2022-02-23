import socket
from _thread import *
import sys
import random
import json
import time
from uuid import uuid4
from datetime import datetime
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
class Server:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = "localhost"
        self.port = 5555
        self.server_ip = socket.gethostbyname(self.server)

        try:
            self.s.bind((self.server, self.port))
        except socket.error as e:
            print(str(e))
        self.s.listen(10)

        print("Waiting for a connection")

        self.players = {}
        self.match = False
        self.wordList = open("words.txt", "r").read().split("\n")


    def threaded_client(self, conn, addr):
        global players

        word = random.choice(self.wordList)
        guesses = []
        done = False
        guessedWord = ""
        tries = 6
        timer = time.time()
        totalTime = 0
        id = str(uuid4())
        for letter in word:
            if letter in guesses:
                guessedWord += letter.upper()
            else:
                guessedWord += "_"
            guessedWord += " "
        self.players[str(
            addr)] = f"id:{id}||name:{addr}||tries:{tries}||guesses:{json.dumps(guesses)}||guessedWord:{guessedWord}||done:{done}||timer:{timer}||totalTime:{totalTime}"
        conn.send(str.encode(self.players[str(addr)]))
        print(word)
        print(guessedWord)
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
                        conn.send(str.encode(self.players[str(addr)]))
                    elif reply[0] == "getAll":
                        # print(players)
                        p = ""
                        for pl in self.players.values():
                            p += pl + "|||"
                        conn.send(str.encode(str(p)))
                    elif reply[0] == "guess":
                        if (int(self.players[str(addr)].split("||")[2].split(":")[1]) > 0 
                            and self.players[str(addr)].split("||")[5].split(":")[1] != "True"):
                            reply[1] = reply[1].lower()[0]
                            guesses.append(reply[1])
                            if reply[1] not in word:
                                tries -= 1
                            guessedWord = ""
                            for letter in word:
                                if letter in guesses:
                                    guessedWord += letter.upper()
                                else:
                                    guessedWord += "_"
                                guessedWord += " "

                            if tries == 0:
                                done = True
                            if guessedWord == word:
                                done = True
                                totalTime = time.time() - timer
                        player = self.players[str(
                            addr)] = f"id:{id}||name:{addr}||tries:{tries}||guesses:{json.dumps(guesses)}||guessedWord:{guessedWord}||done:{done}||timer:{timer}||totalTime:{totalTime}"
                        conn.send(str.encode(player))

            except Exception as e:
                print(e)
                break

        print("Connection Closed")
        conn.close()
        players.pop(str(addr))

    def entry(self):
        while True:
            if not self.match:
                conn, addr = self.s.accept()
                print("Connected to: ", addr, "at: ", datetime.now())
                start_new_thread(self.threaded_client, (conn, addr))

class App(Server):
    def __init__(self, root):
        root.title("Multiplayer Hangman Server")
        width = 1000
        height = 700
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height,
                                    (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        self.root = root
        super().__init__()
        start_new_thread(self.entry, ())

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()