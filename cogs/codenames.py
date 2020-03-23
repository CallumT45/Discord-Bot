import discord
from discord.ext import commands
import random, asyncio

class Codename():
    
    def __init__(self, ctx, client, users):
        
        self.ctx = ctx
        self.client = client
        self.users = users
        self.blue = random.sample(self.users, k=len(self.users)//2)
        self.red = list(set(self.users) - set(self.blue))

        self.words = []
        with open('files/words.txt','r') as wordfile:
                for row in wordfile:
                        self.words.append(row[:-1])


        self.blue_cards = 9
        self.red_cards = 8
        self.game_words = random.sample(self.words, 25)
        self.blue_words = random.sample(self.game_words, self.blue_cards)
        self.red_words = random.sample(list(set(self.game_words) - set(self.blue_words)), self.red_cards)
        self.black_card = random.sample(list(set(self.game_words) - set(self.blue_words) - set(self.red_words)), 1)
        self.neutral_words = list(set(self.game_words) - set(self.blue_words) - set(self.red_words) - set(self.black_card))
        self.guessed_words = []
        self.flag = True

    async def spymaster(self):
            
            embed_code = discord.Embed(title=f"Codename\n\nBlue Words: {self.blue_cards}\nRed Words: {self.red_cards}", color=0x00ff00)

            for w in self.game_words:
                str_w = f'```{w}```'
                if w in self.guessed_words:
                    str_w = str(f"""```css\n{w}```""")
                idenifier = '.'
                if w in self.blue_words:
                    idenifier = 'Blue'
                elif w in self.red_words:
                    idenifier = 'Red'
                elif w in self.neutral_words:
                    idenifier = 'Neutral'
                elif w in self.black_card:
                    idenifier = 'Game Over'
                embed_code.add_field(name=idenifier,value=str_w, inline=True)

            blue_spymaster = random.choice(self.blue)
            red_spymaster = random.choice(self.red)

            blue_spymaster = self.client.get_user(int(blue_spymaster.id))
            red_spymaster = self.client.get_user(int(red_spymaster.id))

            await blue_spymaster.send(embed=embed_code)
            await red_spymaster.send(embed=embed_code)


    async def game_loop(self, team):
        def word_check(m):
            return (m.content.upper() in self.game_words) or m.content.upper() == "END_TURN" or m.content.upper() == "$STOP"

        if team == "Blue":
            team_num = self.blue_cards
            colour = 0x0000fe
        else:
            team_num = self.red_cards
            colour = 0xff0000

        while team_num > 0:
            # await self.ctx.send(f"{team} team choose your letters\n\nBlue Words: {self.blue_cards}\nRed Words: {self.red_cards}")

            embed_code = discord.Embed(title=f"Codename\n\nBlue Words: {self.blue_cards}\nRed Words: {self.red_cards}", color=colour)

            for w in self.game_words:
                str_w = f'```{w}```'
                idenifier = '.'
                if w in self.guessed_words:
                    str_w = str(f"""```css\n{w}```""")

                if w in self.guessed_words and w in self.blue_words:
                    idenifier = 'Blue'
                elif w in self.guessed_words and w in self.red_words:
                    idenifier = 'Red'
                elif w in self.guessed_words and w in self.neutral_words:
                    idenifier = 'Neutral'
                elif w in self.guessed_words and w in self.black_card:
                    idenifier = 'Game Over'
                embed_code.add_field(name=idenifier,value=str_w, inline=True)

            await self.ctx.send(embed=embed_code)

            try:
                guess = await self.client.wait_for('message', timeout=120.0, check=word_check)
                guess.content = guess.content.upper()
                if guess.content == "END_TURN":
                    break
                self.guessed_words.append(guess.content)
                if guess.content in self.black_card or guess.content == 'STOP':
                    self.flag = False
                    break
                if guess.content in self.blue_words:
                    self.blue_cards -= 1
                elif guess.content in self.red_words:
                    self.red_cards -= 1
              
                if team == "Blue" and guess.content not in self.blue_words:
                    break
                elif team == "Red" and guess.content not in self.red_words:
                    break                    


            except:
                await self.ctx.send("Out of Time, your turn is over!")
                break        

    async def main(self):
        blue_names = [member.name for member in self.blue]
        red_names = [member.name for member in self.red]

        await self.ctx.send(f'Blue Team is {", ".join(blue_names)}')
        await self.ctx.send(f'Red Team is {", ".join(red_names)}')
        await self.ctx.send("Spymasters check your DMs")
        

        while self.blue_cards > 0 and self.red_cards > 0 and self.flag:
            await self.spymaster()
            await self.game_loop('Blue')
            if self.flag:
                await self.game_loop('Red')

        await self.ctx.send("Game Over")





class Codenames(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()    
    async def codenames(self, ctx):
        how_to_play = """
            You need at least four players (two teams of two) for a standard game. 
            Each team has one player as their spymaster. Both spymasters will be sent a dm with the answer key.
            \nIf you are the spymaster, you are trying to think of a one-word clue that relates to some of the words your team is trying to guess. 
            When you think you have a good clue, you say it. You also say one number, which tells your teammates how many codenames are related to your clue."""
        Example1 = """Example: Two of your words are NUT and BARK. Both of these grow on trees, so you say tree: 2. 
            You are allowed to give a clue for only one word (cashew: 1 ) but it's fun to try for two or more. """

        how_to_play2 = """Getting four words with one clue is a big accomplishment. The field operatives must always make at least one guess. 
            Any wrong guess ends the turn immediately, but if the field operatives guess a word of their team's color, they can keep guessing. 
            You have 120 seconds for each word to guess. To guess a word type it into the chat. Once you have guessed as many words as your spymaster has linked. Your turn is over.
            Type end_turn to finish your turn or stop to end the game"""
        

        embed_rules = discord.Embed(title="Codenames", color=0x00ff00)

        embed_rules.add_field(name='How to Play', value=how_to_play, inline=False)
        embed_rules.add_field(name='Example', value=Example1, inline=False)
        embed_rules.add_field(name='How to Play', value=how_to_play2, inline=False)
        embed_rules.add_field(name='How to Join', value='To play react to this message', inline=False)

        msg = await ctx.send(embed=embed_rules)
        await msg.add_reaction(emoji = "✅")
        await asyncio.sleep(20)

        cache_msg = discord.utils.get(self.client.cached_messages, id = msg.id)
        reaction = cache_msg.reactions[0]
        users = await reaction.users().flatten()
        users = [x for x in users if str(x) != 'Test Bot#3617']
        if len(users) > 3:
            CN = Codename(ctx, self.client, users)
            await CN.main()
        else:
            await ctx.send("You need at least 4 to play!")

def setup(client):
    client.add_cog(Codenames(client))