from network import Network
import time
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# name = input("Name: ")
net = Network("name")


def getPlayer() -> dict:
    player = {}
    p = net.send("get")
    e = p.split("||")
    for i in e:
        i = i.split(":")
        player[i[0]] = i[1]
    return player


class Player:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def guess(self, guess):
        res = net.send(f"guess||{guess.lower()}")
        self.updateUser()
        return res

    def updateUser(self):
        self.__dict__.update(getPlayer())
        self.tries = int(self.tries)
        self.guesses = json.loads(self.guesses)
        self.timer = float(self.timer)
        self.totalTime = float(self.totalTime)
        
class App(Player):
    def __init__(self, root, player: dict):
        root.title("Multiplayer Hangman")
        width = 1000
        height = 670
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height,
                                    (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        super().__init__(**player)
        x, y = 509, 239
        b=1
        self.alphabets = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", 
                         "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        self.buttons = []
        for alphabet in self.alphabets:
            self.buttons.append(tk.Button(root, text=alphabet,
                                     command=lambda x=alphabet: self.guessButton(x)))
        for yc in range(0, 4):
            for xc in range(0, 8):
                if b <= 26:
                    self.buttons[b-1].place(x=x, y=y, width=50, height=50)
                    b+=1
                x += 55
            x = 509
            y += 55
        self.updateUser()
        self.wordLabel = ttk.Label(root, text=self.guessedWord, font=("Consolas", 25), borderwidth=2, relief="solid", justify=tk.CENTER)
        self.wordLabel.place(x=566, y=573, width=330, height=43)
    
    def guessButton(self, alphabet):
        self.guess(alphabet)
        self.updateUser()
        self.wordLabel.config(text=self.guessedWord)
        buttonID = self.alphabets.index(alphabet)
        button = self.buttons[buttonID]
        button.config(state=tk.DISABLED)
        button.config(bg="#d3d3d3")
        if "_" not in self.guessedWord:
            messagebox.showinfo("You Won", "You Won!")
        elif self.tries == 0:
            messagebox.showinfo("You Lost", "You Lost!")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root, getPlayer())
    root.mainloop()
