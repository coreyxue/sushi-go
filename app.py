from flask import Flask, render_template, request, redirect, url_for
from enum import Enum
import random
import uuid



app = Flask(__name__, static_url_path='', static_folder='C:\\Users\\Corey\\Desktop\\proj\\sushi-go\\app\\static')
#app = Flask(__name__, static_url_path='')

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
    END = "END"

class Card:
    def __init__(self, name, alias):
        self.id = uuid.uuid4().hex.upper()[0:6]
        self.name = name
        self.alias = alias
        self.topping = None

    def __repr__(self):
        return "id: " + str(self.id) + " " + str(self.alias)

    def __lt__(self, other):
        return str(self.alias) < str(other.alias)

    def __gt__(self, other):
        return str(self.alias) > str(other.alias)

    def toTop(self, card):
        self.topping = card

class Player:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.currentTurnCards = []
        self.handCards = []
        self.status = PlayerStatus.WATING
        self.score = 0

    def haveChopsticks(self):
        for card in self.handCards:
            if card.alias == 'chopsticks':
                return True
        return False

    def wasabiCount(self):
        count = 0
        for card in self.handCards:
            if card.alias == 'wasabi' and card.topping == None:
                count +=1
        return count

    def getWasabiCards(self):
        cards = []
        for card in self.handCards:
            if card.alias == 'wasabi' and card.topping == None:
                cards.append(card)
        return cards

    def getChopsticksCard(self):
        for card in self.handCards:
            if card.alias == 'chopsticks':
                return card
        return None

    def sortAllMyCards(self):
        self.currentTurnCards.sort()
        self.handCards.sort()

    #{card.alias -> count}
    def scoringCatagory(self):
        res = {}
        res['maki_rolls'] = 0
        res['pudding'] = 0
        for card in self.handCards:
            key = card.alias
            if card.alias == 'wasabi' and card.topping != None:
                key = 'wasabi-' + card.topping.alias

            if card.alias not in ('maki_rolls_1', 'maki_rolls_2', 'maki_rolls_3'):
                if key in res:
                    res[key] += 1
                else:
                    res[key] = 1
            elif card.alias == 'maki_rolls_1':
                    res['maki_rolls'] += 1
            elif card.alias == 'maki_rolls_2':
                    res['maki_rolls'] += 2
            elif card.alias == 'maki_rolls_3':
                    res['maki_rolls'] += 3
        return res

    def returnChopsticks(self):
        chopsticksCard = self.getChopsticksCard()
        self.handCards.remove(chopsticksCard)
        self.currentTurnCards.append(chopsticksCard)

    def getNewCardToHands(self, newCard):
        self.currentTurnCards.remove(newCard)
        self.handCards.append(newCard)

    def topNewCardToWasabi(self, newCard, wasabiCard):
        wasabiCard.toTop(newCard)
        self.currentTurnCards.remove(newCard)

