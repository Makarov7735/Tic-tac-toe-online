import websockets
import asyncio
import json
import sys
from game import Game

class Server:
    
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.users = dict()
        self.games = []

    async def main_server(self):
        print(f'Server started at ws://{self.host}:{self.port}\nListen connections...')
        async with websockets.serve(self.listen_sockets, self.host, self.port):
            await asyncio.Future() 

    async def remove_user(self, websocket):
        username = self.users[websocket]['username']
        ip = self.users[websocket]['ip']
        port = self.users[websocket]['port']

        print(f'[{ip}:{port}] {username} left game')
        del self.users[websocket]

        for game in self.games:
            if websocket in game.users:
                await game.delete_game(user_left_game=True)

    async def login_user(self, websocket, username):
        ip, port = websocket.remote_address
        self.users[websocket] = {
            'username': username,
            'status': 'waiting',
            'ip': ip,
            'port': port
        }

        print(f'[{ip}:{port}] {username} join game')
        
    async def change_user_status(self, websocket, new_status):
        self.users[websocket]['status'] = new_status
        if new_status == 'wait_game':
            await self.check_game_waiting_users()

    async def check_game_waiting_users(self):
        game_waiting_users = [
            user for user in self.users if self.users[user]['status'] == 'wait_game'
        ]
        
        while len(game_waiting_users) >= 2:
            user1, user2, *_ = game_waiting_users

            for user in (user1, user2):
                game_waiting_users.remove(user)
                self.users[user]['status'] = 'in_game'

            game = Game(self, user1, user2)
            self.games.append(game)

            await game.send_game_meta_data((user1, user2))

    async def set_new_game_state(self, websocket, data):
        for game in self.games:
            if websocket in game.users:
                await game.set_new_game_state(websocket, data['game_state'])

    async def listen_sockets(self, websocket):
        try:
            while True:
                data_json = await websocket.recv()
                data = json.loads(data_json)
                
                if data['status'] == 'login':
                    await self.login_user(websocket, data['username'])
                elif data['status'] == 'change_status':
                    await self.change_user_status(websocket, data['new_status'])
                elif data['status'] == 'game_state':
                    await self.set_new_game_state(websocket, data)

        except (websockets.exceptions.ConnectionClosedOK,
                websockets.exceptions.ConnectionClosedError):
            await self.remove_user(websocket)


def main():
    try:
        host, port = sys.argv[1], sys.argv[2]
    except IndexError:
        host, port = '127.0.0.1', '8000'
    server = Server(host, port)
    try:
        asyncio.run(server.main_server())
    except KeyboardInterrupt:
        exit()

if __name__ == '__main__':
    main()