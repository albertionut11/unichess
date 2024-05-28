document.addEventListener("DOMContentLoaded", function() {
    const pieces = document.querySelectorAll("img[draggable='true']");
    const squares = document.querySelectorAll("td[data-position]");
    const gameId = document.getElementById("game_id").value;
    const userRole = document.getElementById("user_role").value;
    let turn = document.getElementById("turn").value;
    let selectedPiece = null;
    let highlightedMoves = [];

    const socket = new WebSocket(`ws://${window.location.host}/ws/game/${gameId}/`);

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const from = data.from;
        const to = data.to;
        turn = data.turn;
        const enPassant = data.enPassant || false;

        document.getElementById("turn").value = turn;
        document.getElementById("turn-display").innerText = turn;

        const piece = document.querySelector(`td[data-position="${from}"] img`);
        const targetSquare = document.querySelector(`td[data-position="${to}"]`);

        if (enPassant) {
            const fromRow = from[0];
            const capturedPosition = fromRow + to[1];
            resetSquare(capturedPosition);
        }

        resetSquare(from);
        resetSquare(to);
        targetSquare.appendChild(piece);
        updateDraggable();
        console.log("DATA:" ,data);

        if (data.checkmate) {
            console.log('onMessage here');
            displayCheckmateMessage(turn);
        }
    };

    function updateDraggable() {
        pieces.forEach(piece => {
            piece.removeEventListener("dragstart", dragStart);
            piece.removeEventListener("click", handleClick);
            piece.setAttribute("draggable", false);
        });

        if ((userRole === "white" && turn === "white") || (userRole === "black" && turn === "black")) {
            pieces.forEach(piece => {
                const pieceColor = piece.getAttribute("data-color");
                if (pieceColor === userRole) {
                    piece.addEventListener("dragstart", dragStart);
                    piece.addEventListener("click", handleClick);
                    piece.setAttribute("draggable", true);
                }
            });

            squares.forEach(square => {
                square.addEventListener("dragover", dragOver);
                square.addEventListener("drop", drop);
            });
        } else {
            squares.forEach(square => {
                square.removeEventListener("dragover", dragOver);
                square.removeEventListener("drop", drop);
            });
        }
    }

    updateDraggable();

    function dragStart(e) {
        const pieceColor = e.target.getAttribute("data-color");
        if (pieceColor !== userRole) {
            e.preventDefault();
        } else {
            e.dataTransfer.setData("text/plain", e.target.id);
        }
    }

    function dragOver(e) {
        e.preventDefault();
    }

    function drop(e) {
        e.preventDefault();
        const id = e.dataTransfer.getData("text/plain");
        const piece = document.getElementById(id);

        let targetSquare = e.target;
        while (targetSquare && !targetSquare.hasAttribute("data-position")) {
            targetSquare = targetSquare.parentNode;
        }

        const fromPosition = piece.parentNode.getAttribute("data-position");
        const toPosition = targetSquare.getAttribute("data-position");

        if (fromPosition === toPosition) {
            console.log("Invalid move: Cannot move piece to the same position.");
            return;
        }

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
                if (data.enPassant) {
                    const fromRow = fromPosition[0];
                    const capturedPosition = fromRow + toPosition[1];
                    resetSquare(capturedPosition);
                }
                if (data.winner){
                    console.log("Winner:", data.winner)
                }

                resetSquare(fromPosition);
                resetSquare(toPosition);
                targetSquare.appendChild(piece);
                turn = data.new_turn;
                document.getElementById("turn").value = turn;
                clearHighlights();
                updateDraggable();
            } else {
                console.error("Invalid move");
            }
        });
    }

    function handleClick(e) {
        const piece = e.target;
        const fromPosition = piece.parentNode.getAttribute("data-position");

        if (selectedPiece === piece) {
            clearHighlights();
            selectedPiece = null;
            return;
        }

        clearHighlights();
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
                highlightMoves(data.moves, fromPosition);
            } else {
                console.error("Failed to get moves");
            }
        });
    }

    function highlightMoves(moves, fromPosition) {
        clearHighlights();

        moves.forEach(position => {
            if (position === fromPosition) return;
            const square = document.querySelector(`td[data-position="${position}"]`);
            const targetPiece = square.querySelector("img");

            if (!targetPiece) {
                const dot = document.createElement("div");
                dot.classList.add("move-dot");
                square.appendChild(dot);
                square.addEventListener("click", movePiece);
                highlightedMoves.push(square);
            } else {
                const targetPieceColor = targetPiece.getAttribute("data-color");

                if ((targetPieceColor === "black" && userRole === "white") || (targetPieceColor === "white" && userRole === "black")) {
                    const red = document.createElement("div");
                    red.classList.add("highlight-red");
                    square.appendChild(red);
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
            const red = square.querySelector(".highlight-red");
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
                if (data.enPassant) {
                    const fromRow = fromPosition[0];
                    const capturedPosition = fromRow + toPosition[1];
                    resetSquare(capturedPosition);
                }
                if (data.winner){
                    console.log("Winner:", data.winner)
                }

                resetSquare(fromPosition);
                resetSquare(toPosition);
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

    function resetSquare(position) {
        const square = document.querySelector(`td[data-position="${position}"]`);
        while (square.firstChild) {
            square.removeChild(square.firstChild);
        }
    }

    function displayCheckmateMessage(turn) {
        const winner = turn === "white" ? "Black" : "White";
        const messageDiv = document.getElementById("checkmate-message");
        messageDiv.innerText = `Checkmate: ${winner} wins!`;
        messageDiv.classList.add("checkmate-message");
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