class Game:
    def __init__(self, numOfPlayers):
        self.numOfPlayers = numOfPlayers
        self.cardDeck = pupolateCardDeck()
        self.roundCount = 1
        self.players = {}
        self.turnToCards = {}
        self.status = GameStatus.NEW_ROUND

    def add_player(self, player):
        self.players[player.id] = player
        self.turnToCards[player.id] = []

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

    def getPreviousPlayerId(self, playerId):
        if playerId == 1:
            return self.numOfPlayers
        else:
            return playerId - 1

    def getPreviousPlayersCards(self, playerId):
        return self.turnToCards[self.getPreviousPlayerId(playerId)]

    def allPlayersJoined(self):
        return len(self.players) == self.numOfPlayers

    def allPlayersAreWaiting(self):
        allPlayersAreWaiting = True
        for playerId in self.players.keys():
            if self.players[playerId].status != PlayerStatus.WATING:
                allPlayersAreWaiting = False
        return allPlayersAreWaiting

    def allPlayersArePlaying(self):
        allPlayersArePlaying = True
        for playerId in self.players.keys():
            if self.players[playerId].status != PlayerStatus.PLAYING:
                allPlayersArePlaying = False
        return allPlayersArePlaying

    def isRoundEnd(self):
        isRoundEnd = True
        for playerId in self.players.keys():
            if self.turnToCards[playerId] != []:
                isRoundEnd = False
        return isRoundEnd

    def updateStatus(self):
        if self.status == GameStatus.NEW_ROUND or self.status == GameStatus.NEW_TURN:
            if not self.allPlayersJoined():
                return
            # when all player are playing, populate turnToCards
            if self.allPlayersArePlaying():
                for playerId in self.players.keys():
                    self.turnToCards[playerId] = [] + self.players[playerId].currentTurnCards
                self.status = GameStatus.TURN_STARTED
        elif self.status == GameStatus.TURN_STARTED:
            allPlayersAreWaiting = self.allPlayersAreWaiting()
            if not allPlayersAreWaiting:
                return
            if self.isRoundEnd():
                if self.roundCount >= 3:
                    self.status = GameStatus.END
                    return
                else:
                    self.roundCount += 1
                    self.status = GameStatus.NEW_ROUND
                    return
            if allPlayersAreWaiting:
                self.status = GameStatus.NEW_TURN

    def sortAllCards(self):
        for playerId in self.players.keys():
            self.players[playerId].sortAllMyCards()

    def scoring(self):
        import math
        mostMakiRollCount = 0
        secondMostMakiRollCount = 0
        mostPuddingCount = 0
        leastPuddingCount = 100
        MakirollsCountToPlayerId = {}
        PuddingCountToPlayerId = {}
        for playerId in self.players:
            score = 0
            catagories = self.players[playerId].scoringCatagory()
            for catagory in catagories.keys():
                if catagory == 'tempura':
                    score += math.floor(catagories[catagory]/2)*5
                elif catagory == 'sashimi':
                    score += math.floor(catagories[catagory]/3)*10
                elif catagory == 'dumpling':
                    dumplingCount = catagories[catagory]
                    if dumplingCount >= 5:
                        score += 15
                    elif dumplingCount >= 4:
                        score += 10
                    elif dumplingCount >= 3:
                        score += 6
                    elif dumplingCount >=2:
                        score += 3
                    elif dumplingCount ==1:
                        score += 1
                elif catagory == 'salmon_nigiri':
                    score += catagories[catagory]*2
                elif catagory == 'squid_nigiri':
                    score += catagories[catagory]*3
                elif catagory == 'egg_nigiri':
                    score += catagories[catagory]*1
                elif catagory == 'wasabi-salmon_nigiri':
                    score += catagories[catagory]*6
                elif catagory == 'wasabi-squid_nigiri':
                    score += catagories[catagory]*9
                elif catagory == 'wasabi-egg_nigiri':
                    score += catagories[catagory]*3
                elif catagory == 'maki_rolls':
                    if catagories[catagory] > mostMakiRollCount:
                        secondMostMakiRollCount = mostMakiRollCount
                        mostMakiRollCount = catagories[catagory]
                    if catagories[catagory] > secondMostMakiRollCount and catagories[catagory] < mostMakiRollCount:
                        secondMostMakiRollCount = catagories[catagory]
                    if catagories[catagory] not in MakirollsCountToPlayerId:
                        MakirollsCountToPlayerId[catagories[catagory]] = [playerId]
                    else:
                        MakirollsCountToPlayerId[catagories[catagory]].append(playerId)
                elif catagory == 'pudding':
                    if catagories[catagory] > mostPuddingCount:
                        mostPuddingCount = catagories[catagory]
                    if catagories[catagory] < leastPuddingCount:
                        leastPuddingCount = catagories[catagory]
                    if catagories[catagory] not in PuddingCountToPlayerId:
                        PuddingCountToPlayerId[catagories[catagory]] = [playerId]
                    else:
                        PuddingCountToPlayerId[catagories[catagory]].append(playerId)
            self.players[playerId].score = score
        if mostMakiRollCount != 0:
            for mtp in MakirollsCountToPlayerId:
                if mtp != mostMakiRollCount and mtp != secondMostMakiRollCount:
                    continue
                score = 0
                if mtp == mostMakiRollCount:
                    score = math.floor(6/len(MakirollsCountToPlayerId[mtp]))
                elif mtp == secondMostMakiRollCount and secondMostMakiRollCount != 0:
                    score = math.floor(3/len(MakirollsCountToPlayerId[mtp]))
                for playerId in MakirollsCountToPlayerId[mtp]:
                    self.players[playerId].score += score
        if mostPuddingCount != 0:
            for ptp in PuddingCountToPlayerId:
                if ptp != mostPuddingCount and ptp != leastPuddingCount:
                    continue
                score = 0
                if ptp == mostPuddingCount:
                    score = math.floor(6/len(PuddingCountToPlayerId[ptp]))
                elif ptp == leastPuddingCount:
                    score = math.floor(-6/len(PuddingCountToPlayerId[ptp]))
                for playerId in PuddingCountToPlayerId[ptp]:
                    self.players[playerId].score += score

