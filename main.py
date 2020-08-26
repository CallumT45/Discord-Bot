import asyncio
import csv
import datetime
import io
import json
import random
import os

import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from cogs.extraClasses.AssignmentDB import AssignmentDatabase

client = commands.Bot(command_prefix='!', case_insensitive=True)

with open('files/credentials.txt', 'r') as credfile:
    credentials = json.load(credfile)


async def deadline():
    """Function which runs every 24 hours, checks the db for any assignments due in the enxt 24 hours, if so then sends them to the respecitive channel"""
    await client.wait_until_ready()
    while not client.is_closed():
        try:
            adb = AssignmentDatabase()
            due = adb.check_due()
            for row in due:
                text2 = f'{row[1]} | due on {row[0].strftime("%A")}, {row[0].strftime("%d/%m/%Y")}\n\n'
                embedDue = discord.Embed(
                    title="Alert Assignment Due Tomorrow", description=text2, color=0x00ff00)

                send_address = client.get_user(row[2])
                if not send_address:
                    send_address = client.get_channel(row[3])
                await send_address.send(embed=embedDue)

            # everyday check to see if any assignments are due in 1 day
            await asyncio.sleep(86400)
        except Exception as e:
            print(e)
            await asyncio.sleep(20000)


def check_if_it_is_me(ctx):
    return ctx.message.author.id == 307625115963621377


@client.event
async def on_ready():
    print('Bot is alive')


@client.command()
@commands.check(check_if_it_is_me)
async def kill(ctx):
    await client.logout()


@client.command()
async def tutorial(ctx):

    def react_check(msg):
        def check(reaction, reacting_user):
            return reacting_user != client.user and str(reaction.emoji) == '\u23E9' and reaction.message.id == msg.id
        return check

    buttons = "Lots of commands are run by interacting with 'buttons' like the ones below this message. Wait until all buttons are added to a message before clicking\nWhen ready click on next button"
    commands = "Commands are called by first typing ! followed by the command.\nA full list of commands can be found by typing !help\nSome commands require extra arguments, don't forget to enclose any text in quotes"
    games = "Some games require sending you a private message, be sure you check your DMs"
    stages = [commands, games]
    titles = ["Commands", "Games"]

    embed_rules = discord.Embed(title="Tutorial", color=0x00ff00)
    embed_rules.add_field(name='Buttons', value=buttons, inline=False)

    tutEmbed = await ctx.send(embed=embed_rules)
    await tutEmbed.add_reaction(emoji='\u23E9')
    for i in range(2):
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=react_check(tutEmbed))
            embed_tut = discord.Embed(title="Tutorial", color=0x00ff00)
            embed_tut.add_field(
                name=titles[i], value=stages[i], inline=False)
            await tutEmbed.clear_reaction(emoji='\u23E9')
            await tutEmbed.add_reaction(emoji='\u23E9')
            await tutEmbed.edit(embed=embed_tut)
        except Exception as e:
            break


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
        draw.text(
            (380, 328), reaction.message.content[:60], fill='rgb(0, 0, 0)', font=font)
        buff = io.BytesIO()
        img.save(buff, format='PNG')
        byteImage = buff.getvalue()
        # save the edited image
        image = io.BytesIO(byteImage)
        await reaction.message.channel.send("It seems you asked a question better suited for google.")
        await reaction.message.channel.send(link, file=discord.File(image, f'{reaction.message.content}.png'))


client.loop.create_task(deadline())
client.run(credentials['ids']['discord']['server_id'])
