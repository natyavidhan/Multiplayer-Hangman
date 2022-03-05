import socket
from _thread import *
import sys
import random
import json
import time
from uuid import uuid4
from datetime import datetime
import tkinter as tk


class Match:
    def __init__(self, players: dict):
        self.start = time.time()
        self.players = players
        self.wordlist = open("words.txt", "r").read().split("\n")
        for player in self.players.keys():
            self.players[player][word] = self.assignWord()
            self.players[player][guessed] = []
            self.players[player][finished] = False
            self.players[player][guessedWord] = "".join(
                ["_" for i in range(len(player.word))])
            self.players[player][tries] = 6

    def assignWord(self) -> str:
        return random.choice(self.wordlist)

    def checkGuess(self, playerAddr: str, guess: str):
        player = self.players[playerAddr]
        player.guessed.append(guess)
        if guess not in player.word:
            player.tries -= 1

        player.guessedWord = ""
        for letter in player.word:
            if letter in player.guessed:
                player.guessedWord += letter.upper()
            else:
                player.guessedWord += "_"
            player.guessedWord += " "

    def getplayer(self, playerAddr: str) -> dict:
        player = self.players[playerAddr]
        return player

    def getAll(self) -> dict:
        return self.players

    def getMatch(self) -> dict:
        match = {}
        match["players"] = self.players
        match["start"] = self.start
        return match


class Server:
    def __init__(self):
        config = json.load(open("config.json"))
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server = config["host"]
        self.port = config["port"]
        self.server_ip = socket.gethostbyname(self.server)

        try:
            self.s.bind((self.server, self.port))
        except socket.error as e:
            print(str(e))
        self.s.listen(10)

        print("Waiting for a connection")

        self.players = {}
        self.entryAllowed = True
        self.match = None
        self.matchOn = False
        self.wordList = open("words.txt", "r").read().split("\n")

    def generateID(self) -> str:
        return "".join(random.choice("0123456789ABCDEF") for i in range(5))


class App(Server):
    def __init__(self, root: tk.Tk):
        root.title("Multiplayer Hangman Server")
        width = 1000
        height = 700
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = "%dx%d+%d+%d" % (
            width,
            height,
            (screenwidth - width) / 2,
            (screenheight - height) / 2,
        )
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        self.root = root
        super().__init__()
        start_new_thread(self.entry, ())

        playersFrame = tk.Frame(root, borderwidth=2, relief="solid")

        playerListLabel = tk.Label(
            playersFrame, text="Players", font=("Consolas", 30))
        playerListLabel.place(x=0, y=0, width=504, height=35)

        self.playerList = tk.Listbox(
            playersFrame, font=("Consolas", 20), selectmode="SINGLE"
        )
        self.playerList.place(x=18, y=44, width=350, height=250)

        self.kickPlayerButton = tk.Button(
            playersFrame, text="Kick", font=("Consolas", 20), command=self.kickPlayer
        )
        self.kickPlayerButton.place(x=385, y=44, width=100, height=40)

        playersFrame.place(x=25, y=25, width=508, height=312)

        logLabel = tk.Label(root, text="Log", font=("Consolas", 24))
        logLabel.place(x=25, y=376, width=66, height=35)

        self.logList = tk.Listbox(root, font=(
            "Consolas", 12), selectmode="NONE")
        self.logList.place(x=25, y=410, width=948, height=270)

        logListScrollbar = tk.Scrollbar(root, command=self.logList.yview)
        logListScrollbar.place(x=983, y=410, width=20, height=270)
        self.logList.config(yscrollcommand=logListScrollbar.set)

        serverDetails = tk.Label(
            root,
            text=f"IP: {self.server} \nPort: {self.port}",
            font=("Consolas", 16),
            justify="left",
        )
        serverDetails.place(x=554, y=24)

        playerEntryFrame = tk.Frame(root, borderwidth=2, relief="solid")

        playerEntryLabel = tk.Label(
            playerEntryFrame, text="Player Entry", font=("Consolas", 20)
        )
        playerEntryLabel.place(x=0, y=0, width=416, height=35)

        allowEntryButton = tk.Button(
            playerEntryFrame,
            text="Allow",
            font=("Consolas", 20),
            command=lambda: self.playerEntry(True),
        )
        allowEntryButton.place(x=80, y=50, width=120, height=40)

        allowEntryButton = tk.Button(
            playerEntryFrame,
            text="Stop",
            font=("Consolas", 20),
            command=lambda: self.playerEntry(False),
        )
        allowEntryButton.place(x=215, y=50, width=120, height=40)

        playerEntryFrame.place(x=550, y=95, width=420, height=115)

        self.match = None

    def playerEntry(self, state: bool) -> None:
        self.entryAllowed = state
        if state:
            self.log("Player entry Allowed")
        else:
            self.log("Player entry Denied")

    def kickPlayer(self) -> None:
        player = self.playerList.curselection()
        if player:
            player = self.playerList.get(player)
            for addr in self.players.keys():
                if self.players[addr]["name"]+"#"+self.players[addr]["id"] == player:
                    self.log(f"{player} has been kicked")
                    self.players.pop(addr)
                    break

    def entry(self) -> None:
        while True:
            conn, addr = self.s.accept()
            if self.entryAllowed and len(self.players.keys()) < 5 and not self.matchOn:
                start_new_thread(self.threaded_client, (conn, addr))
            else:
                conn.close()

    def startMatch(self) -> None:
        if self.match == None:
            self.match = Match(self.players)

    def threaded_client(self, conn, addr) -> None:
        def send(data) -> None:
            conn.send(str.encode(json.dumps(data)))

        name = conn.recv(1024).decode("utf-8")
        id_ = self.generateID()
        self.players[str(addr)] = {
            "id": id_,
            "name": name,
            "addr": addr,
            "score": 0
        }
        send(self.players[str(addr)])
        self.playerList.insert(tk.END, str(f"{name}#{id_}"))
        self.log(f"{name}#{id_} has connected")
        
        while True:
            if str(addr) not in self.players:
                break
            try:
                data = conn.recv(2048)
                reply = data.decode("utf-8")
                if not data:
                    conn.send(str.encode("Goodbye"))
                    break
                
                command, value = reply.split("||")
                if command == "get":
                    if value == "self":
                        send(self.players[str(addr)])
                    elif value == "all":
                        send(self.players)
                        
                elif command == "match":
                    if self.match != None:
                        if value == "getSelf":
                            send(self.match.getplayer(str(addr)))
                        elif value == "getAll":
                            send(conn, self.match.getplayers())
                        elif value == "getMatch":
                            send(conn, self.match.getmatch())
                            
                    else:
                        conn.send(str.encode("None"))

            except Exception as e:
                traceback = sys.exc_info()[2]
                print(traceback)
                break

        conn.close()

        try:
            self.players.pop(str(addr))
        except KeyError:
            pass

        self.playerList.delete(self.playerList.get(
            0, tk.END).index(f"{name}#{id_}"))
        self.log(f"{name}#{id_} has disconnected")

    def log(self, message: str) -> None:
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        message = f"[{date}]: {message}"
        self.logList.insert(tk.END, message)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
