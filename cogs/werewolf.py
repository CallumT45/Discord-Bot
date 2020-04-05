import discord
from discord.ext import commands
import random, asyncio

class werewolf():
    def __init__(self, ctx, client):
        self.users = ["Callum", "Beak", "Alex", "Sean", "Graham", "David", "Dan", "Ben", "Filipe", "Frank", "Shane"]
        self.set_roles()
        self.ctx = ctx
        self.client = client
        # self.show_werewolfs()#Method to provately send list of werewolves to the other werewolves at the start of the game


    def set_roles(self):
        self.num_wolves = 2
        self.num_villagers_with_roles = 3
        num = len(self.users)
        if num > 9:
            self.num_wolves = 3
            self.num_villagers_with_roles = 4

        self.werewolves = random.sample(self.users, self.num_wolves)
        self.role_dict = { i : "Werewolf" for i in self.werewolves}
        self.villagers = list(set(self.users)-set(self.werewolves))

        self.villagers_with_roles = random.sample(self.villagers, self.num_villagers_with_roles)
        self.villagers_without_roles = list(set(self.villagers)-set(self.villagers_with_roles))

        self.doc = self.villagers_with_roles[0]
        self.role_dict[self.villagers_with_roles[0]] = "Doctor"

        self.seer = self.villagers_with_roles[1]
        self.role_dict[self.villagers_with_roles[1]] = "Seer"

        self.cupid = self.villagers_with_roles[2]
        self.role_dict[self.villagers_with_roles[2]] = "Cupid"


        if num > 9:
            self.hunter = self.villagers_with_roles[3]
            self.role_dict[self.villagers_with_roles[3]] = "Hunter"

        for villager in self.villagers_without_roles:
            self.role_dict[villager] = "Villager"

    async def night(self):
        self.cycle = "night"
        await self.draw_users()
        werewolf_choice = int(input("Werewolves choose who you will kill: "))
        doc_choice = int(input("Doctor choose who you will save: "))
        seer_choice = int(input("Seer choose who you will look at: "))

        await self.ctx.send(str(self.users[seer_choice]) + " is " + str(self.role_dict[self.users[seer_choice]]))


        if werewolf_choice != doc_choice:
            await self.ctx.send(f"{self.users[werewolf_choice]} was brutally mauled to death last night")
            await self.remove_user(werewolf_choice)
        else:
            await self.ctx.send(f"{self.users[werewolf_choice]} was attacked last night, but the doctor managed to save them")

    async def day(self):
        self.cycle = "day"
        await self.draw_users()
        #need to plan for tie
        lynch_choice = int(input("You have 5 minutes to decide who to lynch!\n"))
        #do the wait thing for 5 mins
        await self.ctx.send(f"{self.users[lynch_choice]} was put to death")
        await self.remove_user(lynch_choice)

    async def remove_user(self, index):
        if self.role_dict[self.users[index]] == "Werewolf":
            self.num_wolves -= 1
        elif self.role_dict[self.users[index]] == "Hunter" and self.cycle == "day":
            hunter_choice = int(input("Hunter choose who you will kill: "))
            await self.ctx.send(f"Just before being put to death, the hunter killed {self.users[hunter_choice]}")
            await self.remove_user(hunter_choice)           
        if self.users[index] in self.cupid_choice:
            self.cupid_choice.remove(self.users[index])
            await self.ctx.send(f"Overcome with grief by the loss of {self.users[index]}, {self.cupid_choice[0]} killed themself!")
            self.users.pop(index)
            self.users.remove(self.cupid_choice[0])
        else:
            self.users.pop(index)  

    async def cupid_turn(self):
        def cupid_check(m):
            try:
                m.content = m.content.split(',')
                temp = [self.users[int(i)] for i in m.content]
                return True and (m.guild == self.ctx.guild) and (len(temp)==2)
            except: 
                return False 
            
        await self.ctx.send("Cupid is choosing")
        # cupid_id = self.client.get_user(int(self.cupid.id))
        embed_users = await self.draw_users()
        await self.ctx.send(embed=embed_users)

        await self.ctx.send("Cupid choose who is to fall in love")

        try:
            cupid_choice = await self.client.wait_for('message', timeout=45.0, check=cupid_check)
            print(cupid_choice.content)
            self.cupid_choice = [self.users[int(i)] for i in cupid_choice.content]
        except Exception as e:
            print(e)
            await self.ctx.send("Timed Out!")

    async def doc_turn(self):
        def doc_check(m):
            return (m.content in range(len(self.users)))
            
        await self.ctx.send("Doctor is choosing")
        # cupid_id = self.client.get_user(int(self.cupid.id))
        embed_users = await self.draw_users()
        await self.ctx.send(embed=embed_users)

        await self.ctx.send("Doctor choose who to save")

        try:
            doc_choice = await self.client.wait_for('message', timeout=45.0, check=doc_check)
            print(doc_choice.content)
            return doc_choice.content
        except Exception as e:
            print(e)
            await self.ctx.send("Timed Out!")

    async def main(self):
        await self.cupid_turn()
        while self.num_wolves > 0 and (2 * self.num_wolves != len(self.users)):
            print(self.users) 
            await self.night()
            await self.day()
        if self.num_wolves == 0:
            await self.ctx.send("All werewolves eliminated, congrats villagers!")
        else:
            await self.ctx.send("The werewolves have taken over.")

    async def draw_users(self):
        embed_users = discord.Embed(title=f"User List", color=0x00ff00)
        for i, user in enumerate(self.users):
            embed_users.add_field(name=i, value=user, inline=True)
        return embed_users
        # self.game_board = await self.ctx.send(embed=embed_users)
        





class Werewolf(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()    
    async def werewolf(self, ctx):
        ww = werewolf(ctx, self.client)#, users)
        print(ww.role_dict)
        await ww.main()

def setup(client):
    client.add_cog(Werewolf(client))