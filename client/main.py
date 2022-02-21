from network import Network
import time
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

name = input("Name: ")
net = Network(name)

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
        print(self.__dict__)

# player = Player(**getPlayer())
# player.updateUser()
# while player.tries > 0:
#     if player.done == "True":
#         print("You won!")
#         break
#     guess = input("Guess: ")
#     player.guess(guess)
#     player.updateUser()
#     print(player.guessedWord)
#     time.sleep(0.5)
class App(Player):
    def __init__(self, root, player:dict):
        root.title("Multiplayer Hangman")
        width=1000
        height=670
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        super().__init__(**player)
        x, y = 509, 239
        buttons = []
        for alphabet in ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]:
            buttons.append(tk.Button(root, text=alphabet, command=lambda x=alphabet: self.guess(x)))
        for button in buttons:
            button.pack(side=tk.LEFT, padx=5, pady=5, width=49, height=49)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root, getPlayer())
    root.mainloop()