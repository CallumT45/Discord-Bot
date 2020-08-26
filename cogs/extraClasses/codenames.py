import discord
import random
import asyncio


class Codenames():

    def __init__(self, ctx, client, users):

        self.ctx = ctx
        self.client = client
        self.users = users
        self.blue = random.sample(self.users, k=len(self.users)//2)
        self.red = list(set(self.users) - set(self.blue))

        self.words = []
        with open('files/words.txt', 'r') as wordfile:
            for row in wordfile:
                self.words.append(row[:-1])

        self.blue_cards = 9
        self.red_cards = 8
        self.game_words = random.sample(self.words, 25)
        self.blue_words = random.sample(self.game_words, self.blue_cards)
        self.red_words = random.sample(
            list(set(self.game_words) - set(self.blue_words)), self.red_cards)
        self.black_card = random.sample(
            list(set(self.game_words) - set(self.blue_words) - set(self.red_words)), 1)
        self.neutral_words = list(set(
            self.game_words) - set(self.blue_words) - set(self.red_words) - set(self.black_card))
        self.guessed_words = []
        self.flag = True
        self.spymaster_updates = 0

        self.blue_spymaster = random.choice(self.blue)
        self.red_spymaster = random.choice(self.red)

        self.blue_spymaster = self.client.get_user(int(self.blue_spymaster.id))
        self.red_spymaster = self.client.get_user(int(self.red_spymaster.id))

    async def spymaster(self):

        embed_code = discord.Embed(
            title=f"Codename\n\nBlue Words: {self.blue_cards}\nRed Words: {self.red_cards}", color=0x00ff00)

        for w in self.game_words:
            str_w = f'```{w}```'
            if w in self.guessed_words:
                str_w = str(f"""```css\n{w}```""")
            idenifier = '.'
            if w in self.blue_words:
                idenifier = 'Blue'
            elif w in self.red_words:
                idenifier = 'Red'
            elif w in self.neutral_words:
                idenifier = 'Neutral'
            elif w in self.black_card:
                idenifier = 'Game Over'
            embed_code.add_field(name=idenifier, value=str_w, inline=True)

        if self.spymaster_updates == 0:
            self.blue_spymaster_msg = await self.blue_spymaster.send(embed=embed_code)
            self.red_spymaster_msg = await self.red_spymaster.send(embed=embed_code)

        else:
            await self.blue_spymaster_msg.edit(embed=embed_code)
            await self.red_spymaster_msg.edit(embed=embed_code)
        self.spymaster_updates += 1

    async def game_loop(self, team):
        def word_check(m):
            return (m.content.upper() in self.game_words) or m.content.upper() == "END_TURN" or m.content.upper() == "STOP"

        if team == "Blue":
            team_num = self.blue_cards
            colour = 0x0000fe
        else:
            team_num = self.red_cards
            colour = 0xff0000

        while team_num > 0:
            embed_code = discord.Embed(
                title=f"Codename\n\nBlue Words: {self.blue_cards}\nRed Words: {self.red_cards}", color=colour)

            for w in self.game_words:
                str_w = f'```{w}```'
                idenifier = '.'
                if w in self.guessed_words:
                    str_w = str(f"""```css\n{w}```""")

                if w in self.guessed_words and w in self.blue_words:
                    idenifier = 'Blue'
                elif w in self.guessed_words and w in self.red_words:
                    idenifier = 'Red'
                elif w in self.guessed_words and w in self.neutral_words:
                    idenifier = 'Neutral'
                elif w in self.guessed_words and w in self.black_card:
                    idenifier = 'Game Over'
                embed_code.add_field(name=idenifier, value=str_w, inline=True)

            if not self.guessed_words:
                self.game_board = await self.ctx.send(embed=embed_code)
            else:
                await self.game_board.edit(embed=embed_code)

            try:
                guess = await self.client.wait_for('message', timeout=120.0, check=word_check)
                guess.content = guess.content.upper()
                if guess.content == "END_TURN":
                    break
                self.guessed_words.append(guess.content)
                if guess.content in self.black_card or guess.content == 'STOP':
                    self.flag = False
                    break
                if guess.content in self.blue_words:
                    self.blue_cards -= 1
                elif guess.content in self.red_words:
                    self.red_cards -= 1

                if team == "Blue" and guess.content not in self.blue_words:
                    break
                elif team == "Red" and guess.content not in self.red_words:
                    break

            except:
                await self.ctx.send("Out of Time, your turn is over!")
                break

    async def main(self):
        blue_names = [member.name for member in self.blue]
        red_names = [member.name for member in self.red]

        await self.ctx.send(f'Blue Team is {", ".join(blue_names)}')
        await self.ctx.send(f'Red Team is {", ".join(red_names)}')
        await self.ctx.send("Spymasters check your DMs")

        while self.blue_cards > 0 and self.red_cards > 0 and self.flag:
            await self.spymaster()
            await self.game_loop('Blue')
            if self.flag:
                await self.game_loop('Red')

        await self.ctx.send("Game Over")
