import tkinter as tk


class Lobby:
    def __init__(self, root, match, net):
        self.root = root
        self.match = match
        self.net = net
        root.title("Multiplayer Hangman | Lobby")
        root.geometry("520x245")

        label = tk.Label(root, text="Lobby", font=("Consolas", 16))
        label.place(relx=0.5, rely=0.05, anchor="center")

        self.PlayerList = tk.Listbox(root, font=("Consolas", 12))
        self.PlayerList.place(relx=0.5, rely=0.2, anchor="center")

        self.loadPlayers()

    def loadString(self, data):
        return_ = {}
        for i in data.split("||"):
            i = i.split(":")
            return_[i[0]] = i[1]
        return return_

    def loadPlayers(self):
        players = self.net.send("get||all")
        if players == "[WinError 10053] An established connection was aborted by the software in your host machine":
            raise TimeoutError("Connection timed out")
        else:
            players = self.loadString(players)
            self.PlayerList.delete(0, tk.END)
            for i in players.keys():
                name = players[i]["name"]
                score = players[i]["score"]
                self.PlayerList.insert(tk.END, f"{name} - {score}")
