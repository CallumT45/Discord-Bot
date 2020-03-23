import discord
from discord.ext import commands
import random, asyncio


class PlayingCard():
    rank_num = {'Ace':14,'King':13,'Queen':12,'Jack':11,10:10,9:9,8:8,7:7,6:6,5:5,4:4,3:3,2:2}

    def __init__(self,r,s):
        self.suit = s
        self.rank = r


    def __lt__(self,other):
        return (self.suit, self.rank_num[self.rank]) < (other.suit, self.rank_num[other.rank])



    def __str__(self):
        return self.suit  + " " + str(self.rank)

    async def show(self):
        await self.ctx.send(self.rank, self.suit)


class Deck(object):
    """Represents a deck of cards.

    Attributes:
    cards: list of Card objects.
    """
    suits = ['Spades','Hearts','Diamonds','Clubs']
    rank = [None,'Ace','King','Queen','Jack',10,9,8,7,6,5,4,3,2]

    def __init__(self, num_decks = 1):
        self.cards = []
        for i in range(4*num_decks):
            for j in range(1, 14):
                card = PlayingCard(Deck.rank[j], Deck.suits[(i%4)])
                self.cards.append(card)

    def add_card(self, card):
        """Adds a card to the deck."""
        self.cards.append(card)

    def remove_card(self, card):
        """Removes a card from the deck."""
        self.cards.remove(card)

    def pop_card(self, i=-1):
        """Removes and returns a card from the deck.

        i: index of the card to pop; by default, pops the last card.
        """
        return self.cards.pop(i)

    def shuffle(self):
        """Shuffles the cards in this deck."""
        random.shuffle(self.cards)

    def sort(self):
        """Sorts the cards in ascending order."""
        self.cards.sort()

    def move_cards(self, hand, num):
        """Moves the given number of cards from the deck into the Hand.

        hand: destination Hand object
        num: integer number of cards to move
        """
        for i in range(num):
            hand.add_card(self.pop_card())

    def __str__(self):
        text = ''
        for card in self.cards:
            text += str(card.rank) + " " + card.suit + '\n'
        return text

class Player(Deck):
    """Represents a hand of playing cards."""
    
    def __init__(self):
        self.cards = []
        self.has_bj = False
        self.coins = 100.0
        self.bet = 0
        self.out = False

    def get_value(self):
        bj_rankings = {'Ace':11, 'King':10, 'Queen':10, 'Jack':10, 10:10, 9:9, 8:8, 7:7, 6:6, 5:5, 4:4, 3:3, 2:2}
        value = 0
        for card in self.cards:
            value += bj_rankings[card.rank]
        return value

    def credit(self, amount):
    	self.coins += amount

    def debit(self, amount):
        self.coins -= amount

    def clear(self):
        self.cards = [] 

class BlackJack():
    def __init__(self, num_players, ctx, client):
        self.players = []
        self.deck = Deck(6)#using 6 decks as per casino standard
        self.dealer = Player()
        for i in range(num_players):
            player = Player()
            self.players.append(player)
        self.total_players_out = 0
        self.ctx = ctx
        self.client = client


    async def draw_start(self):
        for i, player in enumerate(self.players):
            if not player.out:
                await self.ctx.send(f"Player {i+1}")
                bet = float(input(f"How much would you like to bet? You have {player.coins} in the bank: "))
                if bet == 0:
                    player.out = True
                else:
                    player.debit(bet)
                    player.bet = bet

        self.deck.shuffle()
        self.dealer.clear()
        self.deck.move_cards(self.dealer, 1)

        await self.ctx.send("Dealer")
        await self.ctx.send(self.dealer)


        for i, player in enumerate(self.players):
            if not player.out:
                await self.ctx.send(f"Player {i+1}")
                player.clear()
                self.deck.move_cards(player, 2)
                await self.ctx.send(player)

    async def round(self):
        for i, player in enumerate(self.players):
            if not player.out:
                HoS = ''
                while HoS != "stand":
                    await self.ctx.send(player)
                    HoS = input(f"Player {i+1}, Would you like to hit or stand? ").lower()
                    if HoS == "hit":
                        self.deck.move_cards(player, 1)
                    if player.get_value() > 21:
                        await self.ctx.send(f"Player {i+1} is bust")
                        await self.ctx.send(player)
                        break
                    elif player.get_value() == 21:
                        await self.ctx.send(f"Player {i+1} has BlackJack!")
                        await self.ctx.send(player)
                        player.has_bj = True
                        break

        while self.dealer.get_value() < 17:
            self.deck.move_cards(self.dealer, 1)
            await self.ctx.send("Dealer")
            await self.ctx.send(self.dealer)
            if self.dealer.get_value() > 21:
                await self.ctx.send("Dealer is bust")
                break
            elif self.dealer.get_value() == 21:
                await self.ctx.send("Dealer has BlackJack!")
                self.dealer.has_bj = True

        if_flag = False
        if self.dealer.get_value() > 21:
            for player in self.players:
                await self.ctx.send(player.get_value())
                if player.get_value() <= 21:#if they have not gone bust
                    player.credit(2 * player.bet)
            await self.ctx.send("Since Dealer is bust, all players win")

        elif self.dealer.has_bj:
            for player in self.players:
                if player.has_bj:
                    player.credit(2 * player.bet)
        else:
            for i, player in enumerate(self.players):
                if player.has_bj or (player.get_value() < 21 and  player.get_value() > self.dealer.get_value()):
                    if_flag = True
                    await self.ctx.send(f"Player {i+1}, Conrats on winning!")
                    player.credit(2 * player.bet)
                elif player.get_value() < 21 and  player.get_value() == self.dealer.get_value():
                    if_flag = True
                    await self.ctx.send(f"Player {i+1}, tied with the dealer!")
                    player.credit(player.bet)
            if not if_flag:
                await self.ctx.send("House wins")


        for player in self.players:
            if player.coins < 1:
                await self.ctx.send("Min bet is €1, get your cheap ass out of here")
                player.out = True
            elif player.coins > 10000:
                await self.ctx.send("Dude! You\'re too good, we have to stop you")
                player.out = True
            if player.out:
                self.total_players_out += 1

    async def main(self):
        while self.total_players_out != len(self.players):
            await self.draw_start()
            await self.round()
        for i, player in enumerate(self.players):
            await self.ctx.send(f"Player {i+1} you are leaving with {player.coins}")

class Blackjack(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()    
    async def blackjack(self, ctx):
        bj = BlackJack(1, ctx, self.client)
        await bj.main()

def setup(client):
    client.add_cog(Blackjack(client))