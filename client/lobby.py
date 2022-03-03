import tkinter as tk
import json

class Lobby:
    def __init__(self, root, net):
        self.root = root
        self.match = None
        self.net = net
        root.title("Multiplayer Hangman | Lobby")
        root.geometry("520x245")

        label = tk.Label(root, text="Lobby", font=("Consolas", 16))
        label.place(relx=0.5, rely=0.1, anchor="center")

        self.PlayerList = tk.Listbox(root, font=("Consolas", 12))
        self.PlayerList.place(relx=0.5, rely=0.2, anchor="center", relwidth=0.9, relheight=0.7)

        self.loadPlayers()

    def loadPlayers(self):
        players = self.net.send("get||all")
        if players == "[WinError 10053] An established connection was aborted by the software in your host machine":
            raise TimeoutError("Connection timed out")
        else:
            players = json.loads(players)
            self.PlayerList.delete(0, tk.END)
            print(players)
            for i in players.keys():
                name = players[i]["name"]
                score = players[i]["score"]
                self.PlayerList.insert(tk.END, f"{name} - {score}")
    
    def checkMatch(self):
        match = self.net.send("match||getMatch")
        if match == "[WinError 10053] An established connection was aborted by the software in your host machine":
            raise TimeoutError("Connection timed out")
        elif match == "None":
            return False
        else:
            return True
            self.match = self.net.send("get||getSelf")
            self.root.destroy()
        self.root.after(1000, self.checkMatch)