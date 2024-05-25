// old_highlights.js

document.addEventListener("DOMContentLoaded", function() {
    const pieces = document.querySelectorAll("img[draggable='true']");
    const squares = document.querySelectorAll("td[data-position]");
    const gameId = document.getElementById("game_id").value;
    const userRole = document.getElementById("user_role").value;
    let turn = document.getElementById("turn").value;
    let selectedPiece = null;
    let highlightedMoves = [];

    function updateDraggable() {
        pieces.forEach(piece => {
            piece.removeEventListener("click", handleClick);
        });

        if ((userRole === "white" && turn === "white") || (userRole === "black" && turn === "black")) {
            pieces.forEach(piece => {
                const pieceColor = piece.getAttribute("data-color");
                if (pieceColor === userRole) {
                    piece.addEventListener("click", handleClick);
                }
            });
        }
    }

    updateDraggable();

    function handleClick(e) {
        const piece = e.target;
        const fromPosition = piece.parentNode.getAttribute("data-position");

        if (selectedPiece === piece) {
            clearHighlights();
            selectedPiece = null;
            return;
        }

        selectedPiece = piece;

        fetch(`/get_moves/${gameId}?from=${fromPosition}&turn=${turn}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                highlightMoves(data.moves);
            } else {
                console.error("Failed to get moves");
            }
        });
    }


    function highlightMoves(moves) {
        clearHighlights();

        moves.forEach(position => {
            const square = document.querySelector(`td[data-position="${position}"]`);
            const targetPiece = square.querySelector("img");
            if (targetPiece) {
                const targetPieceColor = targetPiece.getAttribute("data-color");

                if ((userRole === "white" && targetPieceColor === "black") || (userRole === "black" && targetPieceColor === "white")) {
                    const red = document.createElement("div");
                    red.classList.add("highlight-red");
                    square.appendChild(red);
                    square.addEventListener("click", movePiece);
                    highlightedMoves.push(square);
                }
                else {
                    const dot = document.createElement("div");
                    dot.classList.add("move-dot");
                    square.appendChild(dot);
                    square.addEventListener("click", movePiece);
                    highlightedMoves.push(square);
                }
            }
        });
    }

    function clearHighlights() {
        highlightedMoves.forEach(square => {
            square.removeEventListener("click", movePiece);
            const dot = square.querySelector(".move-dot");
            if (dot) dot.remove();
            const red = square.querySelector(".highlight-red")
            if (red) red.remove();
        });
        highlightedMoves = [];
    }

    function movePiece(e) {
        const targetSquare = e.currentTarget;
        const toPosition = targetSquare.getAttribute("data-position");
        const fromPosition = selectedPiece.parentNode.getAttribute("data-position");

        fetch(`/move_piece/${gameId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ from: fromPosition, to: toPosition, turn: turn }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                while (targetSquare.firstChild) {
                    targetSquare.removeChild(targetSquare.firstChild);
                }
                targetSquare.appendChild(selectedPiece);
                turn = data.new_turn;
                document.getElementById("turn").value = turn;
                clearHighlights();
                updateDraggable();
            } else {
                console.error("Invalid move");
            }
        });
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== "") {
            const cookies = document.cookie.split(";");
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + "=")) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
