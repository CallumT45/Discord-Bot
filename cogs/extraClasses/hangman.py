import discord
from discord.ext import commands
import requests
import html
import random
import json
import asyncio


class Hangman():
    def __init__(self, ctx, client, congrats):
        self.words = """grape catapult dog baboon elephant giraffe apple coconut monkey rubik mice mouse pineapple android apple house fence python grail zebra protein terrain llama fire policeman zebra lion fluffy
        America Balloon Biscuit Blanket Chicken Chimney Country Cupcake Curtain Diamond Eyebrow Fireman Florida Germany Harpoon Husband Morning Octopus Popcorn Printer Sandbox Skyline Spinach
        Backpack Basement Building Campfire Complete Elephant Exercise Hospital Internet Jalapeno Mosquito Sandwich Scissors Seahorse Skeleton Snowball Sunshade Treasure
        Blueberry Breakfast Bubblegum Cellphone Dandelion Hairbrush Hamburger Horsewhip Jellyfish Landscape Nightmare Pensioner Rectangle Snowboard Spaceship Spongebob Swordfish Telephone Telescope
        Bellpepper Broomstick Commercial Flashlight Lighthouse Lightsaber Microphone Photograph Skyscraper Strawberry Sunglasses Toothbrush Toothpaste
        """.lower().split()
        self.ctx = ctx
        self.client = client
        self.lives = 5
        self.word_to_guess = random.choice(self.words)
        self.split_wtg = [char for char in self.word_to_guess]
        # prints a list the length of the hidden word
        self.cg = ["_"]*len(self.split_wtg)
        self.letters_left = "a b c d e f g h i j k l m n o p q r s t u v w x y z".split()
        self.congrats = congrats
        self.rounds = 0

    def game(self, guess):
        """iterates through the split word and if the letter guess is at that element then place that letter in the 
        current guess list, if not then increment count. After the for loop concludes if no matches were found
        then decrement number of lives"""
        count = 0
        for i in range(len(self.split_wtg)):
            if guess == self.split_wtg[i]:
                self.cg[i] = guess
            else:
                count += 1
        if count == len(self.split_wtg):
            self.lives -= 1

    def string_format(self, letters_list):
        text = ''
        for i in letters_list:
            text += i + ' | '
        return text

    def string_format2(self, cg):
        text = "```{}```".format(" ".join(cg))
        return text

    async def maingame(self):
        def letter_check(m):
            return (m.content in self.letters_left or m.content.lower() == "stop") and m.guild == self.ctx.guild
        await self.ctx.send(f"Word has {len(self.cg)} letters")
        while self.cg != self.split_wtg:  # While guessed word is not equal to the hidden word
            try:
                # await self.ctx.send("Choose your letter")

                try:
                    guess = await self.client.wait_for('message', timeout=45.0, check=letter_check)

                except Exception as e:
                    await self.ctx.send(e)
                    await self.ctx.send("Timed Out!")
                    break

                self.letters_left.remove(guess.content)
                self.game(guess.content)
                letters_string = self.string_format(self.letters_left)
                embed = discord.Embed(title="Hangman", color=0x00ff00)
                embed.add_field(name="Letters Left",
                                value=letters_string, inline=False)
                embed.add_field(name="Lives", value=self.lives, inline=False)
                embed.add_field(name="Current Guess",
                                value=self.string_format2(self.cg), inline=False)

                if self.rounds % 5 == 0:
                    self.hangman_msg = await self.ctx.send(embed=embed)
                else:
                    await self.hangman_msg.edit(embed=embed)

                if self.lives == 0:
                    await self.ctx.send(f"Word was {self.word_to_guess}")
                    break  # break the inside game loop, prompts the user to play again
                self.rounds += 1
            except Exception as e:
                # print(e)
                continue
        if self.cg == self.split_wtg:
            await self.ctx.send(random.choice(self.congrats))
        else:
            await self.ctx.send("Better Luck Next Time!")
