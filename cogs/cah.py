import discord
from discord.ext import commands
import random, asyncio

casts = ['90s', 'apples', 'Base', 'BaseUK', 'Box', 'c-admin', 'c-anime', 'c-antisocial', 'c-derps', 'c-doctorwho', 'c-equinity', 
'c-eurovision', 'c-fim', 'c-gamegrumps', 'c-golby', 'c-guywglasses', 'c-homestuck', 'c-imgur', 'c-khaos', 'c-ladies', 
'c-mrman', 'c-neindy', 'c-nobilis', 'c-northernlion', 'c-prtg', 'c-ragingpsyfag', 'c-rpanons', 'c-rt', 'c-socialgamer', 
'c-sodomydog', 'c-stupid', 'c-tg', 'c-vainglory', 'c-vewysewious', 'c-vidya', 'c-xkcd', 'CAHe1', 'CAHe2', 'CAHe3', 'CAHe4', 'CAHe5', 'CAHe6', 'CAHgrognards', 
'Canadian', 'crabs', 'fantasy', 'food', 'GOT', 'greenbox', 'HACK', 'hillary', 'HOCAH', 'Image1', 'matrimony', 'mi   await self.ctx.send', 
'NSFH', 'PAX2015', 'PAXE2013', 'PAXE2014', 'PAXEP2014', 'PAXP2013', 'PAXPP2014', 'period', 'reject', 'reject2', 'science', 'trumpbag', 
'trumpvote', 'weed', 'www', 'xmas2012', 'xmas2013']

def remove_newline(text):

    	return text.split('\n')[0]

class Player():
    def __init__(self, casts):
        self.score = 0
        self.cards = []
        self.casts = casts
        

        for _ in range(10):
            self.draw_card()

    def draw_card(self):
        white_cards = []
        with open("CardsAgainstHumanity/" + random.choice(self.casts) + "/white.md.txt", 'r') as white:
            for line in white:
                white_cards.append(remove_newline(line))
            self.cards.append(random.choice(white_cards))

    def play_card(self, num):
        return self.cards.pop(num)

class CAH():
    def __init__(self, ctx, client, max_score, users):
        self.ctx = ctx
        self.client = client
        self.users = users
        self.players = []
        self.max_score = max_score
        self.casts = ['BaseUK', 'Box','CAHe1', 'CAHe2', 'CAHe3', 'CAHe4', 'CAHe5', 'CAHe6', 'CAHgrognards', 'Canadian', 'crabs', 'fantasy', 'food',
                     'greenbox', 'HACK', 'hillary', 'HOCAH', 'Image1', 'matrimony', 'NSFH', 'period']
        self.card_choices = []
        self.hand_updates = 0

        for _ in range(len(self.users)):
            pp = Player(self.casts)
            self.players.append(pp)

    def play_black_card(self):
        black_cards = []
        with open("CardsAgainstHumanity/" + random.choice(self.casts) + "/black.md.txt", 'r') as black:
            for line in black:
                black_cards.append(remove_newline(line))
        self.black_card = random.choice(black_cards)
        self.black_card_blanks = self.black_card.count('_')
        return self.black_card

    async def send_hand(self, player, player_num):
        embed_hand = discord.Embed(title=f"{self.users[player_num].name}\t\tScore: {player.score}\n{self.black_card}")

        for i, card in enumerate(player.cards):
            embed_hand.add_field(name=f"Card {i+1}",value=card, inline=False)

        if self.hand_updates < 1:
            self.hand = await self.ctx.send(embed=embed_hand)

        else:
            await self.hand.edit(embed=embed_hand)


    async def round(self):
        # await self.ctx.send(self.play_black_card())
        self.play_black_card()
        if self.black_card_blanks < 2:
            for i, player in enumerate(self.players):
                await self.send_hand(player, i)
                choice = int(input(f"{self.users[i].name}, what card do you pick?"))
                self.card_choices.append(choice-1)

        else:
            for i, player in enumerate(self.players):
                player_choices = []
                await self.ctx.send(player.cards)
                for j in range(self.black_card_blanks):
                    choice = int(input(f"{self.users[i].name}, what card do you pick?"))
                    player_choices.append(choice-1)
                self.card_choices.append(player_choices)

        #end_round
        
        embed_main_game = discord.Embed(title=self.black_card)

        for i, player in enumerate(self.players):
            if self.black_card_blanks < 2:
                embed_main_game.add_field(name=f"{self.users[i].name}",value=player.play_card(self.card_choices[i]), inline=False)
                player.draw_card()
            else:
                text = ""
                for k in range(self.black_card_blanks):
                    text += player.play_card(self.card_choices[i][k]) + "\n"
                embed_main_game.add_field(name=f"{self.users[i].name}",value=text, inline=False)


        self.main_card = await self.ctx.send(embed=embed_main_game)


        
        

        winner = int(input("Czar, choose your favourite!"))

        self.players[winner-1].score += 1
        self.card_choices = []
        self.hand_updates += 1

    def player_wins(self):
        for player in self.players:
            if player.score == self.max_score:
                return True
        return False

    async def main(self):
        while not self.player_wins():
           await self.round()


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
        await asyncio.sleep(15)

        cache_msg = discord.utils.get(self.client.cached_messages, id = msg.id)
        reaction = cache_msg.reactions[0]
        users = await reaction.users().flatten()
        users = [x for x in users if str(x) != str(self.client.user)]

        game = CAH(ctx, self.client, 2, users)
        await game.main()



def setup(client):
    client.add_cog(CardsAgainstHumanity(client))