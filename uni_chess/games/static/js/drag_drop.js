document.addEventListener("DOMContentLoaded", function() {
    const pieces = document.querySelectorAll("img[draggable='true']");
    const squares = document.querySelectorAll("td[data-position]");
    const gameId = document.getElementById("game_id").value;

    pieces.forEach(piece => {
        piece.addEventListener("dragstart", dragStart);
    });

    squares.forEach(square => {
        square.addEventListener("dragover", dragOver);
        square.addEventListener("drop", drop);
    });

    function dragStart(e) {
        e.dataTransfer.setData("text/plain", e.target.id);
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

        // Ensure only one piece per square
        while (targetSquare.firstChild) {
            targetSquare.removeChild(targetSquare.firstChild);
        }

        fetch(`/move_piece/${gameId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ from: fromPosition, to: toPosition }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                targetSquare.appendChild(piece);
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
