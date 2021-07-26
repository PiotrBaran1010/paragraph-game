import os, sys
sys.path.append(".")

from enum import Enum
from flask import Flask, render_template, request, redirect, url_for
from util import *
from model import *

app = Flask(__name__)
treeFilePath = './config/tree.json'
namesFilePath = './config/names.json'

@app.route('/')
def root():
    return render_template('start.html')

@app.route('/mode', methods = ["POST"])
def mode_select():
    global game_executor
    node_dict = TreeReader().readFromFile(treeFilePath)
    if request.form.to_dict()['mode'] == 'singleplayer':
        game_executor = GameExecutor(GameMode.SINGLEPLAYER, node_dict)
    elif request.form.to_dict()['mode'] == 'hotseats':
        game_executor = GameExecutor(GameMode.HOTSEATS, node_dict)
    elif request.form.to_dict()['mode'] == 'multiplayer':
        game_executor = GameExecutor(GameMode.MULTIPLAYER, node_dict)
    return redirect(url_for('populatechar'))

@app.route('/populatechar')
def populatechar():
    characters = CharactersReader().readFromFile(namesFilePath)
    if game_executor.game_mode == GameMode.SINGLEPLAYER:
        question = u"Select your character"
    else:
        question = u"Select player 1 character, player 2 will start as the other one"
    data = {
        "question": question,
        "id_0": characters[0]['id'],
        "name_0": characters[0]['name'],
        "avatar_0": characters[0]['avatar_path'],
        "id_1": characters[1]['id'],
        "name_1": characters[1]['name'],
        "avatar_1": characters[1]['avatar_path']
    }
    return render_template('char-select.html', data = data)

@app.route('/char', methods = ["POST"])
def character_select():
    characters = CharactersReader().readFromFile(namesFilePath)
    selected_id = int(request.form.to_dict()['char'])
    game_executor.initializePlayers(characters, selected_id)
    return redirect(url_for('game'))


@app.route('/game')
def game():
    player_name, question, children, avatar = game_executor.getCurrentGameContent()
    keys = list(children.keys())
    data = {
        "playername" : player_name.split(' ')[0],
        "question": question,
        "answer_1_key": keys[0],
        "answer_1_value": children[keys[0]],
        "avatar": avatar
    }
    if len(keys) == 1:
        return render_template('game1answer.html', data = data)
    else:
        data["answer_2_key"] = keys[1]
        data["answer_2_value"] = children[keys[1]]
        return render_template('game2answers.html', data = data)

@app.route('/process', methods = ["POST"])
def process():
    game_state, human_victory = game_executor.processPlayerAction(int(request.form.to_dict()['answer']))
    if game_state == GameState.VICTORY:
        if (game_executor.game_mode == GameMode.SINGLEPLAYER and human_victory) or game_executor.game_mode != GameMode.SINGLEPLAYER:
            display_text, player_name = game_executor.getVictorsDataToDisplay()
        elif game_executor.game_mode == GameMode.SINGLEPLAYER and not human_victory:
            display_text, player_name = game_executor.getLosersDataToDisplay()
        data = {
            "playername" : player_name,
            "text" : display_text
        }
        if game_executor.game_mode == GameMode.SINGLEPLAYER:
            return render_template('end-last.html', data = data)
        else:
            return render_template('end-first.html', data = data)
    else:
        return redirect(url_for('game'))

@app.route('/loss', methods = ["POST"])
def loss():
    display_text, player_name = game_executor.getLosersDataToDisplay()
    data = {
        "playername" : player_name,
        "text" : display_text
    }
    return render_template('end-last.html', data = data)
    
if __name__ == '__main__':
    app.run()