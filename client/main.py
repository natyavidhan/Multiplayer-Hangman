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

class Enemy:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        
    def updateEnemy(self, **kwargs):
        self.__dict__.update(kwargs)
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
        self.root = root
        super().__init__(**player)
        x, y = 509, 239
        b=1
        self.alphabets = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", 
                         "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]
        self.buttons = []
        for alphabet in self.alphabets:
            self.buttons.append(tk.Button(root, text=alphabet,
                                     command=lambda x=alphabet: self.guessButton(x), font=("Consolas", 25)))
        for yc in range(0, 4):
            for xc in range(0, 8):
                if b <= 26:
                    self.buttons[b-1].place(x=x, y=y, width=50, height=50)
                    b+=1
                x += 55
            x = 509
            y += 55
        self.updateUser()
        self.wordLabel = ttk.Label(root, text=self.guessedWord, font=("Consolas", 25), borderwidth=2, relief="solid", justify="center")
        self.wordLabel.place(x=566, y=573, width=330, height=43)
        
        self.triesLabel = ttk.Label(root, text=f"Tries left: {str(self.tries)}", font=("Consolas", 15), borderwidth=2, relief="solid", justify="center")
        self.triesLabel.place(x=631, y=496, width=200, height=41)
        
        self.hangmanCanvas = tk.Canvas(root, width=500, height=500, borderwidth=2, relief="solid")
        self.hangmanCanvas.place(x=92, y=239, width=377, height=377)
        
        #draw hangman
        self.hangmanCanvas.create_rectangle(84, 360, 311, 377, fill="#000000")
        self.hangmanCanvas.create_rectangle(268, 121, 287, 377, fill="#000000")
        self.hangmanCanvas.create_rectangle(161, 121, 161+126, 121+17, fill="#000000")
        self.hangmanCanvas.create_rectangle(161, 121, 161+19, 121+49, fill="#000000")
    
    def guessButton(self, alphabet):
        self.guess(alphabet)
        self.updateUser()
        self.wordLabel.config(text=self.guessedWord)
        self.triesLabel.config(text=f"Tries left: {str(self.tries)}")
        self.DrawHangman(self.tries)
        buttonID = self.alphabets.index(alphabet)
        button = self.buttons[buttonID]
        button.config(state=tk.DISABLED)
        button.config(bg="#e57076")
        if "_" not in self.guessedWord:
            messagebox.showinfo("You Won", "You Won! \nTime Taken: " + str(round(time.time() - self.timer, 2)) + " seconds")
        elif self.tries == 0:
            messagebox.showinfo("You Lost", "You Lost!")
    
    def DrawHangman(self, triesLeft):
        if triesLeft < 6:
            self.hangmanCanvas.create_oval(140, 154, 140+62, 154+62, fill="#000000")
        if triesLeft < 5:
            self.hangmanCanvas.create_rectangle(166, 204, 166+10, 204+80, fill="#000000")
        if triesLeft < 4:
            self.hangmanCanvas.create_line(170, 205, 144, 258, fill="#000000", width=10)
        if triesLeft < 3:
            self.hangmanCanvas.create_line(170, 205, 202, 258, fill="#000000", width=10)
        if triesLeft < 2:
            self.hangmanCanvas.create_line(170, 205+78, 144, 258+78, fill="#000000", width=10)
        if triesLeft < 1:
            self.hangmanCanvas.create_line(170, 205+78, 202, 258+78, fill="#000000", width=10)

    def loadEnemies(self):
        self.enemies = []
        enemies = net.send("getAll")
        enemies = enemies.split("|||")[:-1]
        for enemy in enemies:
            if enemy.split("||")[0].split(":")[1] != self.id:
                enemy_ = {}
                e = enemy.split("||")
                for i in e:
                    i = i.split(":")
                    enemy_[i[0]] = i[1]
                self.enemies.append(Enemy(**enemy_))
        print([enemy.__dict__ for enemy in self.enemies])
        self.root.after(1000, self.loadEnemies)
            
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root, getPlayer())
    app.loadEnemies()
    root.mainloop()
