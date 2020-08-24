import discord
from discord.ext import commands
import requests
import random
import asyncio


class TicTacToe():

    def __init__(self, player_letter, ctx, client, PvP):
        self.board = ["___", '\u0031\u20E3', '\u0032\u20E3', '\u0033\u20E3', '\u0034\u20E3',
                      '\u0035\u20E3', '\u0036\u20E3', '\u0037\u20E3', '\u0038\u20E3', '\u0039\u20E3']
        self.turns = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        self.player_letter = player_letter
        self.ctx = ctx
        self.client = client
        self.rounds = 0
        self.letter_dict = {'X': '\u274C', 'O': '\u2B55'}
        if PvP:
            self.player2_letter = self.other_letter(player_letter)
        else:
            self.comp_letter = self.other_letter(player_letter)

    async def drawBoard(self):
        """Prints the board in the correct format"""
        tic_embed = discord.Embed(title='TicTacToe', color=0x00ff00)
        tic_embed.add_field(name=".", value=self.board[7], inline=True)
        tic_embed.add_field(name=".", value=self.board[8], inline=True)
        tic_embed.add_field(name=".", value=self.board[9], inline=True)
        tic_embed.add_field(name=".", value=self.board[4], inline=True)
        tic_embed.add_field(name=".", value=self.board[5], inline=True)
        tic_embed.add_field(name=".", value=self.board[6], inline=True)
        tic_embed.add_field(name=".", value=self.board[1], inline=True)
        tic_embed.add_field(name=".", value=self.board[2], inline=True)
        tic_embed.add_field(name=".", value=self.board[3], inline=True)

        if self.rounds < 1:
            self.game_board = await self.ctx.send(embed=tic_embed)
            for i in range(9):
                await self.game_board.add_reaction(emoji=self.board[1:][i])
        else:
            await self.game_board.edit(embed=tic_embed)

    def player_move(self, move, letter):
        """Updates the board with the players turn, removes that option from turns"""
        self.turns.remove(move)
        self.board[move] = self.letter_dict[letter]

    def other_letter(self, letter):
        """If player is X, comp is O visa versa"""
        if letter == "X":
            return "O"
        else:
            return "X"

    def victory(self, board):
        """Returns True if any victory conditions are met"""
        return (((board[7] == board[8]) and (board[8] == board[9])) or
                # across the middle
                ((board[4] == board[5]) and (board[5] == board[6])) or
                # across the bottom
                ((board[1] == board[2]) and (board[2] == board[3])) or
                # down the left side
                ((board[1] == board[4]) and (board[4] == board[7])) or
                # down the middle
                ((board[2] == board[5]) and (board[5] == board[8])) or
                # down the right side
                ((board[3] == board[6]) and (board[6] == board[9])) or
                ((board[1] == board[5]) and (board[5] == board[9])) or  # diagonal
                ((board[7] == board[5]) and (board[5] == board[3])))  # diagonal

    async def comp_move_ai(self):
        """Makes a copy of the board, then iterates through all the remaining turns, 
        firstly to see if there is any move that will result in victory for the computer.
        Then to see if there are any moves which will see the player win, if so blocks that move. If no move will lead
        to victory then the computer randomly chooses its move"""

        # checking for victory move for computer, must come before block loop
        for i in range(len(self.turns)):
            test_board = self.board[:]
            test_board[self.turns[i]] = self.letter_dict[self.comp_letter]
            if self.victory(test_board):
                # if victory update the board and remove from turns list
                self.board[self.turns[i]] = self.letter_dict[self.comp_letter]
                self.turns.remove(self.turns[i])
                # await self.drawBoard()
                return
        # checking for blocking move for comp
        for i in range(len(self.turns)):
            test_board = self.board[:]
            test_board[self.turns[i]] = self.letter_dict[self.player_letter]
            if self.victory(test_board):
                # if victory update the board and remove from turns list
                self.board[self.turns[i]] = self.letter_dict[self.comp_letter]
                self.turns.remove(self.turns[i])
                # await self.drawBoard()
                return

        # turns keeps track of options we have left, this line randomly chooses
        comp = random.choice(self.turns)
        self.board[comp] = self.letter_dict[self.comp_letter]
        self.turns.remove(comp)
        # await self.drawBoard()

    async def mainGame(self):
        def move_check(m):
            return (m.content in list(map(lambda x: str(x), self.turns)) or m.content.lower() == "stop")

        def react_check(msg):
            def check(reaction, reacting_user):
                return reacting_user != self.client.user and str(reaction.emoji) in self.board and reaction.message.id == msg.id and self.board.index(str(reaction.emoji)) in self.turns
            return check
        flag = True
        while flag:  # while no victory is determined or while there are turns left to make
            self.rounds += 1
            # await self.ctx.send("Choose your spot\n")

            try:
                # move = await self.client.wait_for('message', timeout=45.0, check=move_check)
                reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=react_check(self.game_board))
                move = self.board.index(str(reaction.emoji))
            except:
                await self.ctx.send('Timed Out!')
                break

            else:
                self.player_move(int(move), self.player_letter)
                await self.drawBoard()
                if self.turns == [] or self.victory(self.board):
                    # if no moves left or victory reached, otherwise computers turn
                    flag = False
                    await self.drawBoard()
                else:
                    await asyncio.sleep(0.5)
                    await self.comp_move_ai()
                    await self.drawBoard()
                    if self.turns == [] or self.victory(self.board):
                        flag = False

        await self.ctx.send("Game Over!")

    async def player_move_code(self, player):
        def react_check(msg):
            def check(reaction, reacting_user):
                return reacting_user != self.client.user and str(reaction.emoji) in self.board and reaction.message.id == msg.id and self.board.index(str(reaction.emoji)) in self.turns
            return check

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout=30.0, check=react_check(self.game_board))
            move = self.board.index(str(reaction.emoji))
            return move
        except Exception as e:
            print(e)
            await self.ctx.send('Timed Out!')
            flag = False

    async def mainGamePvP(self):

        flag = True
        move = ""
        while flag:  # while no victory is determined or while there are turns left to make
            self.rounds += 1
            move = await self.player_move_code("Player 1")

            self.player_move(int(move), self.player_letter)
            await self.drawBoard()
            if self.turns == [] or self.victory(self.board):
                # if no moves left or victory reached, otherwise computers turn
                flag = False
            else:
                move = await self.player_move_code("Player 2")
                self.player_move(int(move), self.player2_letter)
                await self.drawBoard()
                if self.turns == [] or self.victory(self.board):
                    flag = False

        await self.ctx.send("Game Over!")
