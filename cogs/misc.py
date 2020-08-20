import discord
from discord.ext import commands
import requests
import bs4
import datetime
import io
import random
import json
import urllib
import matplotlib.pyplot as plt
from Equation import Expression
import pandas as pd


class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def covid(self, ctx, country='Ireland', graph="total_cases"):
        """Return a sumary of recent covid cases in the supplied country

        Args:
            country (str, optional): [Wrap in quotes for multi word countries]. Defaults to 'Ireland'.
            graph (str, optional): [total_deaths, total_cases, new_cases]. Defaults to "total_cases".
        """

        df_all = pd.read_csv(
            "https://covid.ourworldindata.org/data/ecdc/full_data.csv")
        country = country.lower()
        df = df_all.loc[df_all['location'] == country.title()]

        df = df.loc[df['new_cases'] > 0]

        plt.style.use('dark_background')
        fig, ax = plt.subplots()

        plt.plot_date(df['date'], df[graph], color='#47a0ff',
                      linestyle='-', ydate=False, xdate=True)
        ax.yaxis.grid()
        plt.xticks(rotation=65)
        plt.title(graph)

        for i, label in enumerate(ax.xaxis.get_ticklabels()):
            if i % 5 != 0:
                label.set_visible(False)
            else:
                pass

        plt.savefig('graph.png', transparent=True)

        dates_string = '\n'.join(df['date'].tail(15))
        cases_string = '\n'.join(df['total_cases'].tail(15).astype(str))
        change_string = '\n'.join(df['new_cases'].tail(15).astype(str))

        with open('graph.png', 'rb') as f:
            file = io.BytesIO(f.read())

        image = discord.File(file, filename='graph.png')

        embed_stats = discord.Embed(
            title=f"Covid-19 {country.title()}", color=0x00ff00)

        embed_stats.add_field(name='Date', value=dates_string, inline=True)
        embed_stats.add_field(name='Total Cases',
                              value=cases_string, inline=True)
        embed_stats.add_field(
            name='New Cases', value=change_string, inline=True)
        embed_stats.set_image(url=f'attachment://graph.png')
        await ctx.send(file=image, embed=embed_stats)

    @commands.command()
    async def insult(self, ctx):
        """
        Chooses from two endpoints and returns the insult
        """
        urls = ["https://insult.mattbas.org/api/insult.txt",
                "https://amused.api.stdlib.com/insult@1.0.0/"]
        response = requests.get(random.choice(urls))
        await ctx.send(response.text)

    @commands.command()
    async def compliment(self, ctx):
        """
        Life got you down?
        """
        response = requests.get("https://complimentr.com/api")

        await ctx.send(json.loads(response.text)["compliment"])

    @commands.command()
    async def calc(self, ctx, *args):
        """
            Call this command followed by the equation with no spaces
        """
        try:
            xn = Expression(*args)
            await ctx.send(*args)  # + '=' + str(xn()))
            await ctx.send('= ' + str(xn()))
        except Exception as e:
            # print(e)
            await ctx.send("Invalid Computation")

    @commands.command()
    async def xkcd(self, ctx, num=random.randint(1, 2250)):
        """
            Call this command for a random comic or call the command followed by the comic number for a specific comic
        """
        response = requests.get(f"https://xkcd.com/{num}/")
        soup = bs4.BeautifulSoup(response.text, 'html.parser')
        data = soup.findAll("div", {"id": "middleContainer"})
        data = data[0].findAll("img")[0]
        url = str(data).split('src')[1].split('title')[0]
        imgURL = "HTTPS:"+url[2:-2]
        raw_data = urllib.request.urlopen(imgURL).read()
        im = io.BytesIO(raw_data)
        await ctx.send(file=discord.File(im, "xkcd_comic.png"))

    @commands.command()
    async def poll(self, ctx, *args):
        """
            Call this command followed by the question, then up to 9 options separated by spaces, use quotes where necessary
        """
        emojis = ['\u0031\u20E3', '\u0032\u20E3', '\u0033\u20E3', '\u0034\u20E3',
                  '\u0035\u20E3', '\u0036\u20E3', '\u0037\u20E3', '\u0038\u20E3', '\u0039\u20E3']
        embed_poll = discord.Embed(title=args[0], color=0x00ff00)

        for i, value in enumerate(args[1:9]):
            embed_poll.add_field(name=emojis[i], value=value, inline=True)
        poll_object = await ctx.send(embed=embed_poll)

        for i, answer in enumerate(args[1:9]):
            await poll_object.add_reaction(emoji=emojis[i])

    @commands.command()
    async def problem(self, ctx):
        """
            Gives a random problem from the popular coding website leetcode.com
        """
        with open('files/problems.json', 'r') as credfile:
            problems = json.load(credfile)

            num = random.randint(0, 1021)

            embed_problem = discord.Embed(
                title=problems[str(num)]['title'].upper(), color=0x00ff00)

            embed_problem.add_field(
                name='Problem', value=problems[str(num)]['problem'], inline=False)
            embed_problem.add_field(
                name="Examples", value=problems[str(num)]['example'], inline=False)
            embed_problem.add_field(
                name="Link", value="https://leetcode.com/problems/" + problems[str(num)]['title'], inline=False)
            await ctx.send(embed=embed_problem)


def setup(client):
    client.add_cog(Misc(client))