def printState():
    print("\n\n\n")
    print(game.status)
    for playerId in game.players.keys():
        player = game.players[playerId]
        print("player "+str(playerId))
        print("======== turnToCards ========")
        for card in game.turnToCards[playerId]:
            print(card)
        print("======== currentTurnCards ========")
        for card in player.currentTurnCards:
            print(card)
        print("======== handCards ========")
        for card in player.handCards:
            print(card)

def validateStartRequest(request):
    global game
    if 'game' in globals():
        if len(game.players) == game.numOfPlayers:
            return (False, "Wait for next game!")
        if request.form['player_name'] == None:
            return (False, "Your name please!")
    else:
        if request.form['player_name'] == None:
            return (False, "Your name please!")
        if request.form['number_of_players'] == None:
            return (False, "Enter the game size!")
    return (True, "")


@app.route('/')
@app.route("/start", methods=['GET', 'POST'])
def start():
    errorMessage = request.args.get('errorMessage')
    global game
    if request.method == 'POST':
        validationResult = validateStartRequest(request)
        
        if 'game' not in globals():
            if not validationResult[0]:
                return render_template('home.html', numOfPlayers = 0, gameSize = 0, errorMessage = validationResult[1])
            game = Game(int(request.form['number_of_players']))
        else:
            if not validationResult[0]:
                return render_template('home.html', numOfPlayers = len(game.players), gameSize = game.numOfPlayers, errorMessage = validationResult[1])
        playerName = request.form['player_name']
        playerId = len(game.players) + 1
        game.add_player(Player(playerId, playerName))

        return redirect(url_for('turn', playerId = playerId))
    else:
        if 'game' in globals():
            return render_template('home.html', numOfPlayers = len(game.players), gameSize = game.numOfPlayers, errorMessage = errorMessage)
        else:
            return render_template('home.html', numOfPlayers = 0, gameSize = 0, errorMessage = errorMessage)

def validateTurnRequest(request):
    if 'game' not in globals():
        return (False, "Create a game first please :)")
    playerId = int(request.args.get('playerId'))
    global game
    if playerId > len(game.players):
        return (False, "Join a game first!")
    return (True, "")

@app.route('/turn', methods=['GET'])
def turn():
    validationResult = validateTurnRequest(request)
    if not validationResult[0]:
        return redirect(url_for('start', errorMessage = validationResult[1]))
    playerId = int(request.args.get('playerId'))
    global game
    player = game.players[playerId]
    errorMessage = request.args.get('errorMessage')
    if not game.allPlayersJoined():
        return render_template('turn.html', pageStatus = 'waiting',  players = game.players, player = player, roundNumber = game.roundCount, errorMessage = errorMessage)
    if game.status == GameStatus.NEW_ROUND:
        if player.currentTurnCards == []:
            cards = game.getCardsToStartARound()
            player.currentTurnCards = cards
            player.status = PlayerStatus.PLAYING
    elif game.status == GameStatus.NEW_TURN:
        if player.currentTurnCards == []:
            cards = game.getPreviousPlayersCards(playerId)
            player.currentTurnCards = cards
            player.status = PlayerStatus.PLAYING
    elif game.status == GameStatus.END:
        del game
        return redirect('start')
    game.updateStatus()
    game.sortAllCards()
    game.scoring()
    return render_template('turn.html', pageStatus = 'playing', players = game.players, gameSize = game.numOfPlayers, player = player, roundNumber = game.roundCount, errorMessage = errorMessage)

def getNewHandCards(playerId, request):
    newHandCards = []
    for card in game.turnToCards[playerId]:
            if request.form.get(card.id) != None:
                newHandCards.append(card)
    return newHandCards

def getSpecificCardFromNewHandCards(cardAlias, newHandCards):
    temp = [] + newHandCards
    for card in temp:
        if card.alias == cardAlias:
            newHandCards.remove(card)
            return card

def playersWasabiCount(player, newHandCards):
    count = 0
    for card in newHandCards:
        if card.alias == 'wasabi':
            count += 1
    return count + player.wasabiCount()

def inNewHandCards(cardAlias, newHandCards):
    for card in newHandCards:
        if card.alias == cardAlias:
            return True
    return False

