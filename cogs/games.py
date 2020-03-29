import discord
from discord.ext import commands
import requests, html, random, json, asyncio




class Hangman():
    def __init__(self, ctx, client, congrats):
        self.words =  """grape catapult dog baboon elephant giraffe apple coconut monkey rubik mice mouse pineapple android apple house fence python grail zebra protein terrain llama fire policeman zebra lion fluffy
        America Balloon Biscuit Blanket Chicken Chimney Country Cupcake Curtain Diamond Eyebrow Fireman Florida Germany Harpoon Husband Morning Octopus Popcorn Printer Sandbox Skyline Spinach
        Backpack Basement Building Campfire Complete Elephant Exercise Hospital Internet Jalapeno Mosquito Sandwich Scissors Seahorse Skeleton Snowball Sunshade Treasure
        Blueberry Breakfast Bubblegum Cellphone Dandelion Hairbrush Hamburger Horsewhip Jellyfish Landscape Nightmare Pensioner Rectangle Snowboard Spaceship Spongebob Swordfish Telephone Telescope
        Bellpepper Broomstick Commercial Flashlight Lighthouse Lightsaber Microphone Photograph Skyscraper Strawberry Sunglasses Toothbrush Toothpaste
        """.lower().split()
        self.ctx = ctx
        self.client = client
        self.lives = 5
        self.word_to_guess = random.choice(self.words)
        self.split_wtg = [char for char in self.word_to_guess]
        self.cg= ["_"]*len(self.split_wtg)#prints a list the length of the hidden word
        self.letters_left="a b c d e f g h i j k l m n o p q r s t u v w x y z".split()
        self.congrats = congrats
        self.rounds = 0

    def game(self, guess):
        """iterates through the split word and if the letter guess is at that element then place that letter in the 
        current guess list, if not then increment count. After the for loop concludes if no matches were found
        then decrement number of lives"""
        count = 0
        for i in range(len(self.split_wtg)):
            if guess == self.split_wtg[i]:
                self.cg[i]= guess
            else:
                count += 1
        if count == len(self.split_wtg):
            self.lives -= 1

    def string_format(self, letters_list):
        text = ''
        for i in letters_list:
            text += i + ' | ' 
        return text

    def string_format2(self, cg):
        text = "```{}```".format(" ".join(cg))
        return text



    async def maingame(self):
        def letter_check(m):
            return (m.content in self.letters_left or m.content.lower() == "stop") and m.guild == self.ctx.guild
        await self.ctx.send(f"Word has {len(self.cg)} letters")
        while self.cg!=self.split_wtg:#While guessed word is not equal to the hidden word 
            try:
                # await self.ctx.send("Choose your letter")

                try:
                    guess = await self.client.wait_for('message', timeout=45.0, check=letter_check)

                except Exception as e:
                    await self.ctx.send(e)
                    await self.ctx.send("Timed Out!")
                    break

                self.letters_left.remove(guess.content)
                self.game(guess.content)
                letters_string = self.string_format(self.letters_left)
                embed = discord.Embed(title="Hangman", color=0x00ff00)
                embed.add_field(name="Letters Left", value=letters_string, inline=False)
                embed.add_field(name="Lives", value=self.lives, inline=False)
                embed.add_field(name="Current Guess", value=self.string_format2(self.cg), inline=False)

                if self.rounds % 5 == 0:
                    self.hangman_msg = await self.ctx.send(embed=embed)
                else:
                    await self.hangman_msg.edit(embed=embed)

                if self.lives == 0:
                    await self.ctx.send(f"Word was {self.word_to_guess}")
                    break#break the inside game loop, prompts the user to play again
                self.rounds += 1
            except Exception as e:
                # print(e)
                continue
        if self.cg == self.split_wtg:
            await self.ctx.send(random.choice(self.congrats))
        else:
            await self.ctx.send("Better Luck Next Time!")


