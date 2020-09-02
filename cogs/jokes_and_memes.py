import discord
from discord.ext import commands
import praw
import random
import io
import json
import requests

from urllib.request import Request, urlopen

with open('files/credentials.txt', 'r') as credfile:
    credentials = json.load(credfile)


reddit = praw.Reddit(client_id=credentials['ids']['reddit']['client_id'],
                     client_secret=credentials['ids']['reddit']['client_secret'],
                     username=credentials['ids']['reddit']['username'],
                     password=credentials['ids']['reddit']['password'],
                     user_agent=credentials['ids']['reddit']['user_agent'])
reddit.read_only = True


class Jokes_and_Memes(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def meme(self, ctx):
        """Grabs one of the hot posts from r/programmerhumor and displays it in the chat"""
        subreddit = 'ProgrammerHumor'
        post_to_pick = random.randint(0, 15)
        for count, submission in enumerate(reddit.subreddit(subreddit).top(random.choice(["week", "month"]))):
            if count == post_to_pick:
                if not submission.stickied and not submission.is_video and submission.is_reddit_media_domain:
                    try:
                        raw_post = str(submission.title) + " \u2191 " + \
                            str(submission.score) + "  r/" + str(subreddit)
                        imgURL = submission.url
                        raw_data = urlopen(imgURL).read()
                        im = io.BytesIO(raw_data)
                        await ctx.send(raw_post, file=discord.File(im, "funny_meme.png"))

                    except:
                        post_to_pick += 1
                        continue
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
                    try:
                        raw_post = str(submission.title) + " \u2191 " + \
                            str(submission.score) + "  r/" + str(subreddit)
                        imgURL = submission.url
                        raw_data = urlopen(imgURL).read()
                        im = io.BytesIO(raw_data)
                        await ctx.send(raw_post, file=discord.File(im, "funny_meme.gif"))

                    except Exception as e:
                        # print(e)
                        post_to_pick += 1
                        continue
                    break
                else:
                    post_to_pick += 1

    @commands.command()
    async def eyebleach(self, ctx):
        """Grabs one of the hot posts from r/eyebleach and displays it in the chat"""
        subreddit = 'eyebleach'
        post_to_pick = random.randint(0, 15)
        for count, submission in enumerate(reddit.subreddit(subreddit).top(random.choice(["day", "week", "month"]))):
            if count == post_to_pick:
                if not submission.stickied and not submission.is_video and submission.is_reddit_media_domain:
                    try:
                        raw_post = str(submission.title) + " \u2191 " + \
                            str(submission.score) + "  r/" + str(subreddit)
                        imgURL = submission.url
                        raw_data = urlopen(imgURL).read()
                        im = io.BytesIO(raw_data)
                        await ctx.send(raw_post, file=discord.File(im, "aww.gif"))

                    except:
                        post_to_pick += 1
                        continue
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
                    raw_post = str(submission.title) + \
                        " \u2191 " + str(submission.score)
                    await ctx.send(raw_post)
                    break
                else:
                    post_to_pick += 1

    @commands.command()
    async def joke(self, ctx):
        """
        Probably a funny joke
        """

        urls = ['https://official-joke-api.appspot.com/random_joke',
                'https://official-joke-api.appspot.com/jokes/programming/random']
        choice = random.choice([0, 1])
        response = requests.get(urls[choice])
        json_data = json.loads(response.text)

        if choice == 0:
            await ctx.send(json_data['setup'])
            await ctx.send(json_data['punchline'])
        else:
            await ctx.send(json_data[0]['setup'])
            await ctx.send(json_data[0]['punchline'])

    @commands.command()
    async def distracted(self, ctx, text0, text1):
        """Generate a Distracted Boyfriend meme

        Args:
            text0 ([String]): [Text on woman, enclose in quotes]
            text1 ([String]): [Text on boyfriend, enclose in quotes]
        """
        URL = 'https://api.imgflip.com/caption_image'
        params = {
            'username': credentials['ids']['reddit']['username'],
            'password': credentials['ids']['reddit']['password'],
            'template_id': '112126428',
            'text0': text0,
            'text1': text1
        }
        response = requests.request('POST', URL, params=params).json()
        imgURL = response['data']['url']
        response = requests.get(imgURL)
        im = io.BytesIO(response.content)
        await ctx.send(file=discord.File(im, "meme.png"))

    @commands.command()
    async def hotline(self, ctx, text0, text1):
        """Generate a Hotline bling meme, Call command followed by text in quotes, then a space and the second text in quotes

        Args:
            text0 ([String]): [Top text, enclose in quotes]
            text1 ([String]): [Bottom text, enclose in quotes]
        """
        URL = 'https://api.imgflip.com/caption_image'
        params = {
            'username': credentials['ids']['reddit']['username'],
            'password': credentials['ids']['reddit']['password'],
            'template_id': '181913649',
            'text0': text0,
            'text1': text1
        }
        response = requests.request('POST', URL, params=params).json()
        imgURL = response['data']['url']
        response = requests.get(imgURL)
        im = io.BytesIO(response.content)
        await ctx.send(file=discord.File(im, "meme.png"))

    @commands.command()
    async def cmm(self, ctx, text0):
        """Generate a Change my Mind meme

        Args:
            text0 ([String]): [Text on sign, enclose in quotes]
        """
        URL = 'https://api.imgflip.com/caption_image'
        params = {
            'username': credentials['ids']['reddit']['username'],
            'password': credentials['ids']['reddit']['password'],
            'template_id': '129242436',
            'text0': text0
        }
        response = requests.request('POST', URL, params=params).json()
        imgURL = response['data']['url']
        response = requests.get(imgURL)
        im = io.BytesIO(response.content)
        await ctx.send(file=discord.File(im, "meme.png"))


def setup(client):
    client.add_cog(Jokes_and_Memes(client))
