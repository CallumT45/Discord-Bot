import discord
from discord.ext import commands
import requests, html, bs4, re, datetime, io, random, json
import matplotlib.pyplot as plt
class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def covid(self, ctx):
        response = requests.get("https://thevirustracker.com/free-api?countryTotal=IE", headers={'Accept-Encoding': 'deflate','User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"})

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

        # cases = [2,6,13,18,19,21,24,34,43,70,90,129,169,223,292,366,557]


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
    async def covid2(self, ctx):
        """
        Scrapes Wikipedia for number of confirmed cases in Ireland, returns the data in list and graphical form. 
        If not working, wikipedia must have changed how the are displaying the data.
        """

        res = requests.get("https://en.wikipedia.org/wiki/2020_coronavirus_pandemic_in_the_Republic_of_Ireland")

        soup = bs4.BeautifulSoup(res.text, 'html.parser')

        data = soup.find_all('table')

        def cleanhtml(raw_html):
            cleanr = re.compile('<[^<]*?>')
            cleantext = re.sub(cleanr, '', raw_html)
            return cleantext

        def case_cleaning(case):
            x = case.split('(')
            num_cases = x[0]
            change = x[1].split(')')[0]
            return int(num_cases), change

        ire = cleanhtml(str(data[2]))
        ire = ire.strip()
        ire = ire.replace("   ", " ")
        divs = ire.split()

        divs2 = [x for x in divs if x != '\u200b']
        for i in range(len(divs2)-1,0,-1):
            if ('div' in divs2[i]) or ('parser' in divs2[i]) or ('columns' in divs2[i]):
                divs2.remove(divs2[i])

        for j in range(3):
            try:
                start_date = '2020-03-03'
                current_date = (datetime.datetime.today() - datetime.timedelta(days=j)).strftime('%Y-%m-%d')
                start_date_index = divs2.index(start_date)
                current_date_index = divs2.index(current_date)
                data_list = divs2[start_date_index:current_date_index+3]

                dates = [datetime.datetime.strptime(yep, "%Y-%m-%d").strftime('%d-%m') for i, yep in enumerate(data_list) if i % 3 ==0]
                cases = [case_cleaning(yep)[0] for i, yep in enumerate(data_list) if (i-1) % 3 ==0]
                change = [case_cleaning(yep)[1] for i, yep in enumerate(data_list) if (i-1) % 3 ==0]

                plt.style.use('dark_background')
                fig, ax = plt.subplots()

                plt.plot_date(dates, cases, color='#47a0ff', linestyle='-', ydate=False, xdate=True)
                ax.yaxis.grid()
                plt.xticks(rotation=45)
                plt.savefig('graph.png', transparent=True)

                cases = [str(i) for i in cases]

                dates_string = '\n'.join(dates)
                cases_string = '\n'.join(cases)
                change_string = '\n'.join(change)

                with open('graph.png', 'rb') as f:
                    file = io.BytesIO(f.read())
                
                image = discord.File(file, filename='graph.png')
                

                

                embed_stats = discord.Embed(title="Covid-19 Ireland", color=0x00ff00)
                
                embed_stats.add_field(name='Date', value=dates_string, inline=True)
                embed_stats.add_field(name='Cases', value=cases_string, inline=True)
                embed_stats.add_field(name='Change', value=change_string, inline=True)
                embed_stats.set_image(url=f'attachment://graph.png')
                await ctx.send(file=image, embed=embed_stats)
                break
            except Exception as e:
                print(e)
                continue



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