class TicTacToe():
    
    def __init__(self,player_letter, ctx, client, PvP):
        self.board = ["___",'\u0031\u20E3','\u0032\u20E3','\u0033\u20E3','\u0034\u20E3','\u0035\u20E3','\u0036\u20E3','\u0037\u20E3','\u0038\u20E3','\u0039\u20E3']
        self.turns = [1,2,3,4,5,6,7,8,9]
        self.player_letter = player_letter
        self.ctx = ctx
        self.client = client
        self.rounds = 0
        self.letter_dict = {'X': '\u274C','O': '\u2B55'}
        if PvP:
            self.player2_letter = self.other_letter(player_letter)
        else:
            self.comp_letter = self.other_letter(player_letter)

    async def drawBoard(self):
        """Prints the board in the correct format"""
        tic_embed = discord.Embed(title='TicTacToe', color=0x00ff00)
        tic_embed.add_field(name=".", value=self.board[7], inline=True)
        tic_embed.add_field(name=".", value=self.board[8], inline=True)
        tic_embed.add_field(name=".", value=self.board[9], inline=True)
        tic_embed.add_field(name=".", value=self.board[4], inline=True)
        tic_embed.add_field(name=".", value=self.board[5], inline=True)
        tic_embed.add_field(name=".", value=self.board[6], inline=True)
        tic_embed.add_field(name=".", value=self.board[1], inline=True)
        tic_embed.add_field(name=".", value=self.board[2], inline=True)
        tic_embed.add_field(name=".", value=self.board[3], inline=True)

        if self.rounds < 1:
            self.game_board = await self.ctx.send(embed=tic_embed)
            for i in range(9):
                await self.game_board.add_reaction(emoji=self.board[1:][i])
        else:
            await self.game_board.edit(embed=tic_embed)




    def player_move(self, move, letter):
        """Updates the board with the players turn, removes that option from turns"""
        self.turns.remove(move)
        self.board[move] = self.letter_dict[letter] 
        
    def other_letter(self, letter):
        """If player is X, comp is O visa versa"""
        if letter == "X":
            return "O"
        else:
            return "X"

    def victory(self, board):
        """Returns True if any victory conditions are met"""
        return (((board[7] == board[8]) and  (board[8] == board[9])) or 
        ((board[4] == board[5]) and  (board[5] == board[6])) or # across the middle
        ((board[1] == board[2]) and  (board[2] == board[3])) or # across the bottom
        ((board[1] == board[4]) and  (board[4] == board[7])) or # down the left side
        ((board[2] == board[5]) and  (board[5] == board[8])) or # down the middle
        ((board[3] == board[6]) and  (board[6] == board[9])) or # down the right side
        ((board[1] == board[5]) and  (board[5] == board[9])) or # diagonal
        ((board[7] == board[5]) and  (board[5] == board[3]))) # diagonal

    async def comp_move_ai(self):
        """Makes a copy of the board, then iterates through all the remaining turns, 
        firstly to see if there is any move that will result in victory for the computer.
        Then to see if there are any moves which will see the player win, if so blocks that move. If no move will lead
        to victory then the computer randomly chooses its move"""
        
        #checking for victory move for computer, must come before block loop
        for i in range(len(self.turns)):
            test_board = self.board[:]
            test_board[self.turns[i]] = self.letter_dict[self.comp_letter]
            if self.victory(test_board):
                self.board[self.turns[i]] = self.letter_dict[self.comp_letter]#if victory update the board and remove from turns list    
                self.turns.remove(self.turns[i])
                # await self.drawBoard()
                return
        #checking for blocking move for comp
        for i in range(len(self.turns)):
            test_board = self.board[:]
            test_board[self.turns[i]] = self.letter_dict[self.player_letter]
            if self.victory(test_board):
                self.board[self.turns[i]] = self.letter_dict[self.comp_letter]#if victory update the board and remove from turns list    
                self.turns.remove(self.turns[i])
                # await self.drawBoard()
                return


        comp = random.choice(self.turns)#turns keeps track of options we have left, this line randomly chooses
        self.board[comp] = self.letter_dict[self.comp_letter]
        self.turns.remove(comp)
        # await self.drawBoard()


        

    async def mainGame(self):
        def move_check(m):
            return (m.content in list(map(lambda x: str(x), self.turns))  or m.content.lower() == "stop")

        def react_check(msg):
            def check(reaction, reacting_user):
                return reacting_user != self.client.user and str(reaction.emoji) in self.board and reaction.message.id==msg.id and self.board.index(str(reaction.emoji)) in self.turns
            return check
        flag = True
        while flag:#while no victory is determined or while there are turns left to make
            self.rounds += 1
            # await self.ctx.send("Choose your spot\n")

            try:
                # move = await self.client.wait_for('message', timeout=45.0, check=move_check)
                reaction, user= await self.client.wait_for('reaction_add', timeout=30.0, check=react_check(self.game_board))
                move = self.board.index(str(reaction.emoji))
            except:
                await self.ctx.send('Timed Out!')
                break

            else:
                self.player_move(int(move), self.player_letter)
                await self.drawBoard()
                if self.turns == []  or self.victory(self.board):
                    #if no moves left or victory reached, otherwise computers turn
                    flag = False
                    await self.drawBoard()
                else:
                    await asyncio.sleep(0.5)
                    await self.comp_move_ai()
                    await self.drawBoard()
                    if self.turns == []  or self.victory(self.board):
                        flag = False
            
        await self.ctx.send("Game Over!")

    async def player_move_code(self, player):
        def react_check(msg):
            def check(reaction, reacting_user):
                return reacting_user != self.client.user and str(reaction.emoji) in self.board and reaction.message.id==msg.id and self.board.index(str(reaction.emoji)) in self.turns
            return check

        try:
            reaction, user= await self.client.wait_for('reaction_add', timeout=30.0, check=react_check(self.game_board))
            move = self.board.index(str(reaction.emoji))
            return move
        except Exception as e:
            print(e)
            await self.ctx.send('Timed Out!')
            flag = False

    async def mainGamePvP(self):


        flag = True
        move = ""
        while flag:#while no victory is determined or while there are turns left to make
            self.rounds += 1
            move = await self.player_move_code("Player 1")

            self.player_move(int(move), self.player_letter)
            await self.drawBoard()
            if self.turns == []  or self.victory(self.board):
                #if no moves left or victory reached, otherwise computers turn
                flag = False
            else:
                move = await self.player_move_code("Player 2")
                self.player_move(int(move), self.player2_letter)
                await self.drawBoard()
                if self.turns == []  or self.victory(self.board):
                    flag = False

        await self.ctx.send("Game Over!")

