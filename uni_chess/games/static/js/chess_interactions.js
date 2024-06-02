let pieces;

document.addEventListener("DOMContentLoaded", function() {
    pieces = document.querySelectorAll("img[draggable='true']");
    const squares = document.querySelectorAll("td[data-position]");
    const gameId = document.getElementById("game_id").value;
    const userRole = document.getElementById("user_role").value;
    let turn = document.getElementById("turn").value;
    let selectedPiece = null;
    let promotionPiece = null;
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

        if (data.castling) {
            performCastlingMove(data.castling, from);
        } else {
            resetSquare(from);
            resetSquare(to);
            targetSquare.appendChild(piece);
        }

        updateDraggable();
        console.log("DATA:" ,data);

        if (data.promotion) {
            const promotionColor = turn === "white" ? "b" : "w"
            console.log('Promotion to', promotionColor + data.promotion);
            promotePawn(to, promotionColor + data.promotion);
        }

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
            selectedPiece = e.target;
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

        if (!targetSquare || !targetSquare.hasAttribute("data-position")) {
            console.error("Invalid target square");
            return;
        }

        const fromPosition = piece.parentNode.getAttribute("data-position");
        const toPosition = targetSquare.getAttribute("data-position");

        if (fromPosition === toPosition) {
            console.log("Invalid move: Cannot move piece to the same position.");
            return;
        }

         // Check for pawn promotion situation
        if (isPawnPromotion(piece, toPosition)) {
            showPromotionOptions(fromPosition, toPosition, targetSquare);
        } else {
            makeMove(fromPosition, toPosition, targetSquare);
        }
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
            console.log("Position", position, fromPosition);
            if (position === fromPosition) return;
            const square = document.querySelector(`td[data-position="${position}"]`);
            const targetPiece = square.querySelector("img");

            console.log(square, targetPiece);

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
        if (isPawnPromotion(selectedPiece, toPosition)) {
            showPromotionOptions(fromPosition, toPosition, targetSquare);
        } else {
            makeMove(fromPosition, toPosition, targetSquare);
        }
    }


    function makeMove(fromPosition, toPosition, targetSquare, promotion = null) {
        fetch(`/move_piece/${gameId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken"),
            },
            body: JSON.stringify({ from: fromPosition, to: toPosition, turn: turn, promotion: promotion }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                if (data.enPassant) {
                    const fromRow = fromPosition[0];
                    const capturedPosition = fromRow + toPosition[1];
                    resetSquare(capturedPosition);
                }

                resetSquare(fromPosition);
                resetSquare(toPosition);

                if (targetSquare) {
                    targetSquare.appendChild(selectedPiece);
                }

                if (data.winner) {
                    console.log("Winner:", data.winner);
                }

                turn = data.new_turn;
                document.getElementById("turn").value = turn;
                clearHighlights();
                updateDraggable();

                // Check if promotion occurred and handle it
                if (promotion) {
                    promotePawn(toPosition, userRole[0] + promotion); // e.g., "wQ" for white Queen
                }
            } else {
                console.error("Invalid move");
            }
        });
    }

    function isPawnPromotion(piece, toPosition) {
        // const pieceSrc = piece.getAttribute("src"); // cheap workaround around wrong data-piece data for bishop promotion
        // const pieceTypeSrc = pieceSrc.slice(-5)[0];
        // console.log(pieceTypeSrc);
        const pieceType = piece.getAttribute("data-piece");
        const toRow = toPosition[0];
        return pieceType === "P" && ((userRole === "white" && toRow === "8") || (userRole === "black" && toRow === "1"));
    }

    function showPromotionOptions(fromPosition, toPosition, targetSquare) {
        const promotionChoices = ["Q", "R", "B", "N"];
        const promotionContainer = document.getElementById("promotion-container");
        promotionContainer.innerHTML = "";
        promotionChoices.forEach(choice => {
            const btn = document.createElement("button");
            btn.innerText = choice;
            btn.addEventListener("click", () => {
                promotionPiece = choice;
                promotionContainer.innerHTML = "";
                makeMove(fromPosition, toPosition, targetSquare, choice);
            });
            promotionContainer.appendChild(btn);
        });
    }

     function performCastlingMove(castling, from) {
         // const kingColor = turn === "white" ? "b" : "w";

         console.log("from", from);
         console.log("castling", castling);
         // kingside castle
         let rookFrom = from[0] + "h";
         let kingTo = from[0] + "g";
         let rookTo = from[0] + "f";

         if (castling === "Q") {
             rookFrom = from[0] + "a";
             kingTo = from[0] + "c";
             rookTo = from[0] + "d";
         }

         console.log("rookFrom", rookFrom);
         console.log("kingTo", kingTo);
         console.log("rookTo", rookTo);

        const king = document.querySelector(`td[data-position="${from}"] img`);
        const rook = document.querySelector(`td[data-position="${rookFrom}"] img`);

        const kingTargetSquare = document.querySelector(`td[data-position="${kingTo}"]`);
        const rookTargetSquare = document.querySelector(`td[data-position="${rookTo}"]`);

        resetSquare(from);
        resetSquare(rookFrom);

        kingTargetSquare.appendChild(king);
        rookTargetSquare.appendChild(rook);
        clearHighlights();
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

    function promotePawn(position, promotion) {
        const targetSquare = document.querySelector(`td[data-position="${position}"]`);
        const promotionPiece = document.createElement("img");
        promotionPiece.src = `/static/chess/pieces/${promotion}.svg`;
        promotionPiece.setAttribute("data-piece", promotion.slice(1)); // Only the piece type (e.g., "Q", "R", etc.)
        promotionPiece.setAttribute("data-color", promotion[0]); // "w" for white, "b" for black
        promotionPiece.setAttribute("draggable", true); // Make it draggable
        resetSquare(position);
        targetSquare.appendChild(promotionPiece);

        // Add event listeners to the new promoted piece
        promotionPiece.addEventListener("dragstart", dragStart);
        promotionPiece.addEventListener("click", handleClick);
    }
});
