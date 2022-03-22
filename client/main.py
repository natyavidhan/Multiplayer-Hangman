from network import Network
import time
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from lobby import Lobby

# net = Network("name")
net = None


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Hangman")
        self.root.geometry("520x245")
        self.root.resizable(False, False)

        title = tk.Label(root, text="Multiplayer Hangman",
                            font=("Consolas", 26))
        title.place(x=88, y=35)

        namelabel = tk.Label(root, text="Name", font=("Consolas", 14))
        namelabel.place(x=80, y=109)

        iplabel = tk.Label(root, text="IP", font=("Consolas", 14))
        iplabel.place(x=80, y=149, width=64)

        self.nameinput = tk.Entry(root, font=("Consolas", 18))
        self.nameinput.place(x=164, y=106, width=250, height=33)
        self.nameinput.insert(0, "Player")
        self.ipInput = tk.Entry(root, font=("Consolas", 18))
        self.ipInput.place(x=164, y=140, width=250, height=33)
        self.ipInput.insert(0, "localhost:5555")

        joinServerButton = tk.Button(root, text="Join", font=(
            "Consolas", 14), command=self.joinServer)
        joinServerButton.place(x=233, y=200, width=53, height=33)

    def joinServer(self):
        global net
        ip = self.ipInput.get()
        name = self.nameinput.get()
        net = Network(name, ip)
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
    if net != None:
        root = tk.Tk()
        lobby = Lobby(root, net)
        lobby.checkMatch()
        root.mainloop()
