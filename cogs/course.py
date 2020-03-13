import discord
from discord.ext import commands
import random, asyncio, datetime, csv, json

from PIL import Image, ImageDraw, ImageFont

with open('files/credentials.txt', 'r') as credfile:
    credentials = json.load(credfile)


class Course(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def problem(self, ctx):
        """
            Gives a random problem from the popular coding website leetcode.com
        """
        with open('files/problems.json', 'r') as credfile:
            problems = json.load(credfile)

            num = random.randint(0, 1021)

            embed_problem = discord.Embed(title=problems[str(num)]['title'].upper(), color=0x00ff00)

            embed_problem.add_field(name = 'Problem', value=problems[str(num)]['problem'], inline=False)
            embed_problem.add_field(name = "Examples", value=problems[str(num)]['example'], inline=False)
            embed_problem.add_field(name = "Link", value="https://leetcode.com/problems/" + problems[str(num)]['title'], inline=False)
            await ctx.send(embed=embed_problem)  

    @commands.command()
    async def due(self, ctx):
        """Prints the contents of the assignments csv in a discord embedded message"""
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
        
        with open(r'files\AssignmentList.csv','r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            text = ''
            for row in csv_reader:
                numDays = countdown(row[1])
                text += f'{row[2]} | due on {row[0]}, {row[1]} | {numDays} day/s\n\n'
        embedAss = discord.Embed(title="Upcoming Assignments", description=text, color=0x00ff00)
        await ctx.send(embed=embedAss)

    @commands.command()
    async def new(self, ctx):
        """Once called it this case waits 45 seconds for the assignment details, then 45 more for the due date. 
        For the due date it will only read in inputs which are in the right format"""
        await ctx.send('Please enter assignment details')

        def dateValidate(date_text):
            """Function ensures that unless input is in the right format, it will not be read in as a date""" 
            try:
                datetime.datetime.strptime(date_text, '%d/%m/%Y')
                return True
            except:
                return False

        def assignment_check(m):
            return m.author == ctx.author

        def assignment_date_check(m):
            return dateValidate(m.content) and m.author == ctx.author

        try:
            msg2 = await self.client.wait_for('message', timeout=45.0, check=assignment_check)
            assignment_details = msg2.content
        except:
            await ctx.send('Timed Out!')

        await ctx.send('Please enter assignment due date in dd/mm/yyyy')

        try:
            msg3 = await self.client.wait_for('message', timeout=45.0, check=assignment_date_check)
            assignment_due = msg3.content
            due_day = datetime.datetime.strptime(assignment_due, '%d/%m/%Y').strftime('%A')
        except Exception as e:
            await ctx.send(e)
            await ctx.send('Timed Out!')
        with open(r'files\AssignmentList.csv', 'a', newline='\n') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows([[f'{due_day}',f'{assignment_due}',f'{assignment_details}']])


    @commands.command()
    async def remove(self, ctx):
        """Removes a row in the assignment list, matches assignment details"""
        lines = []
        await ctx.send('Please enter assignment details')

        with open(r'files\AssignmentList.csv', 'r') as readFile:
            csv_reader = csv.reader(readFile, delimiter=',')
            
            for row in csv_reader:
                lines.append(row)        
        readFile.close()

        def detValidate(dets, lines):
            """Returns true if the assignment details exist in the csv file""" 
            for i in lines:
                if dets.lower() == i[2].lower():
                    return True
            else: return False

        def assignment_check_remove(m):
            return detValidate(m.content, lines) and m.author == ctx.author
        try:
            msg3 = await self.client.wait_for('message', timeout=60.0, check=assignment_check_remove)
            assignment_details_remove = msg3.content
        except:
            await ctx.send('Timed Out!')

        for i in lines:
            if assignment_details_remove.lower() == i[2].lower():
                lines.remove(i)
        
        
        with open(r'files\AssignmentList.csv', 'w', newline='\n') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(lines)
        writeFile.close()

    @commands.command()
    async def poll(self, ctx, *args):
        """
            Call this command followed by the question, then up to 9 options separated by spaces, use quotes where necessary
        """
        emojis = ['\u0031\u20E3','\u0032\u20E3','\u0033\u20E3','\u0034\u20E3','\u0035\u20E3','\u0036\u20E3','\u0037\u20E3','\u0038\u20E3','\u0039\u20E3']
        embed_poll = discord.Embed(title=args[0], color=0x00ff00)

        for i, value in enumerate(args[1:9]):    
            embed_poll.add_field(name=emojis[i], value=value, inline=True)
        poll_object = await ctx.send(embed=embed_poll)


        for i, answer in enumerate(args[1:9]):
            await poll_object.add_reaction(emoji=emojis[i])

def setup(client):
    client.add_cog(Course(client))