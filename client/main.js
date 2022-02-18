
class ticTacToe {
    constructor() {
        this.circle = '<img src="images/circle.png" class="circle">';
        this.cross = '<img src="images/cross.png" class="cross">';
        this.yourSymbol = this.cross;
        this.yourSymbolStr = 'x';
        this.enemySymbol = this.circle;
        this.enemySymbolStr = '0';
        this.HTMLFields = document.querySelectorAll('.field');
        this.fields = ['', '', '', '', '', '', '', '', ''];
        this.gameEnded = true;
        this.yourTurn = false;
        this.title = document.querySelector('.title');
        this.vstitle = document.querySelector('.vstitle');
        this.loader = document.querySelector('.loader');
    }
    restartGame() {
        for (let i of this.HTMLFields) {
            i.innerHTML = '';
        }
        this.fields = ['', '', '', '', '', '', '', '', ''];
        this.setTitleText('Searching for game');
        this.loader.hidden = false;
        this.vstitle.innerHTML = '';
        this.gameEnded = true;
    }
    getRandomField() {
        return Math.floor(Math.random() * 9 + 1);
    }
    setTitleText(text) {
        this.title.innerHTML = text;
    }
    winnerChecker(symbol) {
        let winningPositions = [
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
            [2, 4, 6],
            [0, 4, 8],
        ];
        for (let i of winningPositions) {
            if (this.fields[i[0]] == symbol && 
                this.fields[i[1]] == symbol &&
                this.fields[i[2]] == symbol) {
                return true;
            }
        }
    }
    gameEndedChecker() {
        if (this.winnerChecker(this.yourSymbolStr)) {
            this.setTitleText('You win!');
            this.gameEnded = true;
        } else if (this.winnerChecker(this.enemySymbolStr)) {
            this.setTitleText('You lose.');
            this.gameEnded = true;
        } else if (!this.fields.includes('')) {
            this.setTitleText('It\'s draw.');
            this.gameEnded = true;
        }

        if (this.gameEnded) {
            let data = JSON.stringify({'status': 'change_status', 'new_status': 'waiting'});
            websocket.send(data);
        }
    }
    sendGameState(fieldNum) {
        let data = JSON.stringify({'status': 'game_state', 'game_state': fieldNum});
        websocket.send(data);
    }
    setEnemyMove(position) {
        this.fields[position-1] = this.enemySymbolStr;
        for (let field of this.HTMLFields) {
            if (field.getAttribute('field-num') == position) {
                field.innerHTML = this.enemySymbol;
                this.yourTurn = true;
                break;
            }
        }
        this.gameEndedChecker();
    }
    click(el) {
        if (el.getAttribute('class') == 'find-game') {
            this.restartGame();
        }
        else if (!el.innerHTML && this.fields.includes('') && !this.gameEnded && this.yourTurn) {
            let fieldNum = el.getAttribute('field-num');
            this.fields[fieldNum-1] = this.yourSymbolStr;
            el.innerHTML = this.yourSymbol;
            this.yourTurn = false;
            this.sendGameState(Number(fieldNum));
            this.gameEndedChecker();
        }
    }
}


function main() {
    tTT.click(this);
}

let fields = document.querySelectorAll('.field');
let tTT = new ticTacToe;
for (let i of fields) {
    i.addEventListener('click', main);
}


let websocket = new WebSocket('ws://127.0.0.1:9000');
let findGameButton = document.querySelector('.find-game');


function setMetaData(data) {
    let vstitle = document.querySelector('.vstitle');
    tTT.loader.hidden = true;
    vstitle.innerHTML = data['user1'] + ' vs '+ data['user2'];
    tTT.setTitleText('Game Started!<br>You are '+data['your_symbol']);
    tTT.gameEnded = false;
    tTT.yourTurn = data['your_turn'];
    if (data['your_symbol'] == 'x') {
        tTT.yourSymbol = tTT.cross;
        tTT.yourSymbolStr = 'x';
        tTT.enemySymbol = tTT.circle;
        tTT.enemySymbolStr = '0';
    } else {
        tTT.yourSymbol = tTT.circle;
        tTT.yourSymbolStr = '0';
        tTT.enemySymbol = tTT.cross;
        tTT.enemySymbolStr = 'x';
    }
}


websocket.addEventListener('open', event => {
    let username;
    while (!username) {
        username = prompt('Enter your username');
    }
    let data = JSON.stringify({'status': 'login', 'username': username});
    websocket.send(data);
});

websocket.addEventListener('message', event => {
    let data = JSON.parse(event.data);
    
    if (data['status'] == 'game_meta_data') {
        setMetaData(data);
    } else if (data['status'] == 'game_state') {
        tTT.setEnemyMove(data['game_state']);
    } else if (data['status'] == 'game_ended') {
        if (data['mod'] == 'enemy_left_game') {
            tTT.setTitleText('Enemy left game.')
        }
        tTT.gameEnded = true;
    }
});


findGameButton.addEventListener('click', event => {
    if (tTT.gameEnded == true) {
        tTT.restartGame();
        setTimeout(() => {
            let data = JSON.stringify({'status': 'change_status', 'new_status': 'wait_game'});
            websocket.send(data);
        }, 500);
    }
});
