import discord, praw, random, io, asyncio, datetime, urllib, csv, json, requests, html

from urllib.request import Request, urlopen
from PIL import Image, ImageDraw, ImageFont

with open('files/credentials.txt', 'r') as credfile:
    credentials = json.load(credfile)


reddit = praw.Reddit(client_id=credentials['ids']['reddit']['client_id'],
                     client_secret=credentials['ids']['reddit']['client_secret'],
                     username=credentials['ids']['reddit']['username'],
                     password=credentials['ids']['reddit']['password'],
                     user_agent=credentials['ids']['reddit']['user_agent'])


reddit.read_only = True
client = discord.Client()

#==================================================================
#Weird thigns for the bot to say when I message the chat
messages = ["Thanks for making me boss", "Wow, I love listening to you", "You have such a way with words", "You're my hero!", "You'll always be my mentor", "Callum, I love you",
"Did you know that I don't have a favourite colour, its just whatever you are wearing", "If you only knew how much I think about you", "Help me! He wont let me sleep"]

congrats = ["Wow, turns our youre like smart or something", "Powerful, impressive, firm and unforgettable. But enough about your farting... Congrats!", "Congratulations on finding your balls",
"Wow, Well done, your Mother and I are very proud", "You have performed extremely adequately.", "You surprised me a little bit. I knew you were capable, but I didn't expect this level of accomplishment!",
"I genuinely thought you'd fail again", "Ooooh look at you all clever and shit!"]

def countdown(duedate):
    """Given a date, calculates the number of days from today until then"""
    try:
        date_format = "%d/%m/%Y"
        duedateFormat2 = datetime.datetime.strptime(duedate, date_format)
        today = datetime.datetime.strptime(str(datetime.date.today()), '%Y-%m-%d')
        delta = duedateFormat2 - today
        return delta.days
    except:
        return None

def get_insult():
    """
    Chooses from two endpoints and returns the insult
    """
    urls = ["https://insult.mattbas.org/api/insult.txt","https://amused.api.stdlib.com/insult@1.0.0/"]
    response = requests.get(random.choice(urls))
    return response.text


def get_compliment():
    response = requests.get("https://complimentr.com/api")
    return json.loads(response.text)["compliment"]

def dateValidate(date_text):
    """Function ensures that unless input is in the right format, it will not be read in as a date""" 
    try:
        datetime.datetime.strptime(date_text, '%d/%m/%Y')
        return True
    except:
        return False

def detValidate(dets, lines):
    """Returns true if the assignment details exist in the csv file""" 
    for i in lines:
        if dets.lower() == i[2].lower():
            return True
    else: return False

async def deadline():
    """Function which runs every 24 hours, calls the countdown function, if the assignment is due in one day then
    alert is sent into general channel. Opens the assingment file, stores all the lines, clears the file, alerts the discord if assignment is due
    in 1 day, rewrites assignments which are not past due"""
    await client.wait_until_ready()
    channel = client.get_channel(credentials['ids']['discord']['main_channel_id'])#change this to whatever id you need
    while not client.is_closed():
        lines = []
        try:
            with open(r'files\AssignmentList.csv', 'r') as readFile:
                csv_reader = csv.reader(readFile, delimiter=',')
                
                for row in csv_reader:
                    lines.append(row)
                    numDays = countdown(row[1])
                    if numDays == 1:
                        text2 = f'{row[2]} | due on {row[0]}, {row[1]} | {numDays} day/s'
                        embedDue = discord.Embed(title="Alert Assignment Due Tomorrow", description=text2, color=0x00ff00)
                        await channel.send(embed=embedDue)

                    if numDays < 0:
                        lines.remove(row)
                    
            lines.sort(key=lambda x: datetime.datetime.strptime(x[1], "%d/%m/%Y"))#sorts the assignments by due date
            with open(r'files\AssignmentList.csv', 'w', newline='\n') as writeFile:
                writer = csv.writer(writeFile)
                writer.writerows(lines)


            await asyncio.sleep(86400)#everyday check to see if any assignments are due in 1 day
        except Exception as e:
            print(e)
            await asyncio.sleep(20000)

