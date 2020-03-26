import discord
from discord.ext import commands
import random, asyncio

casts = ['90s', 'apples', 'Base', 'BaseUK', 'c-admin', 'c-anime', 'c-antisocial', 'c-derps', 'c-doctorwho', 
'c-equinity', 'c-eurovision', 'c-fim', 'c-gamegrumps', 'c-golby', 'c-guywglasses', 'c-homestuck', 
'c-imgur', 'c-khaos', 'c-ladies', 'c-mrman', 'c-neindy', 'c-nobilis', 'c-northernlion', 'c-prtg', 
'c-ragingpsyfag', 'c-rpanons', 'c-rt', 'c-socialgamer', 'c-sodomydog', 'c-stupid', 'c-tg', 'c-vewysewious', 
'c-vidya', 'c-xkcd', 'CAHe1', 'CAHe2', 'CAHe3', 'CAHe4', 'CAHe5', 'CAHe6', 'CAHgrognards', 'Canadian', 'crabs', 
'fantasy', 'food', 'GOT', 'greenbox', 'HACK', 'hillary', 'HOCAH', 'Image1', 
'matrimony', 'misprint', 'NSFH', 'period', 'reject', 'reject2', 'science', 'test', 'trumpbag', 'trumpvote', 
'weed', 'www', 'xmas2012', 'xmas2013']

def remove_newline(text):

    	return text.replace('\n', ' ')

class Player():
    def __init__(self, casts):
        self.score = 0
        self.cards = []
        self.casts = casts
        
        #Each player starts with 10 cards
        for _ in range(10):
            self.draw_card()

    def draw_card(self):
        """
        Randomly chooses a cast to draw from then randomly chooses a cards from that cast
        """
        white_cards = []
        with open("CardsAgainstHumanity/" + random.choice(self.casts) + "/white.md.txt", 'r') as white:
            for line in white:
                white_cards.append(remove_newline(line))
            self.cards.append(random.choice(white_cards))

    def play_card(self, num):
        """
        Removes the given card and returns it from printing 
        """
        return self.cards.pop(num)

