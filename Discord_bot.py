import discord, praw, random, io, asyncio, datetime, urllib, csv, json

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

class game():

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
                move = await client.wait_for('message', timeout=30.0, check=move_check)

            except:
                await self.channel.send('👎')
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
    channel = message.channel
    author = message.author
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
        post_to_pick = random.randint(0, 10)
        for count, submission in enumerate(reddit.subreddit(subreddit).top("day")):
            if count == post_to_pick:
                if not submission.stickied and not submission.is_video and submission.is_reddit_media_domain:
                    raw_post = str(submission.title) + " \u2191 " + str(submission.score) + "  r/" + str(subreddit)
                    imgURL = submission.url
                    raw_data = urllib.request.urlopen(imgURL).read()
                    im = io.BytesIO(raw_data)
                    await channel.send(raw_post)
                    await channel.send(file=discord.File(im, "img.png"))
                    break
                else:
                    post_to_pick += 1

            
                    
    elif message.content == '$kill' : await client.logout()

    elif message.content == '$help': 
        output = """
        The functions currently available are; \n
        • $due for a list of outstanding assignments, \n
        • $meme for a random meme from r/programmerhumor, \n
        • $new for adding new assignments. Follow the given instructions, \n
        • $remove for removing assingments, \n
        • $tictactoe for a round of the classic game versus the computer \n
        • React with ❓ for sarcastic google response
        """
        await channel.send(output)



    elif message.content == '$tictactoe': 
        await channel.send('Do you want to be X or O?')

        def check(m):
            return (m.content.upper() == 'X' or m.content.upper() == 'O') and m.channel == channel
        try:
            msg = await client.wait_for('message', timeout=30.0, check=check)
            letter = msg.content.upper()
            tttGame = game(letter,channel)
            await tttGame.drawBoard()
            await tttGame.mainGame()
        except:
            await channel.send('👎')

    elif message.content == "$new":
        """Once called it this case waits 30 seconds for the assignment details, then 30 more for the due date. 
        For the due date it will only read in inputs which are in the right format"""
        await channel.send('Please enter assignment details')
        def assignment_check(m):
            return m.author == author

        def assignment_date_check(m):
            return dateValidate(m.content) and m.author == author

        try:
            msg2 = await client.wait_for('message', timeout=30.0, check=assignment_check)
            assignment_details = msg2.content
        except:
            await channel.send('👎')

        await channel.send('Please enter assignment due date in dd/mm/yyyy')

        try:
            msg3 = await client.wait_for('message', timeout=30.0, check=assignment_date_check)
            assignment_due = msg3.content
            due_day = datetime.datetime.strptime(assignment_due, '%d/%m/%Y').strftime('%A')
        except:
            await channel.send('👎')
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
            await channel.send('👎')

        for i in lines:
            if assignment_details_remove.lower() == i[2].lower():
                lines.remove(i)
        
        
        with open(r'files\AssignmentList.csv', 'w', newline='\n') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(lines)
        writeFile.close()

@client.event
async def on_reaction_add(reaction, user):
    """If reaction matches and there is text in the message then draw the text on the image, return the image"""
    if reaction.emoji == '❓' and reaction.message.content:
        img = Image.open(r'files\Google_web_search.png')
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype(r"files\OpenSans-Regular.ttf", 18)
        # draw the message on the background
            
        draw.text((380, 328), reaction.message.content, fill='rgb(0, 0, 0)', font=font)
        buff = io.BytesIO()
        img.save(buff, format ='PNG')
        byteImage = buff.getvalue()
        # save the edited image
        image = io.BytesIO(byteImage)
        await reaction.message.channel.send("It seems you asked a question better suited for google.")
        await reaction.message.channel.send(file=discord.File(image, f'{reaction.message.content}.png')) 



client.loop.create_task(deadline())
client.run(credentials['ids']['discord']['server_id'])