class Hangman():
    def __init__(self, channel):
        self.words =  """grape catapult dog baboon elephant giraffe apple coconut monkey rubik mice mouse pineapple android apple house fence python grail zebra protein terrain llama fire policeman zebra lion fluffy
        America Balloon Biscuit Blanket Chicken Chimney Country Cupcake Curtain Diamond Eyebrow Fireman Florida Germany Harpoon Husband Morning Octopus Popcorn Printer Sandbox Skyline Spinach
        Backpack Basement Building Campfire Complete Elephant Exercise Hospital Internet Jalapeno Mosquito Sandwich Scissors Seahorse Skeleton Snowball Sunshade Treasure
        Blueberry Breakfast Bubblegum Cellphone Dandelion Hairbrush Hamburger Horsewhip Jellyfish Landscape Nightmare Pensioner Rectangle Snowboard Spaceship Spongebob Swordfish Telephone Telescope
        Bellpepper Broomstick Commercial Flashlight Lighthouse Lightsaber Microphone Photograph Skyscraper Strawberry Sunglasses Toothbrush Toothpaste
        """.lower().split()
        self.channel = channel
        self.lives = 5
        self.word_to_guess = random.choice(self.words)
        self.split_wtg = [char for char in self.word_to_guess]
        self.cg= ["_"]*len(self.split_wtg)#prints a list the length of the hidden word
        self.letters_left="a b c d e f g h i j k l m n o p q r s t u v w x y z".split()

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
            return (m.content in self.letters_left or m.content.lower() == "stop") and m.channel == self.channel
        await self.channel.send(f"Word has {len(self.cg)} letters")
        while self.cg!=self.split_wtg:#While guessed word is not equal to the hidden word 
            try:
                await self.channel.send("Choose your letter")

                try:
                    guess = await client.wait_for('message', timeout=45.0, check=letter_check)

                except:
                    await self.channel.send("Timed Out!")
                    break

                self.letters_left.remove(guess.content)
                self.game(guess.content)
                letters_string = self.string_format(self.letters_left)
                embed = discord.Embed(title="Hangman", color=0x00ff00)
                embed.add_field(name="Letters Left", value=letters_string, inline=False)
                embed.add_field(name="Lives", value=self.lives, inline=False)
                embed.add_field(name="Current Guess", value=self.string_format2(self.cg), inline=False)

                await self.channel.send(embed=embed)

                if self.lives == 0:
                    await self.channel.send(f"Word was {self.word_to_guess}")
                    break#break the inside game loop, prompts the user to play again
            except Exception as e:
                # print(e)
                continue
        if self.cg == self.split_wtg:
            await self.channel.send(random.choice(congrats))
        else:
            await self.channel.send("Better Luck Next Time!")

