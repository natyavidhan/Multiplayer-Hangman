from network import Network
import time
import json

net = Network()

def getPlayer():
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
        return net.send(f"guess||{guess}")
    
    def updateUser(self):
        self.__dict__.update(getPlayer())
        self.tries = int(self.tries)
        self.guesses = json.loads(self.guesses)
        self.timer = float(self.timer)
        self.totalTime = float(self.totalTime)
        print(self.__dict__)

player = Player(**getPlayer())
player.updateUser()
while player.tries > 0:
    if player.done == "True":
        print("You won!")
        break
    guess = input("Guess: ")
    player.guess(guess)
    player.updateUser()
    print(player.guessedWord)
    time.sleep(0.5)