document.addEventListener("DOMContentLoaded", function() {
    const prevButton = document.getElementById("prev-move");
    const nextButton = document.getElementById("next-move");
    const chessTable = document.getElementById("chess-table");
    const moves = JSON.parse(chessTable.dataset.moves);
    let currentMoveIndex = -1;

    prevButton.addEventListener("click", () => navigateMoves(-1));
    nextButton.addEventListener("click", () => navigateMoves(1));

    function navigateMoves(direction) {
        currentMoveIndex += direction;
        if (currentMoveIndex < -1) {
            currentMoveIndex = -1;
        } else if (currentMoveIndex >= moves.length) {
            currentMoveIndex = moves.length - 1;
        }
        updateBoard(currentMoveIndex);
    }

    function updateBoard(index) {
        resetBoard();
        for (let i = 0; i <= index; i++) {
            const move = moves[i];
            if (move) {
                const [from, to] = move.match(/[a-h][1-8]/g);
                movePiece(from, to);
            }
        }
    }

    function resetBoard() {
        const squares = document.querySelectorAll("td[data-position]");
        squares.forEach(square => {
            square.innerHTML = '';
        });

        const initialSetup = [
            ["a1", "wR"], ["b1", "wN"], ["c1", "wB"], ["d1", "wQ"], ["e1", "wK"], ["f1", "wB"], ["g1", "wN"], ["h1", "wR"],
            ["a2", "wP"], ["b2", "wP"], ["c2", "wP"], ["d2", "wP"], ["e2", "wP"], ["f2", "wP"], ["g2", "wP"], ["h2", "wP"],
            ["a8", "bR"], ["b8", "bN"], ["c8", "bB"], ["d8", "bQ"], ["e8", "bK"], ["f8", "bB"], ["g8", "bN"], ["h8", "bR"],
            ["a7", "bP"], ["b7", "bP"], ["c7", "bP"], ["d7", "bP"], ["e7", "bP"], ["f7", "bP"], ["g7", "bP"], ["h7", "bP"]
        ];

        initialSetup.forEach(([pos, piece]) => {
            const square = document.querySelector(`td[data-position="${pos}"]`);
            const img = document.createElement("img");
            img.src = `/static/chess/pieces/${piece}.svg`;
            img.draggable = false;
            square.appendChild(img);
        });
    }

    function movePiece(from, to) {
        const fromSquare = document.querySelector(`td[data-position="${from}"]`);
        const toSquare = document.querySelector(`td[data-position="${to}"]`);
        if (fromSquare && toSquare) {
            toSquare.innerHTML = fromSquare.innerHTML;
            fromSquare.innerHTML = '';
        }
    }

    resetBoard();
});
