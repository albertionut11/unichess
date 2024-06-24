let whiteTime;
let blackTime;
let whiteInterval, blackInterval;
let gameOver = false;

document.addEventListener("DOMContentLoaded", function() {
    const gameId = document.getElementById("game_id").value;
    const increment = parseInt(document.getElementById("time_increment").value);
    const whiteTimerElement = document.getElementById("white-timer");
    const blackTimerElement = document.getElementById("black-timer");
    const COUNTER_KEY_WHITE = `white-counter-${gameId}`;
    const COUNTER_KEY_BLACK = `black-counter-${gameId}`;

    function saveToSessionStorage() {
        window.sessionStorage.setItem(COUNTER_KEY_WHITE, whiteTime);
        window.sessionStorage.setItem(COUNTER_KEY_BLACK, blackTime);
    }

    function startTimer(turn) {
        let started = document.getElementById("started").value;
        let isActive = document.getElementById("is_active").value;

        if (isActive === "False" || started === "False") return;

        clearInterval(whiteInterval);
        clearInterval(blackInterval);

        if (turn === 'white') {
            whiteInterval = setInterval(() => updateTimer('white'), 1000);
        } else {
            blackInterval = setInterval(() => updateTimer('black'), 1000);
        }
    }

    function updateTimer(player) {

        if (player === 'white') {
            whiteTime--;
            if (whiteTime < 0) {
                endGame('black', 'White ran out of time');
            } else {
                whiteTimerElement.textContent = formatTime(whiteTime);
            }
        } else {
            blackTime--;
            if (blackTime < 0) {
                endGame('white', 'Black ran out of time');
            } else {
                blackTimerElement.textContent = formatTime(blackTime);
            }
        }
        saveToSessionStorage();
    }

    function formatTime(time) {
        const minutes = Math.floor(time / 60);
        const seconds = time % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    function endGame(winner, message) {
        clearInterval(whiteInterval);
        clearInterval(blackInterval);
        const messageDiv = document.getElementById("endgame-message");
        messageDiv.innerText = message;
        messageDiv.classList.add("checkmate-message");

    }

    function initializeTimers() {
        whiteTime = parseInt(window.sessionStorage.getItem(COUNTER_KEY_WHITE)) || parseInt(document.getElementById("initial_white_time").value) * 60;
        blackTime = parseInt(window.sessionStorage.getItem(COUNTER_KEY_BLACK)) || parseInt(document.getElementById("initial_black_time").value) * 60;

        whiteTimerElement.textContent = formatTime(whiteTime);
        blackTimerElement.textContent = formatTime(blackTime);

        let turn = document.getElementById("turn").value;

        startTimer(turn);
    }

    initializeTimers();

    const socket = new WebSocket(`ws://${window.location.host}/ws/game/${gameId}/`);

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        if (data.type === "game_move"){
        let turn = data.turn;
        console.log(data);

        whiteTime = data.white_time_remaining;
        blackTime = data.black_time_remaining;

        if (turn === 'white') {
            blackTime += increment;
        }
        else {
            whiteTime += increment;
        }

        whiteTimerElement.textContent = formatTime(whiteTime);
        blackTimerElement.textContent = formatTime(blackTime);

        startTimer(data.turn);

        }
    };

    window.startTimer = startTimer;
    window.updateTimer = updateTimer;
    window.formatTime = formatTime;
});
