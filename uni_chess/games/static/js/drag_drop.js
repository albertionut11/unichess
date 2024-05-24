document.addEventListener("DOMContentLoaded", function() {
    const pieces = document.querySelectorAll("img[draggable='true']");
    const squares = document.querySelectorAll("td[data-position]");
    const gameId = document.getElementById("game_id").value;
    const userRole = document.getElementById("user_role").value;
    let turn = document.getElementById("turn").value;

    const socket = new WebSocket(`ws://${window.location.host}/ws/game/${gameId}/`);

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        const from = data.from;
        const to = data.to;
        turn = data.turn;
        document.getElementById("turn").value = turn; // Update the hidden input value
        document.getElementById("turn-display").innerText = turn; // Update the displayed turn

        const piece = document.querySelector(`td[data-position="${from}"] img`);
        const targetSquare = document.querySelector(`td[data-position="${to}"]`);

        while (targetSquare.firstChild) {
            targetSquare.removeChild(targetSquare.firstChild);
        }

        targetSquare.appendChild(piece);
        updateDraggable();
    };

    function updateDraggable() {
        pieces.forEach(piece => {
            piece.removeEventListener("dragstart", dragStart);
            piece.setAttribute("draggable", false);
        });

        if ((userRole === "white" && turn === "white") || (userRole === "black" && turn === "black")) {
            pieces.forEach(piece => {
                const pieceColor = piece.getAttribute("data-color");
                if (pieceColor === userRole) {
                    piece.addEventListener("dragstart", dragStart);
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
            e.preventDefault(); // Prevent dragging if piece color doesn't match user role
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

        while (targetSquare.firstChild) {
            targetSquare.removeChild(targetSquare.firstChild);
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
                targetSquare.appendChild(piece);
                turn = data.new_turn;
                document.getElementById("turn").value = turn;
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
