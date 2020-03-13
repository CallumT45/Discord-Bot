import discord
from discord.ext import commands
import random, io, asyncio, json, requests, html, bs4, re, datetime
import matplotlib.pyplot as plt
class Misc(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def covid(self, ctx):

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
                continue


def setup(client):
    client.add_cog(Misc(client))