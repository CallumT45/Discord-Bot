import asyncio
import csv
import datetime
import io
import json
import os
import random
import re

import bs4
import discord
import matplotlib.pyplot as plt
import requests
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

client = commands.Bot(command_prefix = '$')

with open('files/credentials.txt', 'r') as credfile:
    credentials = json.load(credfile)

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

async def deadline():
    """Function which runs every 24 hours, calls the countdown function, if the assignment is due in one day then
    alert is sent into general channel. Opens the assingment file, stores all the lines, clears the file, alerts the discord if assignment is due
    in 1 day, rewrites assignments which are not past due"""
    await client.wait_until_ready()
    channel = client.get_channel(credentials['ids']['discord']['main_channel_id'])#change this to whatever id you need
    while not client.is_closed():
        lines = []
        try:
            with open('files/AssignmentList.csv', 'r') as readFile:
                csv_reader = csv.reader(readFile, delimiter=',')
                
                for row in csv_reader:
                    lines.append(row)
                    numDays = countdown(row[1])
                    if numDays == 1:
                        text2 = f'{row[2]} | due on {row[0]}, {row[1]}'
                        embedDue = discord.Embed(title="Alert Assignment Due Tomorrow", description=text2, color=0x00ff00)
                        await channel.send(embed=embedDue)

                    if numDays < 0:
                        lines.remove(row)
                    
            lines.sort(key=lambda x: datetime.datetime.strptime(x[1], "%d/%m/%Y"))#sorts the assignments by due date
            with open('files/AssignmentList.csv', 'w', newline='\n') as writeFile:
                writer = csv.writer(writeFile)
                writer.writerows(lines)


            await asyncio.sleep(86400)#everyday check to see if any assignments are due in 1 day
        except Exception as e:
            print(e)
            await asyncio.sleep(20000)

async def problem():
    await client.wait_until_ready()
    channel = client.get_channel(credentials['ids']['discord']['main_channel_id'])#change this to whatever id you need
    while not client.is_closed():
        try:
            with open('files/problems.json', 'r') as credfile:
                problems = json.load(credfile)

                num = random.randint(0, 1021)

                embed_problem = discord.Embed(title="Daily Problem " +problems[str(num)]['title'].upper(), color=0x00ff00)

                embed_problem.add_field(name = 'Problem', value=problems[str(num)]['problem'], inline=False)
                embed_problem.add_field(name = "Examples", value=problems[str(num)]['example'], inline=False)
                embed_problem.add_field(name = "Link", value="https://leetcode.com/problems/" + problems[str(num)]['title'], inline=False)
                await channel.send(embed=embed_problem)      
                await asyncio.sleep(86400)
        except Exception as e:
            print(e)
            await asyncio.sleep(30)

async def update_covid():
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            response = requests.get("https://thevirustracker.com/free-api?countryTotal=IE", headers={'Accept-Encoding': 'deflate','User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"})

            x = json.loads(response.text)

            total_cases = x["countrydata"][0]['total_cases']
            # define an empty list
            cases = []
            # open file and read the content in a list
            with open('files/casefile.txt', 'r') as filehandle:
                for line in filehandle:
                    # remove linebreak which is the last character of the string
                    currentPlace = line[:-1]
                    cases.append(int(currentPlace))
            if cases[-1] != total_cases:
                cases.append(total_cases)

            with open('files/casefile.txt', 'w') as filehandle:
                for listitem in cases:
                    filehandle.write('{}\n'.format(listitem))

            await asyncio.sleep(86400)
        except Exception as e:
            print(e)
            await asyncio.sleep(1500)


def check_if_it_is_me(ctx):
    return ctx.message.author.id == 307625115963621377 or ctx.message.author.id == 618791421432037386
 
@client.event
async def on_ready():
    print('Bot is ready')

@client.command()
@commands.check(check_if_it_is_me)
async def kill(ctx):
    await client.logout()

# @client.command()
# @commands.check(check_if_it_is_me)
# async def load(ctx, extension):
#     client.load_extension(f'cogs.{extension}')        


# @client.command()
# @commands.check(check_if_it_is_me)
# async def unload(ctx, extension):
#     client.unload_extension(f'cogs.{extension}')


for filename in os.listdir("./cogs"):
    if filename.endswith('.py'):
        client.load_extension(f'cogs.{filename[:-3]}')


@client.event
async def on_reaction_add(reaction, user):
    """If reaction matches and there is text in the message then draw the text on the image, return the image and search link"""
    if reaction.emoji == "\u2753" and reaction.message.content:
        img = Image.open('files/Google_web_search.png')
        draw = ImageDraw.Draw(img)

        font = ImageFont.truetype("files/OpenSans-Regular.ttf", 18)
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
client.loop.create_task(problem())
client.loop.create_task(update_covid())
client.run(credentials['ids']['discord']['server_id'])
