document.addEventListener("DOMContentLoaded", function() {
    const prevButton = document.getElementById("prev-move");
    const nextButton = document.getElementById("next-move");
    const gameId = document.getElementById("game_id").value;
    let movesElement = document.getElementById("moves-data");
    let moves = JSON.parse(movesElement.textContent);
    let currentMoveIndex = 0;

    prevButton.addEventListener("click", () => navigateMoves(-1));
    nextButton.addEventListener("click", () => navigateMoves(1));
    highlightCurrentMove(currentMoveIndex);

    function navigateMoves(direction) {
        currentMoveIndex += direction;
        if (currentMoveIndex < 0) {
            currentMoveIndex = 0;
        } else if (currentMoveIndex > moves.length) {
            currentMoveIndex = moves.length;
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
                highlightCurrentMove(index);
                const jsonTable = JSON.parse(data.json_table);
                renderBoard(jsonTable);
                updateEvaluation(data.evaluation);
                updateSuggestions(data.suggestions);
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
                const square = document.querySelector(`td[data-position="${position}"]`);
                if (square) {
                    square.innerHTML = piece !== 'None' ? `<img src="/static/chess/pieces/${piece}.svg" alt="${piece}">` : '';
                }
            }
        }
    }

    function updateEvaluation(evaluation) {
        const evaluationBox = document.getElementById("evaluation-box");
        evaluationBox.textContent = `Evaluation: ${evaluation}`;
    }

    function updateSuggestions(suggestions) {
        const suggestionsList = document.getElementById("suggestions-list");
        suggestionsList.innerHTML = '';
        suggestions.forEach(suggestion => {
            const listItem = document.createElement("li");
            listItem.textContent = suggestion;
            suggestionsList.appendChild(listItem);
        });

        drawSuggestionArrows(suggestions.slice(0, 3));
    }

    function highlightCurrentMove(index) {
        document.querySelectorAll('.cell-highlight').forEach(el => el.classList.remove('cell-highlight'));

        const moveRow = Math.floor(index / 2);
        const moveCol = index % 2 === 0 ? 'white' : 'black';

        const cell = document.querySelector(`.moves-table tbody tr:nth-child(${moveRow + 1}) td:nth-child(${moveCol === 'white' ? 2 : 3})`);
        if (cell) {
            cell.classList.add('cell-highlight');
        }
    }

    function drawSuggestionArrows(suggestions) {
        clearArrows();
        suggestions.forEach(suggestion => {
            const from = suggestion[1] + suggestion[0];
            const to = suggestion[3] + suggestion[2];
            drawArrow(from, to);
        });
    }

    function drawArrow(from, to) {
        const chessContainer = document.getElementById("chess-container");
        const fromSquare = document.querySelector(`td[data-position="${from}"]`);
        const toSquare = document.querySelector(`td[data-position="${to}"]`);

        if (fromSquare && toSquare) {
            const fromRect = fromSquare.getBoundingClientRect();
            const toRect = toSquare.getBoundingClientRect();
            const containerRect = chessContainer.getBoundingClientRect();

            const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
            svg.setAttribute("class", "arrow");
            svg.setAttribute("style", `position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none;`);
            svg.setAttribute("viewBox", `0 0 ${containerRect.width} ${containerRect.height}`);

            const line = document.createElementNS("http://www.w3.org/2000/svg", "line");
            line.setAttribute("x1", fromRect.left + fromRect.width / 2 - containerRect.left);
            line.setAttribute("y1", fromRect.top + fromRect.height / 2 - containerRect.top);
            line.setAttribute("x2", toRect.left + toRect.width / 2 - containerRect.left);
            line.setAttribute("y2", toRect.top + toRect.height / 2 - containerRect.top);
            line.setAttribute("stroke", "rgba(0, 128, 0, 1)");
            line.setAttribute("stroke-width", "10");
            line.setAttribute("marker-end", "url(#arrowhead)");

            svg.appendChild(line);
            chessContainer.appendChild(svg);
        }
    }

    function clearArrows() {
        document.querySelectorAll('.arrow').forEach(arrow => arrow.remove());
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
