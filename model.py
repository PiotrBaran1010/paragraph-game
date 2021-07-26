import json
from enum import Enum

class GameMode(Enum):
    SINGLEPLAYER = 1
    HOTSEATS = 2
    MULTIPLAYER = 3

class GameState(Enum):
    VICTORY = 1
    CONTINUE = 2

class Player():
    def __init__(self, id, name, avatar, startLocation, humanControlled):
        self.location = 0
        self.history = []
        self.id = id
        self.humanControlled = humanControlled
        self.name = name
        self.avatar = avatar
        self.moveToLocation(startLocation)

    def moveToLocation(self, location):
        self.location = location
        self.history.append(location)

class GenericNode ():
    def __init__(self, id):
        self.id = id

class ConcreteNode(GenericNode):
    def __init__(self, id, question, children):
        self.question = question
        self.children = {}
        for child in children:
            self.children[int(child[0])] = child[1]
        super().__init__(id)
    
    def __repr__(self):
        return str(self.id) + ' ' + str(self.question) + ' ' + str(self.children)

class VictoryNode(GenericNode):
    def __init__(self, id, player0arrivedFirst, player1arrivedFirst):
        self.player0arrivedFirst = player0arrivedFirst
        self.player1arrivedFirst = player1arrivedFirst
        super().__init__(id)