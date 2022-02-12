import random
import json


class Game:

    def __init__(self, sevrer_object, user1, user2):
        self.server = sevrer_object
        self.users = (user1, user2)
        self.game_ended = False
        self.whoseTurn = random.choice(self.users)
        self.cross = self.whoseTurn
        self.circle = self.users[self.users.index(self.whoseTurn)-1]
        self.game_state = ['', '', '', '', '', '', '', '', '']
        print(f'New game {self}')
        
    async def send_game_meta_data(self, users: tuple):
        data = {
            'status': 'game_meta_data',
            'user1': self.server.users[users[0]]['username'],
            'user2': self.server.users[users[1]]['username']
        }
        for user in self.users:
            if user == self.cross:
                data['your_turn'] = True
                data['your_symbol'] = 'x'
            else:
                data['your_turn'] = False
                data['your_symbol'] = '0'

            data_json = json.dumps(data)
            await user.send(data_json)

    async def set_new_game_state(self, websocket, position):
        if self.whoseTurn == websocket:
            if websocket == self.cross:
                self.game_state[position-1] = 'x'
                await self.check_game_ended()
                self.whoseTurn = self.circle
                data = {
                    'status': 'game_state',
                    'game_state': position
                }
                data_json = json.dumps(data)
                await self.circle.send(data_json)
            else:
                self.game_state[position-1] = '0'
                await self.check_game_ended()
                self.whoseTurn = self.cross
                data = {
                    'status': 'game_state',
                    'game_state': position
                }
                data_json = json.dumps(data)
                await self.cross.send(data_json)
    
    async def delete_game(self, user_left_game=False):
        if user_left_game:
            data_json = json.dumps({'status': 'game_ended', 'mod': 'enemy_left_game'})
        else:
            data_json = json.dumps({'status': 'game_ended', 'mod': 'game_ended'})

        for user in self.users:
            if user in self.server.users:
                self.server.users[user]['status'] = 'waiting'
                await user.send(data_json)
        
        self.server.games.remove(self)
        print(f'Game ended {self}')

    async def winner_checker(self, symbol):
        winning_positions = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [2, 4, 6],
            [0, 4, 8],
        ]
        for i in winning_positions:
            if self.game_state[i[0]] == symbol and self.game_state[i[1]] == symbol and self.game_state[i[2]] == symbol:
                return True

    async def check_game_ended(self):
        if await self.winner_checker('x') or await self.winner_checker('0') or not '' in self.game_state:
            await self.delete_game()
        