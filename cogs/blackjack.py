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
            def bet_check(m):
                try:
                    value = float(m.content)
                    if 0 <= value <= player.coins:
                        return True
                    else: return False
                except:
                    return False
            if not player.out:
                await self.ctx.send(f"Player {i+1}, How much would you like to bet? You have {player.coins} in the bank: ")
                try:
                    bet = await self.client.wait_for('message', timeout=120.0, check=bet_check)
                    bet = float(bet.content)
                    if bet == 0:
                        player.out = True
                        self.total_players_out += 1
                    else:
                        player.debit(bet)
                        player.bet = bet
                except:
                    await self.ctx.send("Timed Out!")
                    player.out = True
                    self.total_players_out += 1
        if self.total_players_out < len(self.players):#if all players arent out
            self.deck.shuffle()
            self.dealer.clear()
            self.deck.move_cards(self.dealer, 1)

            embed_dealer = discord.Embed(title='Dealer', color=0x00ff00)
            embed_dealer.add_field(name="Hand", value=self.dealer, inline=False)
            self.dealer_msg = await self.ctx.send(embed = embed_dealer)

            embed_players = discord.Embed(title='Players', color=0x0000fd)
            for i, player in enumerate(self.players):
                if not player.out:
                    player.clear()
                    self.deck.move_cards(player, 2)
                    embed_players.add_field(name=f"Player {i+1}", value=player, inline=True)
                    if player.get_value() == 21:
                        player.has_bj = True
            self.players_msg = await self.ctx.send(embed = embed_players)

    async def round(self):

        def turn_check(m):
            return (m.content.lower() == 'stand') or (m.content.lower() == 'hit')

        for i, player in enumerate(self.players):
            if not player.out:
                HoS = ''
                while HoS != "stand":
                    embed_players = discord.Embed(title='Players', color=0x0000fd)
                    try:
                        await self.ctx.send(f"Player {i+1}, Would you like to hit or stand? ")
                        HoS = await self.client.wait_for('message', timeout=20.0, check=turn_check)
                        HoS = HoS.content.lower()

                        if HoS == "stand":
                            break

                        elif HoS == "hit":
                            self.deck.move_cards(player, 1)#give the player a new card
                            for j, player2 in enumerate(self.players):#reload the embed with player hands
                                if not player.out:
                                    embed_players.add_field(name=f"Player {j+1}", value=player2, inline=True)
                                    await self.players_msg.edit(embed = embed_players)

                        if player.get_value() > 21:
                            await self.ctx.send(f"Player {i+1} is bust")
                            break
                        elif player.get_value() == 21:
                            await self.ctx.send(f"Player {i+1} has BlackJack!")
                            player.has_bj = True
                            break

                    except Exception as e:
                        print(e)
                        continue

        while self.dealer.get_value() < 17:
            self.deck.move_cards(self.dealer, 1)

        embed_dealer = discord.Embed(title='Dealer', color=0x00ff00)
        embed_dealer.add_field(name="Hand", value=self.dealer, inline=False)
        await self.dealer_msg.edit(embed=embed_dealer)    

        if_flag = False
        if self.dealer.get_value() > 21:
            for player in self.players:
                if player.get_value() <= 21:#if they have not gone bust
                    player.credit(2 * player.bet)
            await self.ctx.send("Since Dealer is bust, all players win")

        elif self.dealer.get_value() == 21:
            await self.ctx.send("Dealer has BlackJack!")
            for player in self.players:
                if player.has_bj:
                    player.credit(2 * player.bet)
        else:
            for i, player in enumerate(self.players):
                if player.has_bj or (player.get_value() < 21 and  player.get_value() > self.dealer.get_value()) and not player.out:
                    if_flag = True
                    await self.ctx.send(f"Player {i+1}, Conrats on winning!")
                    player.credit(2 * player.bet)
                elif player.get_value() < 21 and  player.get_value() == self.dealer.get_value() and not player.out:
                    if_flag = True
                    await self.ctx.send(f"Player {i+1}, tied with the dealer!")
                    player.credit(player.bet)
            if not if_flag:
                await self.ctx.send("House wins")


        for i, player in enumerate(self.players):
            if not player.out:
                player.has_bj = False
                if player.coins < 1:
                    await self.ctx.send(f"Player {i+1}, Min bet is €1, get your cheap ass out of here")
                    player.out = True
                    self.total_players_out += 1
                elif player.coins > 10000:
                    await self.ctx.send(f"Player {i+1}! You\'re too good, we have to stop you")
                    player.out = True
                    self.total_players_out += 1


    async def main(self):
        while self.total_players_out < len(self.players):
            await self.draw_start()
            await self.round()
        for i, player in enumerate(self.players):
            await self.ctx.send(f"Player {i+1} you are leaving with {player.coins}")

class Blackjack(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()    
    async def blackjack(self, ctx):
        bj = BlackJack(2, ctx, self.client)
        await bj.main()

def setup(client):
    client.add_cog(Blackjack(client))