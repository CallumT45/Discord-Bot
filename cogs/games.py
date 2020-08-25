import discord
from discord.ext import commands
import requests
import html
import random
import json
import asyncio

from cogs.extraClasses.hangman import Hangman
from cogs.extraClasses.TicTacToe import TicTacToe
from cogs.extraClasses.werewolf import Werewolf
from cogs.extraClasses.blackjack import BlackJack
from cogs.extraClasses.codenames import Codenames
from cogs.extraClasses.CardsAgainstHumanity import CAH


class Games(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.congrats = congrats = ["Wow, turns our youre like smart or something", "Powerful, impressive, firm and unforgettable. But enough about your farting... Congrats!", "Congratulations on finding your balls",
                                    "Wow, Well done, your Mother and I are very proud", "You have performed extremely adequately.", "You surprised me a little bit. I knew you were capable, but I didn't expect this level of accomplishment!",
                                    "I genuinely thought you'd fail again", "Ooooh look at you all clever and shit!", "Feeling so much joy for you today. What an impressive achievement!", "I’ve got a feeling this is only the beginning of even more great things to come for you!", "It looks like you'll be world's No.1 in a few hours and I wanted to be the first to congratulate you!", "Congratulations! Now Back To Work!"]

    @commands.command()
    async def ping(self, ctx):
        """?"""
        await ctx.send("Pong!")

    @commands.command()
    async def hangman(self, ctx):
        """
        Classic game of Hangman
        """
        hm = Hangman(ctx, self.client, self.congrats)
        await hm.maingame()

    @commands.command()
    async def quiz(self, ctx):
        """
        Answer a multiple choice question.
        Gets a question and answer from the api, extracts answers and combines correct answer with the others, then shuffles. Question and answers are sent to the server after
        after being linked to an emoji, then linked emojis act as buttons to select answers. The bot waits for the user who sent $quiz to react with an appropriate
        emoji then reveals the answer.

        NOTE: The url sometimes returns html/xml encoded strings, so I deal with it with htmml.unescape

        """
        response = requests.get(
            'https://opentdb.com/api.php?amount=1&type=multiple')
        json_data = json.loads(response.text)
        question = html.unescape(json_data['results'][0]['question'])
        correct_answer = html.unescape(
            json_data['results'][0]['correct_answer'])
        answers = list(map(lambda x: html.unescape(
            x), json_data['results'][0]['incorrect_answers']))
        answers.append(correct_answer)
        random.shuffle(answers)
        answer_pos = answers.index(correct_answer)

        emojis = ['\u0031\u20E3', '\u0032\u20E3',
                  '\u0033\u20E3', '\u0034\u20E3']
        winning_emoji = emojis[answer_pos]
        embed_question = discord.Embed(title=question, color=0x00ff00)
        for i, answer in enumerate(answers):
            embed_question.add_field(name=emojis[i], value=answer, inline=True)
        question_object = await ctx.send(embed=embed_question)

        for i, answer in enumerate(answers):
            await question_object.add_reaction(emoji=emojis[i])

        def react_check(msg):
            def check(reaction, reacting_user):
                return reacting_user == ctx.author and str(reaction.emoji) in emojis and reaction.message.id == msg.id
            return check

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=react_check(question_object))
            if str(reaction.emoji) == winning_emoji:
                await ctx.send(f"{random.choice(self.congrats)}\nAnswer was: {correct_answer}")
            else:
                await ctx.send(f"Can't beleive you dont know this, all my bot friends know this!\nAnswer was: {correct_answer}")
        except:
            await ctx.send(f"Timed out!\nAnswer was: {correct_answer}")

    @commands.command()
    async def tictactoe(self, ctx):
        """
            It's TicTacToe! Now with PvP

        """
        emojis = ['\u0031\u20E3', '\u0032\u20E3']
        letters = {'X': '\u274C', 'O': '\u2B55'}
        embed_tac = discord.Embed(title='How many players?', color=0x00ff00)
        player_count = await ctx.send(embed=embed_tac)

        await player_count.add_reaction(emoji=emojis[0])
        await player_count.add_reaction(emoji=emojis[1])

        def react_check(msg):
            def check(reaction, reacting_user):
                return reacting_user == ctx.author and str(reaction.emoji) in emojis and reaction.message.id == msg.id
            return check

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=60.0, check=react_check(player_count))
            if str(reaction.emoji) == emojis[0]:
                PvP = False
            else:
                PvP = True

            try:
                letter = random.choice([*letters])
                await ctx.send(f"You are {letters[letter]}")
                tttGame = TicTacToe(letter, ctx, self.client, PvP)
                await tttGame.drawBoard()
                if PvP:
                    await tttGame.mainGamePvP()
                if not PvP:
                    await tttGame.mainGame()
            except Exception as e:
                print(e)
                await ctx.send('Game Over!')

        except:
            await ctx.send("Timed out!")

    @commands.command()
    async def werewolf(self, ctx):
        """Can you find the werewolves before they find you?"""
        embed_rules = discord.Embed(title="Werewolf", color=0x00ff00)

        embed_rules.add_field(
            name='How to Play?', value='https://www.playwerewolf.co/how-to-play-werewolf-in-75-seconds', inline=False)
        embed_rules.add_field(name='Discord Specific: How to Play?', value='Those with special roles will be dm\'d instructions during the night cycle. Only one werewolf can choose who to kill each night, make sure to discuss it with each other via dm. Lastly when voting for who to lynch during the day, reply to the bot with the number of who you choose to kill. To help with voting make use of the $poll command', inline=False)
        embed_rules.add_field(
            name='How to Join', value='To play react to this message', inline=False)

        msg = await ctx.send(embed=embed_rules)
        await msg.add_reaction(emoji='\U00002705')
        await asyncio.sleep(15)

        cache_msg = discord.utils.get(self.client.cached_messages, id=msg.id)
        reaction = cache_msg.reactions[0]
        users = await reaction.users().flatten()
        users = [x for x in users if str(x) != str(self.client.user)]
        if 5 < len(users) < 17:
            ww = Werewolf(ctx, self.client, users)
            await ww.main()
        else:
            await ctx.send("Game requires 6 to 16 players!")

    @commands.command()
    async def blackjack(self, ctx):
        """Can you beat the Dealer?"""
        objective = """
            Beat The Dealer. There are some misconceptions about the objective of the game of blackjack but at the simplest level all you are trying to do is beat the dealer.
        """
        how_to_play1 = """
            • By drawing a hand value that is higher than the dealer’s hand value
            • By the dealer drawing a hand value that goes over 21.
            • By drawing a hand value of 21 on your first two cards, when the dealer does not."""
        how_to_play2 = """
            • Your hand value exceeds 21.
            • The dealers hand has a greater value than yours at the end of the round
            """
        find_value = """
            • 2 through 10 count at face value, i.e. a 2 counts as two, a 9 counts as nine.
            • Face cards (J,Q,K) count as 10.
            • Ace can count as a 1 or an 11 depending on which value helps the hand the most.
            """

        embed_rules = discord.Embed(title="Blackjack", color=0x00ff00)

        embed_rules.add_field(name='Objective', value=objective, inline=False)
        embed_rules.add_field(
            name='How do you beat the dealer?', value=how_to_play1, inline=False)
        embed_rules.add_field(
            name='How do you lose to the dealer? ', value=how_to_play2, inline=False)
        embed_rules.add_field(
            name='How Do You Find a Hand’s Total Value?', value=find_value, inline=False)
        embed_rules.add_field(
            name='How to Play?', value='Type hit for another card, type stand to keep your hand. Bet 0 to walk away!', inline=False)
        embed_rules.add_field(
            name='How to Join', value='To play react to this message', inline=False)

        msg = await ctx.send(embed=embed_rules)
        await msg.add_reaction(emoji='\U00002705')
        await asyncio.sleep(15)

        cache_msg = discord.utils.get(self.client.cached_messages, id=msg.id)
        reaction = cache_msg.reactions[0]
        users = await reaction.users().flatten()
        users = [x for x in users if str(x) != str(self.client.user)]
        if len(users) > 0:
            bj = BlackJack(len(users), ctx, self.client, users)
            await bj.main()
        else:
            await ctx.send("You need at least 1 to play!")

    @commands.command()
    async def codenames(self, ctx):
        """Get the secret code to your operatives in the field"""
        objective = """
            The aim of the game is to find all of your teams words in the word grid. First team to Zero wins.
        """
        how_to_play = """
            You need at least four players (two teams of two, red and blue) for a standard game. 
            Each team has one player as their spymaster. Both spymasters will be sent a dm with the answer key.
            \nIf you are the spymaster, you are trying to think of a one-word clue that relates to some of the words your team is trying to guess. 
            When you think you have a good clue, you say it. You also say one number, which tells your teammates how many codenames are related to your clue."""
        Example1 = """Example: Two of your words are NUT and BARK. Both of these grow on trees, so you say tree: 2. 
            You are allowed to give a clue for only one word (cashew: 1 ) but it's fun to try for two or more. """

        how_to_play2 = """Getting four words with one clue is a big accomplishment. The field operatives must always make at least one guess. 
            Any wrong guess ends the turn immediately, but if the field operatives guess a word of their team's color, they can keep guessing. 
            You have 120 seconds for each word to guess. To guess a word type it into the chat. Once you have guessed as many words as your spymaster has linked. Your turn is over.
            Type end_turn to finish your turn or stop to end the game. Careful where you pick, choose incorrectly and find the assassin, that's Game Over!"""

        embed_rules = discord.Embed(title="Codenames", color=0x00ff00)

        embed_rules.add_field(name='Objective', value=objective, inline=False)
        embed_rules.add_field(name='How to Play',
                              value=how_to_play, inline=False)
        embed_rules.add_field(name='Example', value=Example1, inline=False)
        embed_rules.add_field(name='How to Play contd',
                              value=how_to_play2, inline=False)
        embed_rules.add_field(
            name='How to Join', value='To play react to this message', inline=False)

        msg = await ctx.send(embed=embed_rules)
        await msg.add_reaction(emoji='\U00002705')
        await asyncio.sleep(15)

        cache_msg = discord.utils.get(self.client.cached_messages, id=msg.id)
        reaction = cache_msg.reactions[0]
        users = await reaction.users().flatten()
        users = [x for x in users if str(x) != str(self.client.user)]
        if len(users) > 3:
            CN = Codename(ctx, self.client, users)
            await CN.main()
        else:
            await ctx.send("You need at least 4 to play!")

    @commands.command()
    async def cah(self, ctx, rounds=5):
        """A card game for horrible people

        Args:
            rounds (int, optional): [Set how many round to play]. Defaults to 5.
        """
        embed_rules = discord.Embed(
            title="Cards Against Humanity", color=0x00ff00)

        embed_rules.add_field(name='Description', value="Cards Against Humanity is a party game for horrible people. Unlike most of the party games you've played before, Cards Against Humanity is as despicable and awkward as you and your friends.", inline=False)
        embed_rules.add_field(name='How to Play?', value="The game is simple. Each round, one player asks a question from a black card, and everyone else answers with their funniest white card. To choose a card, click the appropriate emoji. Each round, each player will chose their cards by round robin", inline=False)
        embed_rules.add_field(
            name='How to Join', value='To play react to this message', inline=False)

        msg = await ctx.send(embed=embed_rules)
        await msg.add_reaction(emoji='\U00002705')
        await asyncio.sleep(10)

        cache_msg = discord.utils.get(self.client.cached_messages, id=msg.id)
        reaction = cache_msg.reactions[0]
        users = await reaction.users().flatten()
        users = [x for x in users if str(x) != str(self.client.user)]
        if 2 < len(users) < 9:
            game = CAH(ctx, self.client, rounds, users)
            await game.main()
        else:
            await ctx.send("Game requires 3 to 8 players!")


def setup(client):
    client.add_cog(Games(client))