# returns (result, errorMessage)
def validateCommitRequest(playerId, request):
    if 'game' not in globals():
        return (False, "Create a game first please :)")
    global game
    if game.status != GameStatus.TURN_STARTED:
        return (False, "Wait for other players to get their cards!")
    newHandCards = getNewHandCards(playerId, request)
    useChopsticks = request.form.get('useChopsticks') != None
    if useChopsticks and len(newHandCards) != 2:
        return (False, "Take 2 cards if use chopsticks!")
    if not useChopsticks and len(newHandCards) != 1:
        return (False, "You can only take 1 card!")

    useWasabi = request.form.get('useWasabi') != 'wasabi_unchecked'
    if useWasabi:
        player = game.players[playerId]
        wasabiMethod = request.form.get('useWasabi')
        wasabiCount = playersWasabiCount(player, newHandCards)
        if wasabiMethod == 'wasabi_egg_nigiri':
            if not inNewHandCards('egg_nigiri', newHandCards) or wasabiCount<1:
                return (False, "You didn't pick egg nigiri or you don't have wasabi!")
        elif wasabiMethod == 'wasabi_salmon_nigiri':
            if not inNewHandCards('salmon_nigiri', newHandCards) or wasabiCount<1:
                return (False, "You didn't pick salmon nigiri or you don't have wasabi!")
        elif wasabiMethod == 'wasabi_squid_nigiri':
            if not inNewHandCards('squid_nigiri', newHandCards) or wasabiCount<1:
                return (False, "You didn't pick squid nigiri or you don't have wasabi!")
        elif wasabiMethod == 'wasabi_both':
            if wasabiCount < 2:
                return (False, "You don't have 2 wasabis to be topped!")
            for card in newHandCards:
                if card.alias not in ['egg_nigiri', 'salmon_nigiri', 'squid_nigiri']:
                    return (False, "You didn't pick two nigiris!")
        else:
            return (False, "unknown use of wasabi" + wasabiMethod)
    return (True, "")

def handleWasabi(nigiriAlias, newHandCards, player):
    nigiri = getSpecificCardFromNewHandCards(nigiriAlias, newHandCards)
    wasabiInOldHand = player.getWasabiCards()
    if wasabiInOldHand != []:
        player.topNewCardToWasabi(nigiri, wasabiInOldHand[0])
        if len(newHandCards) > 0:
            player.currentTurnCards.remove(newHandCards[0])
            player.handCards.append(newHandCards[0])
    else:
        wasabi = getSpecificCardFromNewHandCards('wasabi', newHandCards)
        player.topNewCardToWasabi(nigiri, wasabi)
        player.getNewCardToHands(wasabi)

@app.route('/turn_commit/<playerId>', methods=['POST'])
def turn_commit(playerId):
    playerId = int(playerId)
    validationResult = validateCommitRequest(playerId, request) 
    if not validationResult[0]:
        return redirect(url_for('turn', playerId = playerId, errorMessage = validationResult[1]))
    global game
    player = game.players[playerId]

    useWasabi = request.form.get('useWasabi') != 'wasabi_unchecked'
    useChopsticks = request.form.get('useChopsticks') != None
    if useChopsticks:
        player.returnChopsticks()

    newHandCards = getNewHandCards(playerId, request)

    if useWasabi:
        wasabiMethod = request.form.get('useWasabi')
        if wasabiMethod == 'wasabi_egg_nigiri':
            handleWasabi('egg_nigiri', newHandCards, player)
        elif wasabiMethod == 'wasabi_salmon_nigiri':
            handleWasabi('salmon_nigiri', newHandCards, player)
        elif wasabiMethod == 'wasabi_squid_nigiri':
            handleWasabi('squid_nigiri', newHandCards, player)
        elif wasabiMethod == 'wasabi_both':
            wasabiInOldHand = player.getWasabiCards()
            player.topNewCardToWasabi(newHandCards[0], wasabiInOldHand[0])
            player.topNewCardToWasabi(newHandCards[1], wasabiInOldHand[1])
    elif useChopsticks:
        player.getNewCardToHands(newHandCards[0])
        player.getNewCardToHands(newHandCards[1])
    else:
        player.getNewCardToHands(newHandCards[0])

    player.status = PlayerStatus.WATING
    game.turnToCards[playerId] = player.currentTurnCards
    player.currentTurnCards = []
    printState()
    return redirect(url_for('turn', playerId = playerId))

@app.route('/end_game')
def end_game():
    if 'game' in globals():
        global game
        del game
    redirect('start')