import discord
from discord.ext import commands
import requests, html, bs4, re, datetime, io, random, json
import matplotlib.pyplot as plt
class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def covid(self, ctx):
        response = requests.get("https://thevirustracker.com/free-api?countryTotal=IE")

        x = json.loads(response.text)

        total_cases = x["countrydata"][0]['total_cases']
        total_new_cases_today = x["countrydata"][0]['total_new_cases_today']
        total_deaths = x["countrydata"][0]['total_deaths']
        total_recovered = x["countrydata"][0]['total_recovered']

        # define an empty list
        cases = []

        # open file and read the content in a list
        with open('files/casefile.txt', 'r') as filehandle:
            for line in filehandle:
                # remove linebreak which is the last character of the string
                currentPlace = line[:-1]
                cases.append(int(currentPlace))

        # cases = [2,6,13,18,19,21,24,34,43,70,90,129,169,223]


        if cases[-1] != total_cases:
            cases.append(total_cases)
        change = [str(cases[i]-cases[i-1]) for i in range(1,len(cases))]
        change.insert(0, '1')


        def make_date(j):    
            date = '03/03/2020'

            d = datetime.datetime.strptime(date, '%d/%m/%Y')

            new_date = (d + datetime.timedelta(days=j)).strftime('%d/%m')
            return new_date
        dates = [make_date(j) for j in range(len(cases))]



        plt.style.use('dark_background')
        fig, ax = plt.subplots()

        plt.plot_date(dates, cases, color='#47a0ff', linestyle='-', ydate=False, xdate=True)
        ax.yaxis.grid()
        plt.axvline(9, label='Lockdown Announced')
        plt.xticks(rotation=45)
        if len(dates) > 20:
            for label in ax.xaxis.get_ticklabels()[::2]:
                label.set_visible(False)

        plt.savefig('graph.png', transparent=True)



        with open('files/casefile.txt', 'w') as filehandle:
            for listitem in cases:
                filehandle.write('{}\n'.format(listitem))



        cases = [str(i) for i in cases]
        

        dates_string = '\n'.join(dates[-15:])
        cases_string = '\n'.join(cases[-15:])
        change_string = '\n'.join(change[-15:])

        with open('graph.png', 'rb') as f:
            file = io.BytesIO(f.read())

        image = discord.File(file, filename='graph.png')


        embed_stats = discord.Embed(title="Covid-19 Ireland", color=0x00ff00)

        embed_stats.add_field(name='Total Cases', value=total_cases, inline=False)
        embed_stats.add_field(name='New Cases Today', value=total_new_cases_today, inline=False)
        embed_stats.add_field(name='Total Deaths', value=total_deaths, inline=False)
        embed_stats.add_field(name='Total Recovered', value=total_recovered, inline=False)


        embed_stats.add_field(name='Date', value=dates_string, inline=True)
        embed_stats.add_field(name='Cases', value=cases_string, inline=True)
        embed_stats.add_field(name='Change', value=change_string, inline=True)
        embed_stats.set_image(url=f'attachment://graph.png')
        await ctx.send(file=image, embed=embed_stats)



    @commands.command()
    async def insult(self, ctx):
        """
        Chooses from two endpoints and returns the insult
        """
        urls = ["https://insult.mattbas.org/api/insult.txt","https://amused.api.stdlib.com/insult@1.0.0/"]
        response = requests.get(random.choice(urls))
        await ctx.send(response.text)

    @commands.command()
    async def compliment(self, ctx):
        """
        Life got you down?
        """
        response = requests.get("https://complimentr.com/api")
        
        await ctx.send(json.loads(response.text)["compliment"])



def setup(client):
    client.add_cog(Misc(client))