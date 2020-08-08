import discord
from discord.ext import commands
import random, asyncio

class Player():
    def __init__(self, name, idn):
        self.name = name
        self.id = idn

class werewolf():
    def __init__(self, ctx, client, users):
        self.users = users#[Player("Callum", 307625115963621377),Player("Ben", 307625115963621377),Player("Eoin", 307625115963621377),Player("Jack", 307625115963621377),Player("Jill", 307625115963621377),Player("Claire", 307625115963621377),Player("Jeane", 307625115963621377)]
        self.set_roles()
        self.ctx = ctx
        self.client = client
        self.cupid_choice = []

    def set_roles(self):
        self.num_wolves = 2
        self.num_villagers_with_roles = 3
        num = len(self.users)
        if num > 9:
            self.num_wolves = 3
            self.num_villagers_with_roles = 4
        if num > 13:
            self.num_wolves = 5

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
        await self.ctx.send("Night Falls")
        self.cycle = "night"
        await self.draw_users()

        await self.ctx.send("Werewolves are choosing their next meal")
        werewolf_choice = await self.killer_turn()

        await self.ctx.send("Doctor is choosing")
        if self.doc in self.users:
            doc_choice = await self.doc_turn()
        else:
            await asyncio.sleep(random.randint(3,12))
            doc_choice = -1

        await self.ctx.send("Seer is choosing")
        if self.seer in self.users:
            await self.seer_turn()
        else:
            await asyncio.sleep(random.randint(3,12))

        await self.ctx.send("Day break!")
        if werewolf_choice != doc_choice:
            await self.ctx.send(f"{self.users[werewolf_choice].name} was brutally mauled to death last night")
            await self.remove_user(werewolf_choice)
        else:
            await self.ctx.send(f"{self.users[werewolf_choice].name} was attacked last night, but the doctor managed to save them")

    async def day(self):     
        def mob_check(m):
            return (m.content in list(map(lambda x: str(x), range(len(self.users))))) and m.guild == self.ctx.guild

        self.cycle = "day"
        embed_users = await self.draw_users()
        await self.ctx.send(embed=embed_users)

        await self.ctx.send("You have 5 minutes to decide who to lynch!")
        while True:
            try:
                lynch_choice = await self.client.wait_for('message', timeout=300.0, check=mob_check)
                lynch_choice =  int(lynch_choice.content) - 1
                await self.ctx.send(f"{self.users[lynch_choice].name} was put to death")
                await self.remove_user(lynch_choice)
                break

            except Exception as e:
                await self.ctx.send("Timed Out!")
                continue
            



    async def remove_user(self, index):
        """
            If the person at users index index is a werewolf then reduce count of werewolves by one and remove that user.
            If they are a hunter, let them kill a player of their choice. 
            Before removing the user check if they are under cupids spell, if so kill their partner as well


        """
        if self.role_dict[self.users[index]] == "Werewolf":
            self.num_wolves -= 1
            self.werewolves.remove(self.users[index])
        elif self.role_dict[self.users[index]] == "Hunter" and self.cycle == "day":
            await self.ctx.send("My God he has got a crossbow, hunter who do you want to kill?")
            hunter_choice = await self.killer_turn(werewolf=False)
            await self.ctx.send(f"Just before being put to death, the hunter killed {self.users[hunter_choice].name}")
            await self.remove_user(hunter_choice) 

        if self.users[index] in self.cupid_choice:
            self.cupid_choice.remove(self.users[index])
            await self.ctx.send(f"Overcome with grief by the loss of {self.users[index].name}, {self.cupid_choice[0].name} killed themself!")
            self.users.pop(index)
            self.users.remove(self.cupid_choice[0])
        else:
            self.users.pop(index)  

    async def cupid_turn(self):
        """
        
        """
        def cupid_check(m):
            try:
                m.content = m.content.split(',')
                temp = [self.users[int(i-1)] for i in m.content]
                return True and (len(temp)==2) and temp[0] != temp[1] #and m.author == self.cupid to be added in in final version
            except: 
                return False 
            
        await self.ctx.send("Cupid is choosing")
        cupid_id = self.client.get_user(int(self.cupid.id))
        embed_users = await self.draw_users()
        await cupid_id.send(embed=embed_users)
        await cupid_id.send("Cupid choose who is to fall in love!\nReply to this message in the form a,b where a and b are your choices")

        try:
            cupid_choice = await self.client.wait_for('message', timeout=45.0, check=cupid_check)
            self.cupid_choice = [self.users[int(i-1)] for i in cupid_choice.content]
        except Exception as e:
            print(e)
            await cupid_id.send("Timed Out!")

    async def doc_turn(self):
        def doc_check(m):
            return (m.content in list(map(lambda x: str(x), range(1,len(self.users)+1)))) and m.author == self.doc
            
        doctor_id = self.client.get_user(int(self.doc.id))
        embed_users = await self.draw_users()
        await doctor_id.send(embed=embed_users)

        await doctor_id.send("Doctor choose who to save\nReply to this message with the corresponding number")

        try:
            doc_choice = await self.client.wait_for('message', timeout=45.0, check=doc_check)
            return int(doc_choice.content) - 1
        except Exception as e:
            await self.ctx.send("Timed Out!")
            return -1

    async def seer_turn(self):
        def seer_check(m):
            return (m.content in list(map(lambda x: str(x), range(1,len(self.users)+1)))) #and m.author == self.seer
            
        
        seer_id = self.client.get_user(int(self.seer.id))
        embed_users = await self.draw_users()
        await seer_id.send(embed=embed_users)

        await seer_id.send("Seer choose who you want to peek at!\nReply to this message with the corresponding number")

        try:
            seer_choice = await self.client.wait_for('message', timeout=45.0, check=seer_check)
            user = self.users[int(seer_choice.content)-1]
            await seer_id.send(str(user.name) + " is " + str(self.role_dict[user]))
        except Exception as e:
            print(e)
            await seer_id.send("Timed Out!")

    async def killer_turn(self, werewolf = True):
        def killer_check(m):
            """
                If message is within range and if the parent function is called with werewolf = True, then author must be first werewolf
            """
            return (m.content in list(map(lambda x: str(x), range(1,len(self.users)+1))))# and (werewolf == (m.author == self.werewolves[0]))

        if werewolf: 
            werewolf_id = self.client.get_user(int(self.werewolves[0].id))
            embed_users = await self.draw_users()
            await werewolf_id.send(embed=embed_users)
            await werewolf_id.send("Werewolf choose who you want to kill!\nReply to this message with the corresponding number")
        else:    
            embed_users = await self.draw_users()
            await self.ctx.send(embed=embed_users)
        #send to all werewolves, but only get response from one
        while True:
            try:
                killer_choice = await self.client.wait_for('message', timeout=45.0, check=killer_check)
                return int(killer_choice.content) - 1
            except Exception as e:
                if werewolf:
                    await werewolf_id.send("Timed Out!, Choose a victim")
                else:
                    await self.ctx.send("Timed Out!, Choose a victim")
                continue

    async def show_werewolfs(self):
        wolves = ""
        for wolf in self.werewolves:
            wolves += wolf.name + "\t"
        for wolf in self.werewolves:
            werewolf_id = self.client.get_user(wolf.id)
            await werewolf_id.send(f"The werewolves are: {wolves}")
                

    async def main(self):
        """
            Send each player their role
        """
        for user in self.users:
            user_id = self.client.get_user(int(user.id))
            await user_id.send(self.role_dict[user])

        await self.show_werewolfs()
        await self.cupid_turn()
        #while their are non zero wolves or greater villagers than wolves
        while self.num_wolves > 0 and (2 * self.num_wolves < len(self.users)):
            await self.night()
            await self.day()
        if self.num_wolves == 0:
            await self.ctx.send("All werewolves eliminated, congrats villagers!")
        else:
            await self.ctx.send("The werewolves have taken over.")

    async def draw_users(self):
        embed_users = discord.Embed(title=f"User List", color=0x00ff00)
        for i, user in enumerate(self.users):
            embed_users.add_field(name=i+1, value=user.name, inline=True)
        return embed_users

        





