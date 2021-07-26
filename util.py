import codecs
import json
import random
from model import *

class GameExecutor():

    def __init__(self, game_mode, node_dict):
        self.node_dict = node_dict
        self.game_finished = False
        self.game_mode = game_mode
        self.path_selector = AlternatingPathSelector(self.node_dict)

    def initializePlayers(self, playersInfo, firstSelectedId):
        self.player_list = []
        start_node = self.findStartNode()
        Player1 = Player(playersInfo[0]['id'], playersInfo[0]['name'], playersInfo[0]['avatar_path'], start_node.id, True)
        if self.game_mode == GameMode.SINGLEPLAYER:
            if firstSelectedId == 0:
                Player1 = Player(playersInfo[0]['id'], playersInfo[0]['name'], playersInfo[0]['avatar_path'], start_node.id, True)
                Player2 = Player(playersInfo[1]['id'], playersInfo[1]['name'], playersInfo[1]['avatar_path'], start_node.id, False)
            else:
                Player1 = Player(playersInfo[0]['id'], playersInfo[0]['name'], playersInfo[0]['avatar_path'], start_node.id, False)
                Player2 = Player(playersInfo[1]['id'], playersInfo[1]['name'], playersInfo[1]['avatar_path'], start_node.id, True)
        else:
            Player1 = Player(playersInfo[0]['id'], playersInfo[0]['name'], playersInfo[0]['avatar_path'], start_node.id, True)
            Player2 = Player(playersInfo[1]['id'], playersInfo[1]['name'], playersInfo[1]['avatar_path'], start_node.id, True)
        self.player_list.append(Player1)
        self.player_list.append(Player2)
        if firstSelectedId == 0:
            self.player_turn = Player1
        else:
            self.player_turn = Player2

    def findStartNode(self):
        for node in self.node_dict.values():
            noParentFound = True
            for node2 in self.node_dict.values():
                try:
                    if str(node.id) in node2.children.keys():
                        noParentFound = False
                        break
                except AttributeError:
                    pass
            if noParentFound:
                return node

    def getCurrentGameContent(self):
        for node in self.node_dict.values():
            if node.id == self.player_turn.location:
                returned_children = {}
                for key in node.children.keys():
                    returned_children[key] = node.children[key].split('||')[self.player_turn.id]
                return self.player_turn.name, node.question.split('||')[self.player_turn.id], returned_children, self.player_turn.avatar

    def processPlayerAction(self, id):
        self.player_turn.moveToLocation(id)
        if isinstance(self.node_dict[id], VictoryNode):
            self.game_finished = True
            if self.game_mode == GameMode.SINGLEPLAYER and self.player_turn.humanControlled:
                return GameState.VICTORY, True
            elif self.game_mode == GameMode.SINGLEPLAYER and not self.player_turn.humanControlled:
                return GameState.VICTORY, False
            else:
                return GameState.VICTORY, None
        else:
            self.player_turn = self.getOtherPlayerObject(self.player_turn.id)
            if (not self.player_turn.humanControlled):
                return self.performMoveForComputerPlayer()
            else:
                return GameState.CONTINUE, None

    def getOtherPlayerObject(self, id):
        for player in self.player_list:
            if player.id != id:
                return player

    def performMoveForComputerPlayer(self):
        next_node = self.path_selector.getNextNode(self.player_turn.location)
        return self.processPlayerAction(next_node)

    def getVictorsDataToDisplay(self):
        if self.game_finished:
            for player in self.player_list:
                if isinstance(self.node_dict[player.location], VictoryNode):
                    if player.id == 0:
                        return self.node_dict[player.location].player0arrivedFirst.split('||')[0], player.name
                    else:
                        return self.node_dict[player.location].player1arrivedFirst.split('||')[0], player.name
    
    def getLosersDataToDisplay(self):
        if self.game_finished:
            for player in self.player_list:
                if isinstance(self.node_dict[player.location], VictoryNode):
                    if player.id == 0:
                        return self.node_dict[player.location].player0arrivedFirst.split('||')[1], self.getOtherPlayerObject(player.id).name
                    else:
                        return self.node_dict[player.location].player1arrivedFirst.split('||')[1], self.getOtherPlayerObject(player.id).name

class TreeReader():
    def readFromFile(self, filepath):
        nodeDict = {}
        with codecs.open(filepath, "r", encoding='utf-8') as f:
            data = json.load(f)
        for entry in data:
            if entry.get('0arrivedFirst'):
                nodeDict[int(entry['id'])] = VictoryNode(entry['id'], entry['0arrivedFirst'], entry['1arrivedFirst'])
            else:
                list = [(k, v) for k, v in entry['children'].items()]
                nodeDict[int(entry['id'])] = ConcreteNode(entry['id'], entry['question'], list)
        return nodeDict

class CharactersReader():
    def readFromFile(self, filepath):
        with codecs.open(filepath, "r", encoding='utf-8') as f:
            return json.load(f)

class AlternatingPathSelector():
    def __init__(self, node_dict):
        self.node_dict = node_dict
        self.perform_incorrect_step = False

    def getNextNode(self, current_id):
        if self.perform_incorrect_step:
            self.perform_incorrect_step = False
            return self.findLongestPath(current_id)[1]
        else:
            self.perform_incorrect_step = True
            return self.findShortestPath(current_id)[1]
    
    def findShortestPath(self, current_id):
        if self.isSecondToLast(current_id):
            return [current_id, self.getVictoryNodeId()]
        else:
            shortest_path_found = []
            for child in self.node_dict[current_id].children.keys():
                path_for_child = self.findShortestPath(child)
                if shortest_path_found == [] or len(path_for_child) < len(shortest_path_found):
                    shortest_path_found = path_for_child
            shortest_path_found.insert(0, current_id)
            return shortest_path_found

    def findLongestPath(self, current_id):
        if self.isSecondToLast(current_id):
            return [current_id, self.getVictoryNodeId()]
        else:
            longest_path_found = []
            for child in self.node_dict[current_id].children.keys():
                path_for_child = self.findLongestPath(child)
                if longest_path_found == [] or len(path_for_child) > len(longest_path_found):
                    longest_path_found = path_for_child
            longest_path_found.insert(0, current_id)
            return longest_path_found

    def isSecondToLast(self, current_id):
        for child in self.node_dict[current_id].children.keys():
            if isinstance(self.node_dict[child], VictoryNode):
                return True
        return False
    
    def getVictoryNodeId(self):
        for node in self.node_dict.values():
            if isinstance(node, VictoryNode):
                return node.id