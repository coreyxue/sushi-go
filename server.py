from flask import Flask, render_template, request, redirect, url_for
from enum import Enum
import random
import uuid;



app = Flask(__name__)

def pupolateCardDeck():
    cardDeck = []
    cardDeck.extend([Card('Tempura', 'tempura') for i in range(14)])
    cardDeck.extend([Card('Sashimi', 'sashimi') for i in range(14)])
    cardDeck.extend([Card('Dumpling', 'dumpling') for i in range(14)])
    cardDeck.extend([Card('2 Maki rolls', 'maki_rolls_2') for i in range(12)])
    cardDeck.extend([Card('3 Maki rolls', 'maki_rolls_3') for i in range(8)])
    cardDeck.extend([Card('1 Maki rolls', 'maki_rolls_1') for i in range(6)])
    cardDeck.extend([Card('Salmon Nigiri', 'salmon_nigiri') for i in range(10)])
    cardDeck.extend([Card('Squid Nigiri', 'squid_nigiri') for i in range(5)])
    cardDeck.extend([Card('Egg Nigiri', 'egg_nigiri') for i in range(5)])
    cardDeck.extend([Card('Pudding', 'pudding') for i in range(10)])
    cardDeck.extend([Card('Wasabi', 'wasabi') for i in range(5)])
    cardDeck.extend([Card('Chopsticks', 'chopsticks') for i in range(4)])

    random.shuffle(cardDeck)
    random.shuffle(cardDeck)
    random.shuffle(cardDeck)
    random.shuffle(cardDeck)
    random.shuffle(cardDeck)
    random.shuffle(cardDeck)

    return cardDeck

class PlayerStatus(Enum):
    WATING = "WATING"
    PLAYING = "PLAYING"

class GameStatus(Enum):
    NEW_ROUND = "NEW_ROUND"
    TURN_STARTED = "TURN_STARTED"
    NEW_TURN = "NEW_TURN"

class Card:
    def __init__(self, name, alias):
        self.id = uuid.uuid4().hex.upper()[0:6]
        self.name = name
        self.alias = alias
        self.topped = None

    def topped(self, card):
        self.topped = card

class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.currentTurnCards = []
        self.handCards = []
        self.status = PlayerStatus.WATING

class Game:
    def __init__(self, numOfPlayers):
        self.numOfPlayers = numOfPlayers
        self.cardDeck = pupolateCardDeck()
        self.roundCount = 0
        self.turnCount = 0
        self.players = {}
        self.turnToCards = {}
        self.status = GameStatus.NEW_ROUND

    def add_player(self, player):
        self.players[player.id] = player

    def getCardsToStartARound(self):
        if self.numOfPlayers == 2:
            cards = self.cardDeck[:10]
            self.cardDeck = self.cardDeck[10:]
            return cards
        elif self.numOfPlayers == 3:
            cards = self.cardDeck[:9]
            self.cardDeck = self.cardDeck[9:]
            return cards
        elif self.numOfPlayers == 4:
            cards = self.cardDeck[:8]
            self.cardDeck = self.cardDeck[8:]
            return cards
        elif self.numOfPlayers ==5:
            cards = self.cardDeck[:7]
            self.cardDeck = self.cardDeck[7:]
            return cards

    def getPrevioudPlayerId(self, playerId):
        if playerId == 1:
            return self.numOfPlayers
        elif playerId == self.numOfPlayers:
            return 1
        else:
            return playerId - 1

    def handOver(self, playerId):
        self.players[playerId].currentTurnCards = self.players[getPrevioudPlayerId(playerId)].currentTurnCards

    def allPlayersJoined(self):
        return len(self.players) == self.numOfPlayers

    def updateStatus(self):
        if self.status == GameStatus.NEW_ROUND:
            if len(self.players) != self.numOfPlayers:
                return
            allPlayersHaveCards = True
            for playerId in self.players.keys():
                if len(self.players[playerId].currentTurnCards) == 0:
                    allPlayersHaveCards = False
            if allPlayersHaveCards:
                self.status = GameStatus.TURN_STARTED
        elif self.status == GameStatus.TURN_STARTED:
            allPlayersAreWaiting = True
            isRoundEnd = True
            for playerId in self.players.keys():
                if self.players[playerId].status != PlayerStatus.WATING:
                    allPlayersAreWaiting = False
                    return
                if self.players[playerId].currentTurnCards != []:
                    isRoundEnd = False
            if isRoundEnd:
                self.status = GameStatus.NEW_ROUND
            if allPlayersAreWaiting:
                self.status = GameStatus.NEW_TURN



@app.route('/')
@app.route("/start", methods=['GET', 'POST'])
def start():
    global game
    if request.method == 'POST':
        if 'game' not in globals():
            game = Game(int(request.form['number_of_players']))
        playerName = request.form['player_name']
        playerId = len(game.players) + 1
        game.add_player(Player(playerId, playerName))

        return redirect(url_for('turn', playerId = playerId))
    else:
        if 'game' in globals():
            return render_template('home.html', numOfPlayers = len(game.players), gameSize = game.numOfPlayers)
        else:
            return render_template('home.html', numOfPlayers = 0, gameSize = 0)

@app.route('/turn', methods=['GET'])
def turn():
    global game
    playerId = int(request.args.get('playerId'))
    if not game.allPlayersJoined():
        return render_template('turn.html', pageStatus = 'waiting',  players = game.players, playerId = playerId, gameStatus = game.status)
    if game.status == GameStatus.NEW_ROUND:
        cards = game.getCardsToStartARound()
        game.turnToCards[playerId] = cards
        game.players[playerId].currentTurnCards = cards
        game.players[playerId].status = PlayerStatus.PLAYING
    game.updateStatus()
    return render_template('turn.html', pageStatus = 'playing', players = game.players, gameSize = game.numOfPlayers, playerId = playerId, gameStatus = game.status)


@app.route('/turn_commit/<playerId>', methods=['POST'])
def turn_commit(playerId):
    global game
    playerId = int(playerId)
    player = game.players[playerId]
    player.status = PlayerStatus.WATING
    for card in game.turnToCards[playerId]:
        if request.form.get(card.id) != None:
            player.handCards.append(card)
            print(player.handCards)
            player.currentTurnCards.remove(card)
            print(player.currentTurnCards)
    game.turnToCards[playerId] = player.currentTurnCards
    player.currentTurnCards = []
    return redirect(url_for('turn', playerId = playerId))