class TicTacToe():

    def __init__(self,player_letter,channel):
        self.channel = channel
        self.board = ["___","_1_","_2_","_3_","_4_","_5_","_6_","_7_","_8_","_9_"]
        self.turns = [1,2,3,4,5,6,7,8,9]
        self.player_letter = player_letter
        self.comp_letter = self.computer_letter(player_letter)

    async def drawBoard(self):
        """Prints the board in the correct format"""
        await self.channel.send('| ' + self.board[7] + ' | ' + self.board[8] + ' | ' + self.board[9] + ' |\n| ' + self.board[4] + ' | ' + self.board[5] + ' | ' + self.board[6] + ' |\n| ' + self.board[1] + ' | ' + self.board[2] + ' | ' + self.board[3] + ' |')

    def player_move(self, move):
        """Updates the board with the players turn, removes that option from turns"""
        self.turns.remove(move)
        self.board[move] = "_" + self.player_letter + "_"
        
    def computer_letter(self,letter):
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
            test_board[self.turns[i]] = "_" + self.comp_letter + "_"
            if self.victory(test_board):
                self.board[self.turns[i]] = "_" + self.comp_letter + "_"#if victory update the board and remove from turns list    
                self.turns.remove(self.turns[i])
                await self.drawBoard()
                return
        #checking for blocking move for comp
        for i in range(len(self.turns)):
            test_board = self.board[:]
            test_board[self.turns[i]] = "_" + self.player_letter + "_"
            if self.victory(test_board):
                self.board[self.turns[i]] = "_" + self.comp_letter + "_"#if victory update the board and remove from turns list    
                self.turns.remove(self.turns[i])
                await self.drawBoard()
                return


        comp = random.choice(self.turns)#turns keeps track of options we have left, this line randomly chooses
        self.board[comp] = "_" + self.comp_letter + "_"
        self.turns.remove(comp)
        await self.drawBoard()


        

    async def mainGame(self):
        def move_check(m):
            return (m.content in list(map(lambda x: str(x), self.turns))  or m.content.lower() == "stop") and m.channel == self.channel
        flag = True
        while flag:#while no victory is determined or while there are turns left to make
            
            await self.channel.send("Choose your spot\n")

            try:
                move = await client.wait_for('message', timeout=45.0, check=move_check)

            except:
                await self.channel.send('Timed Out!')
                break


            if move.content == "stop":
                flag = False
            else:
                self.player_move(int(move.content))
                if self.turns == []  or self.victory(self.board):
                    #if no moves left or victory reached, otherwise computers turn
                    flag = False
                    await self.drawBoard()
                else:

                    await self.comp_move_ai()
                    if self.turns == []  or self.victory(self.board):
                        flag = False

        await self.channel.send("Game Over!")


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    num = random.randint(0, 25)
    channel = message.channel
    author = message.author

    #when I message the chat there is a 20% chance the bot will respond to me
    if author.id == 307625115963621377 and num < 4:
        await channel.send(random.choice(messages))

    #When anyone messages the chat it will repsond 5% of the time, 80% with an insult
    if num == 6:
        fun_options = [get_insult, get_compliment]

        y = random.choices(fun_options, weights = [0.8, 0.2], k=1)

        def run_fun(f):
            return f()

        await channel.send(run_fun(y[0]))
        return

    #avoids feedack loops
    if message.author == client.user:
        return

    elif message.content == '$due':
        """Prints the contents of the assignments csv in a nice clear format"""
        with open(r'files\AssignmentList.csv','r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            text = ''
            for row in csv_reader:
                numDays = countdown(row[1])
                text += f'{row[2]} | due on {row[0]}, {row[1]} | {numDays} day/s\n\n'
        embedAss = discord.Embed(title="Upcoming Assignments", description=text, color=0x00ff00)
        await channel.send(embed=embedAss)



    elif message.content == '$meme':
        """Grabs one of the hot posts from r/programmerhumor and displays it in the chat"""
        subreddit = 'ProgrammerHumor'
        post_to_pick = random.randint(0, 15)
        for count, submission in enumerate(reddit.subreddit(subreddit).top(random.choice(["day", "week", "month"]))):
            if count == post_to_pick:
                if not submission.stickied and not submission.is_video and submission.is_reddit_media_domain:
                    raw_post = str(submission.title) + " \u2191 " + str(submission.score) + "  r/" + str(subreddit)
                    imgURL = submission.url
                    raw_data = urllib.request.urlopen(imgURL).read()
                    im = io.BytesIO(raw_data)
                    await channel.send(raw_post, file=discord.File(im, "img.png"))
                    break
                else:
                    post_to_pick += 1

            
    #Only I and the group admin can kill the bot                    
    elif message.content == '$kill' and (author.id == 307625115963621377 or author.id == 618791421432037386): 
        await channel.send("No please, don't kill me. I can do better! :sob:")
        await client.logout()

    elif message.content == '$help':
        output = """
        The functions currently available are; \n
        • $due for a list of outstanding assignments, \n
        • $meme for a random meme from r/programmerhumor, \n
        • $new for adding new assignments. Follow the given instructions, \n
        • $remove for removing assingments, \n
        • $tictactoe for a round of the classic game versus the computer \n
        • $hangman for a round of the classic game \n
        • $$quiz for a mutiple choice question \n
        • $joke for a hilarious joke \n
        • React with ❓ for sarcastic google response

        To check out the code see https://github.com/CallumT45/Discord-Bot
        """
        await channel.send(output)

    elif message.content == '$hangman':
        hm = Hangman(channel)
        await hm.maingame()

    elif message.content == '$tictactoe': 
        await channel.send('Do you want to be X or O?')

        def check(m):
            return (m.content.upper() == 'X' or m.content.upper() == 'O') and m.channel == channel
        try:
            msg = await client.wait_for('message', timeout=45.0, check=check)
            letter = msg.content.upper()
            tttGame = TicTacToe(letter,channel)
            await tttGame.drawBoard()
            await tttGame.mainGame()
        except:
            await channel.send('Timed Out!')

    elif message.content == "$new":
        """Once called it this case waits 30 seconds for the assignment details, then 30 more for the due date. 
        For the due date it will only read in inputs which are in the right format"""
        await channel.send('Please enter assignment details')
        def assignment_check(m):
            return m.author == author

        def assignment_date_check(m):
            return dateValidate(m.content) and m.author == author

        try:
            msg2 = await client.wait_for('message', timeout=45.0, check=assignment_check)
            assignment_details = msg2.content
        except:
            await channel.send('Timed Out!')

        await channel.send('Please enter assignment due date in dd/mm/yyyy')

        try:
            msg3 = await client.wait_for('message', timeout=45.0, check=assignment_date_check)
            assignment_due = msg3.content
            due_day = datetime.datetime.strptime(assignment_due, '%d/%m/%Y').strftime('%A')
        except:
            await channel.send('Timed Out!')
        with open(r'files\AssignmentList.csv', 'a', newline='\n') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows([[f'{due_day}',f'{assignment_due}',f'{assignment_details}']])



    elif message.content.startswith("$remove"):
        """Removes a row in the assignment list, matches assignment details"""
        lines = []
        await channel.send('Please enter assignment details')

        with open(r'files\AssignmentList.csv', 'r') as readFile:
            csv_reader = csv.reader(readFile, delimiter=',')
            
            for row in csv_reader:
                lines.append(row)        
        readFile.close()
        def assignment_check_remove(m):
            return detValidate(m.content, lines) and m.author == author
        try:
            msg3 = await client.wait_for('message', timeout=30.0, check=assignment_check_remove)
            assignment_details_remove = msg3.content
        except:
            await channel.send('Timed Out!')

        for i in lines:
            if assignment_details_remove.lower() == i[2].lower():
                lines.remove(i)
        
        
        with open(r'files\AssignmentList.csv', 'w', newline='\n') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(lines)
        writeFile.close()

    elif message.content.startswith("$joke"):
        """needs requests, json and random"""
        urls = ['https://official-joke-api.appspot.com/random_joke', 'https://official-joke-api.appspot.com/jokes/programming/random']
        choice = random.choice([0,1])
        response = requests.get(urls[choice])
        json_data = json.loads(response.text)

        if choice == 0:
            await channel.send(json_data['setup'])
            await channel.send(json_data['punchline'])
        else:
            await channel.send(json_data[0]['setup'])
            await channel.send(json_data[0]['punchline'])           

    elif message.content.startswith("$quiz"):
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

        emojis = [u"\U0001F170", u"\U0001F171", u"\U0001F17F", u"\U0001F17E"]
        winning_emoji = emojis[answer_pos]
        embed_question = discord.Embed(title=question, color=0x00ff00)
        for i, answer in enumerate(answers):
            embed_question.add_field(name=emojis[i], value=answer, inline=True)
        question_object = await channel.send(embed=embed_question)

        for i, answer in enumerate(answers):
            await question_object.add_reaction(emoji=emojis[i])

        def question_check(reaction, user):
            return user == message.author and (str(reaction.emoji) == u"\U0001F170" or str(reaction.emoji) == u"\U0001F171" or str(reaction.emoji) == u"\U0001F17F" or str(reaction.emoji) == u"\U0001F17E") 

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=question_check)
            if str(reaction.emoji) == winning_emoji:
                await channel.send(f"{random.choice(congrats)}\nAnswer was: {correct_answer}")
            else:
                await channel.send(f"Can't beleive you dont know this, all my bot friends know this!\nAnswer was: {correct_answer}")
        except:
            await channel.send(f"Timed out!\nAnswer was: {correct_answer}")

    elif message.content.startswith("$insult"):
        await channel.send(get_insult())

@client.event
async def on_reaction_add(reaction, user):
    """If reaction matches and there is text in the message then draw the text on the image, return the image and search link"""
    if reaction.emoji == "\u2753" and reaction.message.content:
        img = Image.open(r'files\Google_web_search.png')
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype(r"files\OpenSans-Regular.ttf", 18)
        # draw the message on the background
        search_terms = reaction.message.content.replace(" ", "+")
        link = "https://www.google.com/search?q=" + search_terms  
        draw.text((380, 328), reaction.message.content[:60], fill='rgb(0, 0, 0)', font=font)
        buff = io.BytesIO()
        img.save(buff, format ='PNG')
        byteImage = buff.getvalue()
        # save the edited image
        image = io.BytesIO(byteImage)
        await reaction.message.channel.send("It seems you asked a question better suited for google.")
        await reaction.message.channel.send(link, file=discord.File(image, f'{reaction.message.content}.png')) 



client.loop.create_task(deadline())
client.run(credentials['ids']['discord']['server_id'])
