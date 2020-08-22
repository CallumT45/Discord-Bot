import discord
from discord.ext import commands
import asyncio

from datetime import datetime, date
from cogs.extraClasses.AssignmentDB import AssignmentDatabase


class Assignment(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def new(self, ctx, date, assignment_details):
        def dateValidate(date_text):
            """Function ensures that unless input is in the right format, it will not be read in as a date"""
            try:
                datetime.strptime(date_text, '%d/%m/%Y')
                return True
            except:
                return False
        print(ctx.channel.id)
        try:
            ID = ctx.guild.id
        except:
            ID = ctx.author.id

        if dateValidate(date):
            adb = AssignmentDatabase()
            status = adb.new(date, assignment_details, ID, ctx.channel.id)
            if status == "OK":
                await ctx.send("Assignment Added")
            else:
                await ctx.send("Error: Assignment already in DB")
        else:
            await ctx.send("Please enter assignment due date in dd/mm/yyyy")

    @commands.command()
    async def due(self, ctx):
        """Prints the contents of the assignments csv in a discord embedded message"""
        def countdown(duedate):
            """Given a date, calculates the number of days from today until then"""
            try:
                today = date.today()
                delta = duedate - today
                return delta.days
            except:
                return None

        try:
            ID = ctx.guild.id
        except:
            ID = ctx.author.id
        adb = AssignmentDatabase()
        rows = adb.due(ID)
        text = ''
        for row in rows:
            numDays = countdown(row[0])
            text += f'{row[1]} | due on {row[0].strftime("%A")}, {row[0].strftime("%d/%m/%Y")} | {numDays} day/s\n\n'
        embedAss = discord.Embed(
            title="Upcoming Assignments", description=text, color=0x00ff00)
        if rows:
            await ctx.send(embed=embedAss)
        else:
            await ctx.send("No upcoming assignments")

    @commands.command()
    async def remove(self, ctx, assignment_details):
        """Removes a row in the assignment list, matches assignment details"""
        try:
            ID = ctx.guild.id
        except:
            ID = ctx.author.id

        adb = AssignmentDatabase()
        adb.remove(assignment_details, ID)
        await ctx.send("Assignment Removed")


def setup(client):
    client.add_cog(Assignment(client))
