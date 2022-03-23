import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import json
from network import Network


def getPlayer(net: Network) -> dict:
    player = {}
    p = net.send("get||self")
    if p == "[WinError 10053] An established connection was aborted by the software in your host machine":
        raise TimeoutError("Connection timed out")
    return json.loads(p)


class Player:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def guess(self, guess: str):
        res = self.net.send(f"match||guess:{guess.lower()}")
        self.updateUser()
        return res

    def updateUser(self):
        self.__dict__.update(getPlayer(self.net))
        self.tries = int(self.tries)
        self.guesses = list(self.guessed)


class Enemy:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def updateEnemy(self, **kwargs):
        self.__dict__.update(kwargs)
        self.tries = int(self.tries)
        self.guesses = list(self.guessed)


class Game(Player):
    def __init__(self, root: tk.Tk, player: dict, net: Network):
        root.title("Multiplayer Hangman | Game")
        width = 1000
        height = 670
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height,
                                    (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=False, height=False)
        self.root = root
        player['net'] = net
        super().__init__(**player)
        x, y = 509, 239
        b = 1
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
                    b += 1
                x += 55
            x = 509
            y += 55
        self.updateUser()
        self.wordLabel = ttk.Label(root, text=self.guessedWord, font=(
            "Consolas", 25), borderwidth=2, relief="solid", justify="center")
        self.wordLabel.place(x=566, y=573, width=330, height=43)

        self.triesLabel = ttk.Label(root, text=f"Tries left: {str(self.tries)}", font=(
            "Consolas", 15), borderwidth=2, relief="solid", justify="center")
        self.triesLabel.place(x=631, y=496, width=200, height=41)

        self.hangmanCanvas = tk.Canvas(
            root, width=500, height=500, borderwidth=2, relief="solid")
        self.hangmanCanvas.place(x=92, y=239, width=377, height=377)

        # draw hangman
        self.hangmanCanvas.create_rectangle(84, 360, 311, 377, fill="#000000")
        self.hangmanCanvas.create_rectangle(268, 121, 287, 377, fill="#000000")
        self.hangmanCanvas.create_rectangle(
            161, 121, 161+126, 121+17, fill="#000000")
        self.hangmanCanvas.create_rectangle(
            161, 121, 161+19, 121+49, fill="#000000")
        self.enemiesFrame = tk.Frame(root)
        self.enemiesFrame.place(x=92, y=20, width=815, height=176)
        self.matchEnd = False

    def guessButton(self, alphabet: str):
        self.guess(alphabet)
        self.updateUser()
        self.wordLabel.config(text=self.guessedWord)
        self.triesLabel.config(text=f"Tries left: {str(self.tries)}")
        self.DrawHangman(self.tries)
        buttonID = self.alphabets.index(alphabet)
        button = self.buttons[buttonID]
        button.config(state=tk.DISABLED)
        button.config(bg="#e57076")
        print(self.guessedWord)
        if "_" not in self.guessedWord:
            for button in self.buttons:
                button.config(state=tk.DISABLED)
        elif self.tries == 0:
            for button in self.buttons:
                button.config(state=tk.DISABLED)

    def DrawHangman(self, triesLeft: int):
        if triesLeft < 6:
            self.hangmanCanvas.create_oval(
                140, 154, 140+62, 154+62, fill="#000000")
        if triesLeft < 5:
            self.hangmanCanvas.create_rectangle(
                166, 204, 166+10, 204+80, fill="#000000")
        if triesLeft < 4:
            self.hangmanCanvas.create_line(
                170, 205, 144, 258, fill="#000000", width=10)
        if triesLeft < 3:
            self.hangmanCanvas.create_line(
                170, 205, 202, 258, fill="#000000", width=10)
        if triesLeft < 2:
            self.hangmanCanvas.create_line(
                170, 205+78, 144, 258+78, fill="#000000", width=10)
        if triesLeft < 1:
            self.hangmanCanvas.create_line(
                170, 205+78, 202, 258+78, fill="#000000", width=10)

    def check_match(self):
        data = self.net.send("match||over")
        print(data)
        data = True if data == "true" else False
        print(data)
        if data:
            if not self.matchEnd:
                result = self.net.send("match||getAll")
                match = self.net.send("match||getMatch")
                result = json.loads(result)
                match = json.loads(match)
                resultStr = ""
                for player in result.values():
                    index = list(result.values()).index(player)
                    resultStr += f"{index+1}. {player['name']}#{player['id']} - {round(float(player['finishedTime'])-float(match['start']), 3)}\n"
                resultStr = "Winners:\n"+resultStr[:-1]
                self.matchEnd = True
                messagebox.showinfo( "Match Over", resultStr)
        else:
            self.matchEnd = False

    def loadEnemies(self):
        self.check_match()
        self.enemies = []
        enemies = self.net.send("match||getAll")
        if enemies == "[WinError 10053] An established connection was aborted by the software in your host machine":
            self.root.destroy()
            return
        elif enemies == "None":
            self.root.destroy()
            from lobby import Lobby
            root = tk.Tk()
            lobby = Lobby(root, self.net)
            lobby.checkMatch()
            root.mainloop()
        enemies = json.loads(enemies).values()
        for enemy in enemies:
            if enemy['id'] != self.id:
                self.enemies.append(Enemy(**enemy))
        x = 0
        for child in self.enemiesFrame.winfo_children():
            child.destroy()

        for enemy in self.enemies:
            enemy.hangmanFrame = tk.Frame(
                self.enemiesFrame, borderwidth=2, relief="solid")
            tk.Label(enemy.hangmanFrame, text=enemy.name, font=(
                "Consolas", 15), justify="center").place(x=0, y=33, width=173)
            tk.Label(enemy.hangmanFrame, text=enemy.guessedWord, font=(
                "Consolas", 15), justify="center").place(x=0, y=73, width=173)
            tk.Label(enemy.hangmanFrame, text=f"Tries Left: {enemy.tries}", font=(
                "Consolas", 15), justify="center").place(x=0, y=113, width=173)
            enemy.hangmanFrame.place(x=x, y=0, width=177, height=177)
            x += (305-92)
        self.root.after(1000, self.loadEnemies)