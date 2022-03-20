import tkinter as tk
import json
from game import Game

class Lobby:
    def __init__(self, root, net):
        self.root = root
        self.match = None
        self.net = net
        self.root.title("Multiplayer Hangman | Lobby")
        self.root.geometry("520x245")
        self.root.resizable(False, False)

        label = tk.Label(root, text="Lobby", font=("Consolas", 16))
        label.place(relx=0.5, rely=0.1, anchor="center")

        self.PlayerList = tk.Listbox(root, font=("Consolas", 12))
        self.PlayerList.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.5)

        self.loadPlayers()

    def loadPlayers(self):
        players = self.net.send("get||all")
        if players == "[WinError 10053] An established connection was aborted by the software in your host machine":
            self.root.destroy()
        else:
            players = json.loads(players)
            self.PlayerList.delete(0, tk.END)
            for i in players.keys():
                name = players[i]["name"]
                score = players[i]["score"]
                self.PlayerList.insert(tk.END, f"{name} - {score}")
    
    def checkMatch(self):
        self.loadPlayers()
        match = self.net.send("match||getMatch")
        if match == "[WinError 10053] An established connection was aborted by the software in your host machine":
            self.root.destroy()
            raise TimeoutError("Connection timed out")
        elif match == "None":
            pass
        else:
            self.match = self.net.send("get||getSelf")
            root = tk.Tk()
            game = Game(root, self.match)
            root.mainloop()
        self.root.after(1000, self.checkMatch)