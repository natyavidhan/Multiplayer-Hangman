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
        config = json.load(open("config.json"))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = config['host']
        self.port = config['port']
        self.server_ip = socket.gethostbyname(self.server)

        try:
            self.s.bind((self.server, self.port))
        except socket.error as e:
            print(str(e))
        self.s.listen(10)

        print("Waiting for a connection")

        self.players = {}
        self.entryAllowed = False
        self.wordList = open("words.txt", "r").read().split("\n")

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
        
        playersFrame = tk.Frame(root, borderwidth=2, relief="solid")
        
        playerListLabel = tk.Label(playersFrame, text = "Players", font=("Consolas", 30))
        playerListLabel.place(x = 0, y = 0, width = 504, height = 35)
        
        self.playerList = tk.Listbox(playersFrame, font=("Consolas", 20), selectmode="SINGLE")
        self.playerList.place(x = 18, y = 44, width = 350, height = 250)
        
        self.kickPlayerButton = tk.Button(playersFrame, text="Kick", font=("Consolas", 20), command=self.kickPlayer)
        self.kickPlayerButton.place(x = 385, y = 44, width = 100, height = 40)
        
        playersFrame.place(x = 25, y = 25, width = 508, height = 312)
        
        logLabel = tk.Label(root, text="Log", font=("Consolas", 24))
        logLabel.place(x = 25, y = 376, width = 66, height = 35)

        self.logList = tk.Listbox(root, font=("Consolas", 12), selectmode="NONE")
        self.logList.place(x = 25, y = 410, width = 948, height = 270)
        
        logListScrollbar = tk.Scrollbar(root, command=self.logList.yview)
        logListScrollbar.place(x = 983, y = 410, width=20, height=270)
        self.logList.config(yscrollcommand=logListScrollbar.set)
        
        
        serverDetails = tk.Label(root, text=f"IP: {self.server} \nPort: {self.port}", font=("Consolas", 16), justify="left")
        serverDetails.place(x = 554, y = 24)
        
        playerEntryFrame = tk.Frame(root, borderwidth=2, relief="solid")
        
        playerEntryLabel = tk.Label(playerEntryFrame, text="Player Entry", font=("Consolas", 20))
        playerEntryLabel.place(x = 0, y = 0, width = 416, height = 35)
        
        allowEntryButton = tk.Button(playerEntryFrame, text="Allow", font=("Consolas", 20), command=lambda: self.playerEntry(True))
        allowEntryButton.place(x = 80, y = 50, width = 120, height = 40)
        
        allowEntryButton = tk.Button(playerEntryFrame, text="Stop", font=("Consolas", 20), command=lambda: self.playerEntry(False))
        allowEntryButton.place(x = 215, y = 50, width = 120, height = 40)
        
        playerEntryFrame.place(x = 550, y = 95, width = 420, height = 115)
    
    def playerEntry(self, state: bool) -> None:
        self.entryAllowed = state
            
    def kickPlayer(self):
        player = self.playerList.curselection()
        if player:
            player = self.playerList.get(player)
            self.log(f"{player} has been kicked")
            del self.players[player]
    
    def entry(self):
        while True:
            conn, addr = self.s.accept()
            print(self.entryAllowed)
            if self.entryAllowed and len(self.players.keys()) < 5: 
                self.playerList.insert(tk.END, str(addr))
                self.log(f"{addr} has connected")
                start_new_thread(self.threaded_client, (conn, addr))
            else:
                conn.close()
                
    def threaded_client(self, conn, addr):
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
        while True:
            if str(addr) not in self.players:
                break
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
        try:
            self.players.pop(str(addr))
        except KeyError:
            pass
        playerIndex = self.playerList.get(0, tk.END).index(str(addr))
        self.playerList.delete(playerIndex)
        self.log(f"{addr} has disconnected")
        
    def log(self, message):
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        message = f"[{date}]: {message}"
        self.logList.insert(tk.END, message)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()