class Werewolf(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()    
    async def werewolf(self, ctx):

        embed_rules = discord.Embed(title="Werewolf", color=0x00ff00)

        embed_rules.add_field(name='How to Play?', value='https://www.playwerewolf.co/how-to-play-werewolf-in-75-seconds', inline=False)
        embed_rules.add_field(name='Discord Specific: How to Play?', value='Those with special roles will be dm\'d instructions during the night cycle. Only one werewolf can choose who to kill each night, make sure to discuss it with each other via dm. Lastly when voting for who to lynch during the day, reply to the bot with the number of who you choose to kill. To help with voting make use of the $poll command', inline=False)
        embed_rules.add_field(name='How to Join', value='To play react to this message', inline=False)

        msg = await ctx.send(embed=embed_rules)
        await msg.add_reaction(emoji = '\U00002705')
        await asyncio.sleep(15)

        cache_msg = discord.utils.get(self.client.cached_messages, id = msg.id)
        reaction = cache_msg.reactions[0]
        users = await reaction.users().flatten()
        users = [x for x in users if str(x) != str(self.client.user)]
        if 5 < len(users) < 17:
            ww = werewolf(ctx, self.client, users)
            await ww.main()
        else:
            await ctx.send("Game requires 6 to 16 players!")
def setup(client):
    client.add_cog(Werewolf(client))