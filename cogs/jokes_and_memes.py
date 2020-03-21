import discord
from discord.ext import commands
import praw, random, io, asyncio, urllib, json, requests, html

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

class Jokes_and_Memems(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def meme(self, ctx):
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
                    await ctx.send(raw_post, file=discord.File(im, "funny_meme.png"))
                    break
                else:
                    post_to_pick += 1

    @commands.command()
    async def dankmeme(self, ctx):
        """Grabs one of the hot posts from r/dankmemes and displays it in the chat"""
        subreddit = 'dankmemes'
        post_to_pick = random.randint(0, 15)
        for count, submission in enumerate(reddit.subreddit(subreddit).top(random.choice(["day", "week", "month"]))):
            if count == post_to_pick:
                if not submission.stickied and not submission.is_video and submission.is_reddit_media_domain:
                    raw_post = str(submission.title) + " \u2191 " + str(submission.score) + "  r/" + str(subreddit)
                    imgURL = submission.url
                    raw_data = urllib.request.urlopen(imgURL).read()
                    im = io.BytesIO(raw_data)
                    await ctx.send(raw_post, file=discord.File(im, "funny_meme.png"))
                    break
                else:
                    post_to_pick += 1

    @commands.command()
    async def showerthought(self, ctx):
        """Grabs one of the hot posts from r/showerthought and displays it in the chat"""
        subreddit = 'showerthoughts'
        post_to_pick = random.randint(0, 15)
        for count, submission in enumerate(reddit.subreddit(subreddit).top(random.choice(["week", "month"]))):
            if count == post_to_pick:
                if not submission.stickied and not submission.is_video:
                    raw_post = str(submission.title) + " \u2191 " + str(submission.score)
                    await ctx.send(raw_post)
                    break
                else:
                    post_to_pick += 1


    @commands.command()
    async def joke(self, ctx):
        urls = ['https://official-joke-api.appspot.com/random_joke', 'https://official-joke-api.appspot.com/jokes/programming/random']
        choice = random.choice([0,1])
        response = requests.get(urls[choice])
        json_data = json.loads(response.text)

        if choice == 0:
            await ctx.send(json_data['setup'])
            await ctx.send(json_data['punchline'])
        else:
            await ctx.send(json_data[0]['setup'])
            await ctx.send(json_data[0]['punchline'])


def setup(client):
    client.add_cog(Jokes_and_Memems(client))