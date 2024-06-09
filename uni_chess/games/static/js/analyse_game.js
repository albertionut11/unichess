document.addEventListener("DOMContentLoaded", function() {
    const prevButton = document.getElementById("prev-move");
    const nextButton = document.getElementById("next-move");
    const gameId = document.getElementById("game_id").value;
    let movesElement = document.getElementById("moves-data");
    let moves = JSON.parse(movesElement.textContent);

    let currentMoveIndex = 0;

    prevButton.addEventListener("click", () => navigateMoves(-1));
    nextButton.addEventListener("click", () => navigateMoves(1));

    function navigateMoves(direction) {
        currentMoveIndex += direction;
        if (currentMoveIndex < -1) {
            currentMoveIndex = 0;
        } else if (currentMoveIndex >= moves.length) {
            currentMoveIndex = moves.length - 1;
        }
        updateBoard(currentMoveIndex);
    }

    function updateBoard(index) {
        fetch(`/analyse/${gameId}/move`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({ indice: index })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                const jsonTable = JSON.parse(data.json_table);
                renderBoard(jsonTable);
            } else {
                console.error("Failed to update board");
            }
        })
        .catch(error => console.error("Error:", error));
    }

    function renderBoard(jsonTable) {
        for (const [row, columns] of Object.entries(jsonTable)) {
            for (const [col, piece] of Object.entries(columns)) {
                const position = `${row}${col}`;
                console.log("Position:", position);
                console.log("Piece:", piece);
                const square = document.querySelector(`td[data-position="${position}"]`);
                if (square) {
                    square.innerHTML = piece !== 'None' ? `<img src="/static/chess/pieces/${piece}.svg" alt="${piece}">` : '';
                }
            }
        }
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
