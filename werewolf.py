import random


class werewolf():
    def __init__(self):
        self.users = ["Callum", "Beak", "Alex", "Sean", "Graham", "David", "Dan", "Ben", "Filipe", "Frank", "Shane"]
        self.set_roles()
        # self.show_werewolfs()#Method to provately send list of werewolves to the other werewolves at the start of the game


    def set_roles(self):
        self.num_wolves = 2
        self.num_villagers_with_roles = 3
        num = len(self.users)
        if num > 9:
            self.num_wolves = 3
            self.num_villagers_with_roles = 5

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

    def night(self):
        for i, user in enumerate(self.users):
            print(i, user)
        werewolf_choice = int(input("Werewolves choose who you will kill: "))
        doc_choice = int(input("Doctor choose who you will save: "))
        seer_choice = int(input("Seer choose who you will look at: "))

        print(self.users[seer_choice], "is ", self.role_dict[self.users[seer_choice]])


        if werewolf_choice != doc_choice:
            print(f"{self.users[werewolf_choice]} was brutally mauled to death last night")
            self.remove_user(werewolf_choice)
        else:
            print(f"{self.users[werewolf_choice]} was attacked last night, but the doctor managed to save them")

    def day(self):
        for i, user in enumerate(self.users):
            print(i, user)
        #need to plan for tie
        lynch_choice = int(input("You have 5 minutes to decide who to lynch!\n"))
        #do the wait thing for 5 mins
        print(f"{self.users[lynch_choice]} was put to death")
        self.remove_user(lynch_choice)

    def remove_user(self, index):
        if self.role_dict[self.users[index]] == "Werewolf":
            self.num_wolves -= 1
        elif self.role_dict[self.users[index]] == "Hunter":
            hunter_choice = int(input("Hunter choose who you will kill: "))
            print(f"Just before being put to death, the hunter killed {self.users[hunter_choice]}")
            self.remove_user(hunter_choice)           
        if self.users[index] in self.cupid_choice:
            self.cupid_choice.remove(self.users[index])
            print(f"Overcome with grief by the loss of {self.users[index]}, {self.cupid_choice[0]} killed themself!")
            self.users.pop(index)
            self.users.remove(self.cupid_choice[0])
        else:
            self.users.pop(index)  

    def cupid_turn(self):
        for i, user in enumerate(self.users):
            print(i, user)
        cupid_choice = input("Cupid choose who is to fall in love\n")
        cupid_choice = cupid_choice.split(',')
        self.cupid_choice = [self.users[int(i)] for i in cupid_choice]

    def main(self):
        self.cupid_turn()
        while self.num_wolves > 0 and (2 * self.num_wolves != len(self.users)): 
            self.night()
            self.day()
        if self.num_wolves == 0:
            print("All werewolves eliminated, congrats villagers!")
        else:
            print("The werewolves have taken over.")    


        



        




ww = werewolf()
# print(ww.villagers)
# print(ww.villagers_with_roles) 
# print(ww.villagers_without_roles) 
# print(ww.doc) 
# ww.show_roles()

ww.main()
print(ww.role_dict)