class CAH():
    def __init__(self, ctx, client, max_score, users):
        self.ctx = ctx
        self.client = client
        self.users = users
        self.players = []
        self.max_score = max_score
        self.casts = ['BaseUK','c-ladies','c-stupid', 'CAHe1', 'CAHe2', 'CAHe3', 'CAHe4', 'CAHe5', 'CAHe6', 'crabs','greenbox',  'hillary', 'NSFH', 'period', 'reject2', 'science', 'test', 'trumpbag', 'trumpvote', 'www']
        self.emojis = ['\u0030\u20E3','\u0031\u20E3','\u0032\u20E3','\u0033\u20E3','\u0034\u20E3', '\u0035\u20E3','\u0036\u20E3','\u0037\u20E3','\u0038\u20E3', '\u0039\u20E3']
        self.card_choices = []
        self.hand_updates = 0
        self.player_accounts = []
        self.hands = []
        self.round_count = 0

        #For as many players as is given, create a player instance and save that users account information
        for k in range(len(self.users)):
            pp = Player(self.casts)
            self.players.append(pp)
            self.player_accounts.append(self.client.get_user(int(self.users[k].id)))

    def play_black_card(self):
        """
        Randomly chooses a cast to draw from then randomly chooses a cards from that cast. Counts the amount of '_' and saves it to the class variable
        """
        black_cards = []
        with open("CardsAgainstHumanity/" + random.choice(self.casts) + "/black.md.txt", 'r') as black:
            for line in black:
                black_cards.append(remove_newline(line))
        self.black_card = random.choice(black_cards)
        self.black_card_blanks = self.black_card.count('_')
        return self.black_card

    async def send_hand(self, player, player_num):
        """
        Send the given player their hand with the black card as title and their score. If this function is not being called for the first time for a player, 
        instead of sending the hand, the hand is instead edited.  
        """
        embed_hand = discord.Embed(title=f"{self.users[player_num].name}\t\tScore: {player.score}\n{self.black_card}")

        for i, card in enumerate(player.cards):
            embed_hand.add_field(name=f"Card {i}",value=card, inline=False)

        
        if self.hand_updates < 1:
            #send to the right player
            self.hand = await self.player_accounts[player_num].send(embed=embed_hand)
            #add emojis to hand message
            for i, card in enumerate(player.cards):
                await self.hand.add_reaction(emoji=self.emojis[i])
            #add to list to store hand messages for editing purposes    
            self.hands.append(self.hand)
        else:
            await self.hands[player_num].edit(embed=embed_hand)


    async def round(self):
        
        def react_check(msg):
            def check(reaction, reacting_user):
                return reacting_user == self.czar and str(reaction.emoji) in self.emojis and reaction.message.id==msg.id
            return check
        #pick Card Czar works in round robin fashion
        self.czar = self.users[self.round_count%len(self.users)]
        await self.ctx.send(f"Card Czar is {self.czar.name}")
        self.play_black_card()

        embed_main_game = discord.Embed(title=f"```{self.black_card}```")
        self.main_card = await self.ctx.send(embed = embed_main_game) 

        #If only one card is required, for each player, send hand and wait for input
        if self.black_card_blanks < 2:
            for i, player in enumerate(self.players):
                await self.send_hand(player, i)
                choice = int(input(f"{self.users[i].name}, what card do you pick?"))
                self.card_choices.append(choice)

        #If more than one card is required, for each player, send hand and wait for inputs, add inputs to a list then append that list to the card_choices list
        else:
            for i, player in enumerate(self.players):
                player_choices = []
                await self.send_hand(player, i)
                for j in range(self.black_card_blanks):
                    choice = int(input(f"{self.users[i].name}, what card do you pick?"))
                    player_choices.append(choice)
                self.card_choices.append(player_choices)


        #end_round     
        #Message to be sent to main channel. Title as black card, then player as field name and value as the card they selected. Draw a card from each one submitted.
        for i, player in enumerate(self.players):
            if self.black_card_blanks < 2:
                embed_main_game.add_field(name=f"{self.users[i].name}\t\t{self.emojis[i]}",value=player.play_card(self.card_choices[i]), inline=False)
                player.draw_card()
            else:
                text = ""
                for k in range(self.black_card_blanks):
                    player.draw_card()
                    text += player.play_card(self.card_choices[i][k]) + "\n"
                embed_main_game.add_field(name=f"{self.users[i].name}",value=text, inline=False)              

        # self.main_card = await self.ctx.send(embed=embed_main_game)
        await self.main_card.edit(embed=embed_main_game)
        
        for i, answer in enumerate(self.players):
            await self.main_card.add_reaction(emoji=self.emojis[i])
    
        try:
            reaction, user= await self.client.wait_for('reaction_add', timeout=60.0, check=react_check(self.main_card))
            winner = self.emojis.index(str(reaction.emoji))
            self.players[winner].score += 1   
        except Exception as e:
            print(e)
            await self.ctx.send("Timed out! No points for anyone!")

        # winner = int(input("Czar, choose your favourite!"))

        #reset card_choices and increment hand_updates and round_count
        self.card_choices = []
        self.hand_updates += 1
        self.round_count += 1

    def player_wins(self):
        for i, player in enumerate(self.players):
            if player.score == self.max_score:
                self.winner = i
                return True
        return False

    async def main(self):
        while not self.player_wins():
           await self.round()
        await self.ctx.send(f"Game Over! Winner was {self.users[self.winner].name}")
        


class CardsAgainstHumanity(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()    
    async def CaH(self, ctx):

        embed_rules = discord.Embed(title="Cards Against Humanity", color=0x00ff00)

        embed_rules.add_field(name='Description', value="Cards Against Humanity is a party game for horrible people. Unlike most of the party games you've played before, Cards Against Humanity is as despicable and awkward as you and your friends.", inline=False)
        embed_rules.add_field(name='How to Play?', value="The game is simple. Each round, one player asks a question from a black card, and everyone else answers with their funniest white card.", inline=False)
        embed_rules.add_field(name='How to Join', value='To play react to this message', inline=False)

        msg = await ctx.send(embed=embed_rules)
        await msg.add_reaction(emoji = '\U00002705')
        await asyncio.sleep(8)

        cache_msg = discord.utils.get(self.client.cached_messages, id = msg.id)
        reaction = cache_msg.reactions[0]
        users = await reaction.users().flatten()
        users = [x for x in users if str(x) != str(self.client.user)]
        if 0 < len(users) < 9:
            game = CAH(ctx, self.client, 2, users)
            await game.main()
        else:
            await ctx.send("Game requires 1 to 8 players!")



def setup(client):
    client.add_cog(CardsAgainstHumanity(client))