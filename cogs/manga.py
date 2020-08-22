import discord
from discord.ext import commands
import html
import random
import asyncio
import io
import requests
from PIL import Image
from urllib.request import Request, urlopen
import bs4


def get_URL(manga, chapter, page):
    URL = "http://www.mangareader.net"
    url = URL + '/' + manga + '/' + chapter + '/' + page
    response = requests.get(url)
    soup = bs4.BeautifulSoup(response.text, 'html.parser')
    myimgs = soup.findAll("img")
    myimgs = [img for img in myimgs if img.has_attr(
        'alt') and "Page" in img['alt']]
    return 'https:' + myimgs[0]['src']


def get_img(imgURL):
    req = Request(imgURL, headers={'User-Agent': 'Mozilla/5.0'})
    webpage = urlopen(req).read()
    im = io.BytesIO(webpage)
    img = Image.open(im)
    try:
        rgb = Image.new('RGB', img.size, (255, 255, 255))
        rgb.paste(img, mask=img.split()[3])
        return rgb
    except:
        return img


class Manga(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def manga(self, ctx, manga, chapter):
        """
           Call this command with the name of the manga in quotes followed by the chapter number
        """
        try:
            page = 1
            URL2 = ""
            img_list = []
            part = ""
            await ctx.send("Collecting pages...This may take a minute")
            while True:
                URL = get_URL(manga.lower().replace(
                    " ", "-"), str(chapter), str(page))
                if URL == URL2:
                    break
                URL2 = URL
                img_list.append(get_img(URL))
                if page == 30:
                    img_list[0].save(f"manga.pdf",
                                     save_all=True, append_images=img_list[1:])
                    await ctx.send(file=discord.File("manga.pdf", f"{manga.title()}-Chapter-{str(chapter)}-Part-1.pdf"))
                    img_list = []
                    part = "-Part-2"
                page += 1

            if page != 30:
                img_list[0].save(f"manga.pdf",
                                 save_all=True, append_images=img_list[1:])
                await ctx.send(file=discord.File("manga.pdf", f"{manga.title()}-Chapter-{str(chapter)}+{part}.pdf"))
        except:
            await ctx.send("Error: Please ensure the manga name and chapter number are correct")


def setup(client):
    client.add_cog(Manga(client))