class Games(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.congrats = congrats = ["Wow, turns our youre like smart or something", "Powerful, impressive, firm and unforgettable. But enough about your farting... Congrats!", "Congratulations on finding your balls",
"Wow, Well done, your Mother and I are very proud", "You have performed extremely adequately.", "You surprised me a little bit. I knew you were capable, but I didn't expect this level of accomplishment!",
"I genuinely thought you'd fail again", "Ooooh look at you all clever and shit!"]
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("Pong!")


    @commands.command()
    async def hangman(self, ctx):
        hm = Hangman(ctx, self.client, self.congrats)
        await hm.maingame()


    @commands.command()
    async def quiz(self, ctx):
        """
        Gets a question and answer from the api, extracts answers and combines correct answer with the others, then shuffles. Question and answers are sent to the server after 
        after being linked to an emoji, then linked emojis act as buttons to select answers. The bot waits for the user who sent $quiz to react with an appropriate
        emoji then reveals the answer.

        NOTE: The url sometimes returns html/xml encoded strings, so I deal with it with htmml.unescape

        """
        response = requests.get('https://opentdb.com/api.php?amount=1&type=multiple')
        json_data = json.loads(response.text)
        question = html.unescape(json_data['results'][0]['question'])
        correct_answer = html.unescape(json_data['results'][0]['correct_answer'])
        answers = list(map(lambda x: html.unescape(x), json_data['results'][0]['incorrect_answers']))
        answers.append(correct_answer)
        random.shuffle(answers)
        answer_pos = answers.index(correct_answer)


        emojis = ['\u0031\u20E3','\u0032\u20E3','\u0033\u20E3','\u0034\u20E3']
        winning_emoji = emojis[answer_pos]
        embed_question = discord.Embed(title=question, color=0x00ff00)
        for i, answer in enumerate(answers):
            embed_question.add_field(name=emojis[i], value=answer, inline=True)
        question_object = await ctx.send(embed=embed_question)

        for i, answer in enumerate(answers):
            await question_object.add_reaction(emoji=emojis[i])

        def react_check(msg):
            def check(reaction, reacting_user):
                return reacting_user == ctx.author and str(reaction.emoji) in emojis and reaction.message.id==msg.id
            return check

        try:
            reaction, user= await self.client.wait_for('reaction_add', timeout=60.0, check=react_check(question_object))
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
        emojis = ['\u0031\u20E3','\u0032\u20E3']
        letters = {'X': '\u274C','O': '\u2B55'}
        embed_tac = discord.Embed(title='How many players?', color=0x00ff00)
        player_count = await ctx.send(embed=embed_tac)

        await player_count.add_reaction(emoji=emojis[0])
        await player_count.add_reaction(emoji=emojis[1])

        def react_check(msg):
            def check(reaction, reacting_user):
                return reacting_user == ctx.author and str(reaction.emoji) in emojis and reaction.message.id==msg.id
            return check

        try:
            reaction, user= await self.client.wait_for('reaction_add', timeout=60.0, check=react_check(player_count))
            if str(reaction.emoji) == emojis[0]:
                PvP = False
            else: PvP = True

            def check(m):
                return (m.content.upper() == 'X' or m.content.upper() == 'O')

            try:
                letter = random.choice([*letters])
                await ctx.send(f"You are {letters[letter]}")
                tttGame = TicTacToe(letter,ctx, self.client, PvP)
                await tttGame.drawBoard()
                if PvP:
                    await tttGame.mainGamePvP()
                if not PvP:
                    await tttGame.mainGame()
            except Exception as e:
                await ctx.send(e)
                await ctx.send('Timed Out!')

        except Exception as e:
            print(e)
            await ctx.send("Timed out!")
 

def setup(client):
    client.add_cog(Games(client))