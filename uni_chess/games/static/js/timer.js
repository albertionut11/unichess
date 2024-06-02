let whiteTime;
let blackTime;

document.addEventListener("DOMContentLoaded", function() {
    whiteTime = parseInt(document.getElementById("initial_white_time").value); // Time in seconds
    blackTime = parseInt(document.getElementById("initial_black_time").value); // Time in seconds
    const increment = parseInt(document.getElementById("time_increment").value);

    let whiteTimerElement = document.getElementById("white-timer");
    let blackTimerElement = document.getElementById("black-timer");

    let whiteInterval, blackInterval;
    let gameOver = false;

    function startTimer(turn) {
        if (turn === 'white') {
            clearInterval(blackInterval);
            whiteInterval = setInterval(() => updateTimer('white'), 1000);
        } else {
            clearInterval(whiteInterval);
            blackInterval = setInterval(() => updateTimer('black'), 1000);
        }
    }

    function updateTimer(player) {
        if (gameOver) return;

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
    }

    function formatTime(time) {
        const minutes = Math.floor(time / 60);
        const seconds = time % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    }

    function endGame(winner, message) {
        gameOver = true;
        clearInterval(whiteInterval);
        clearInterval(blackInterval);
        const messageDiv = document.getElementById("checkmate-message");
        messageDiv.innerText = message;
        messageDiv.classList.add("checkmate-message");
        alert(message);
    }

    const gameId = document.getElementById("game_id").value;
    let turn = document.getElementById("turn").value;

    const socket = new WebSocket(`ws://${window.location.host}/ws/game/${gameId}/`);

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        turn = data.turn;

        whiteTime = data.white_time_remaining;
        blackTime = data.black_time_remaining;

        document.getElementById("turn").value = turn;
        document.getElementById("turn-display").innerText = turn;

        // Update the timer
        if (data.turn === 'white') {
            blackTime += increment;
        } else {
            whiteTime += increment;
        }
        startTimer(data.turn);
    };

    startTimer(turn);
});
