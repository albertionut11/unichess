let pieces;
let whiteTimerElement;
let blackTimerElement;

document.addEventListener("DOMContentLoaded", function() {

    const isActive = document.getElementById("is_active").value === "True";
    let started = document.getElementById("started").value === "True";
    if (!isActive) {
        document.getElementById("endgame-message").style.display = "block";
        return;
    }

    pieces = document.querySelectorAll("img[draggable='true']");
    const squares = document.querySelectorAll("td[data-position]");
    const gameId = document.getElementById("game_id").value;
    const userRole = document.getElementById("user_role").value;
    let turn = document.getElementById("turn").value;
    const increment = parseInt(document.getElementById("time_increment").value);
    let selectedPiece = null;
    let promotionPiece = null;
    let highlightedMoves = [];

     if (!started && userRole === "white") {
        const startGameButton = document.getElementById("start-game-button");
        startGameButton.addEventListener("click", startGame);
    }

    const socket = new WebSocket(`ws://${window.location.host}/ws/game/${gameId}/`);

    whiteTimerElement = document.getElementById("white-timer");
    blackTimerElement = document.getElementById("black-timer");

    socket.onmessage = function(e) {
        const data = JSON.parse(e.data);
        console.log("DATA SENT:", data);
        const messageType = data.type;

        if(messageType === 'start_game'){
            document.getElementById("started").value = "True";
            started = true;
            startTimer(turn);
            updateDraggable();
        }
        else if (messageType === 'end_game') {
            displayEndgameMessage(data.message);
        }
        else if (messageType === 'offer_draw') {
            const offerDrawButton = document.getElementById("offer-draw-button");
            turn = data.turn;
            console.log(userRole);
            console.log(turn);
            if (userRole !== turn){
                offerDrawButton.textContent = "Accept Draw";
            }
        }
        else if (messageType === 'cancel_draw') {
            const offerDrawButton = document.getElementById("offer-draw-button");
            offerDrawButton.textContent = "Offer Draw";
        }
        else if (messageType === 'accept_draw') {
            handleDrawResponse();
        }
        else {
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

            if (data.promotion) {
                const promotionColor = turn === "white" ? "b" : "w";
                console.log('Promotion to', promotionColor + data.promotion);
                promotePawn(to, promotionColor + data.promotion, false);
            }

            if (data.checkmate == 'true') {
                console.log('here');
                console.log(data.checkmate);
                const winner = turn === "white" ? "Black" : "White";
                displayEndgameMessage(`Checkmate! ${winner} wins!`);
            }
            else if (data.checkmate == 'stalemate'){
                displayEndgameMessage("Stalemate!")
            }

            updateDraggable();

            // Update timers
            whiteTime = data.white_time_remaining;
            blackTime = data.black_time_remaining;
            whiteTimerElement.textContent = formatTime(whiteTime);
            blackTimerElement.textContent = formatTime(blackTime);
            startTimer(data.turn);
        }
    };

    function updateDraggable() {
        if (!started) return;

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
            body: JSON.stringify({
                from: fromPosition,
                to: toPosition,
                turn: turn,
                promotion: promotion,
                white_time_remaining: turn === 'white' ? whiteTime + increment : whiteTime,
                black_time_remaining: turn === 'black' ? blackTime + increment : blackTime
            }),
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {

                document.getElementById("white_time").value = data.white_time_remaining;
                document.getElementById("black_time").value = data.black_time_remaining;

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

                if (promotion) {
                    promotePawn(toPosition, userRole[0] + promotion, true);
                }
                updateDraggable();
            } else {
                console.error("Invalid move");
            }
        });
    }

    function isPawnPromotion(piece, toPosition) {
        const pieceType = piece.getAttribute("data-piece");
        const toRow = toPosition[0];
        return pieceType === "P" && ((userRole === "white" && toRow === "8") || (userRole === "black" && toRow === "1"));
    }

    function showPromotionOptions(fromPosition, toPosition, targetSquare) {
    const promotionChoices = ["Q", "R", "B", "N"];
    const promotionContainer = document.getElementById("promotion-container");
    promotionContainer.innerHTML = "";

    // Create a backdrop for the popup
    const backdrop = document.createElement("div");
    backdrop.id = "promotion-backdrop";

    // Create a container for the buttons
    const popupContainer = document.createElement("div");
    popupContainer.id = "promotion-popup";

    promotionChoices.forEach(choice => {
        const btn = document.createElement("button");
        btn.innerText = choice;
        btn.className = "promotion-button";

        btn.addEventListener("click", () => {
            promotionPiece = choice;
            promotionContainer.innerHTML = "";
            document.body.removeChild(backdrop);
            makeMove(fromPosition, toPosition, targetSquare, choice);
        });

        popupContainer.appendChild(btn);
    });

    backdrop.appendChild(popupContainer);
    document.body.appendChild(backdrop);
}


    function performCastlingMove(castling, from) {
        let rookFrom = from[0] + "h";
        let kingTo = from[0] + "g";
        let rookTo = from[0] + "f";

        if (castling === "Q") {
            rookFrom = from[0] + "a";
            kingTo = from[0] + "c";
            rookTo = from[0] + "d";
        }

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

    function displayEndgameMessage(message) {
        const messageDiv = document.getElementById("endgame-message");
        messageDiv.innerText = message;
        messageDiv.classList.add("endgame-message");
        messageDiv.style.display = "block";

        const turnDisplay = document.querySelector(".info-box");
        if (turnDisplay) {
            turnDisplay.remove();
        }

        pieces.forEach(piece => {
            piece.removeEventListener("dragstart", dragStart);
            piece.removeEventListener("click", handleClick);
            piece.setAttribute("draggable", false);
        });
        if (document.getElementById("resign-button")){
            document.getElementById("resign-button").disabled = true;
        }
        if (document.getElementById("offer-draw-button")){
            document.getElementById("offer-draw-button").disabled = true;
        }

        showAnalyseButton();

        clearInterval(whiteInterval);
        clearInterval(blackInterval);

        const isActiveElement = document.getElementById("is_active");
        if (isActiveElement) {
            isActiveElement.value = "False";
        }
    }
    window.displayEndgameMessage = displayEndgameMessage;

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

    window.getCookie = getCookie;

    function promotePawn(position, promotion, draggable) {
        const targetSquare = document.querySelector(`td[data-position="${position}"]`);
        const promotionPiece = document.createElement("img");
        promotionPiece.src = `/static/chess/pieces/${promotion}.svg`;
        promotionPiece.setAttribute("data-piece", promotion.slice(1));

        if (promotion[0] === "w"){
            promotionPiece.setAttribute("data-color", "white");
        }
        else{
            promotionPiece.setAttribute("data-color", "black");
        }

        promotionPiece.setAttribute("id", position);
        promotionPiece.setAttribute("draggable", draggable);
        resetSquare(position);
        targetSquare.appendChild(promotionPiece);

    }

    // Ensure the formatTime and startTimer functions are accessible here
    window.formatTime = function(time) {
        const minutes = Math.floor(time / 60);
        const seconds = time % 60;
        return `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    };

    window.startTimer = function(turn) {
        clearInterval(whiteInterval);
        clearInterval(blackInterval);

        if (turn === 'white') {
            whiteInterval = setInterval(() => updateTimer('white'), 1000);
        } else {
            blackInterval = setInterval(() => updateTimer('black'), 1000);
        }
    };

    document.getElementById("resign-button").addEventListener("click", function() {
        if (confirm("Are you sure you want to resign?")) {
            fetch(`/resign/${gameId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "ok") {
                    const message = `${data.loser} resigns! ${data.winner} wins!`;
                    displayEndgameMessage(message);

                } else {
                    console.error("Failed to resign");
                }
            });
        }
    });

    document.getElementById("offer-draw-button").addEventListener("click", function() {
        const offerDrawButton = document.getElementById("offer-draw-button");
        if (offerDrawButton.textContent === "Offer Draw") {
            fetch(`/offer_draw/${gameId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                },
                body: JSON.stringify ({
                    turn: userRole
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "ok") {
                    offerDrawButton.textContent = "Cancel Draw";
                } else {
                    console.error("Failed to offer draw");
                }
            });
        } else if (offerDrawButton.textContent === "Cancel Draw"){
            fetch(`/cancel_draw/${gameId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "ok") {
                    offerDrawButton.textContent = "Offer Draw";
                } else {
                    console.error("Failed to cancel draw offer");
                }
            });
        }
        else {
            fetch(`/accept_draw/${gameId}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken")
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "ok") {
                    handleDrawResponse();
                } else {
                    console.error("Failed to cancel draw offer");
                }
            });
        }
    });

    function handleDrawResponse() {
        displayEndgameMessage("Game drawn!");
        disableInteraction();
    }

    function disableInteraction() {
        pieces.forEach(piece => {
            piece.removeEventListener("dragstart", dragStart);
            piece.removeEventListener("click", handleClick);
            piece.setAttribute("draggable", false);
        });
        if (document.getElementById("resign-button")){
            document.getElementById("resign-button").disabled = true;
        }
        if (document.getElementById("offer-draw-button")){
            document.getElementById("offer-draw-button").disabled = true;
        }
        clearInterval(whiteInterval);
        clearInterval(blackInterval);
    }

        function showAnalyseButton() {
        const timersElement = document.getElementById("timers");

        const resignButton = document.getElementById("resign-button");
        const offerDrawButton = document.getElementById("offer-draw-button");
        if (resignButton) {
            timersElement.removeChild(resignButton);
        }
        if (offerDrawButton) {
            timersElement.removeChild(offerDrawButton);
        }
        console.log('showAnalyseButton');

        if (!document.getElementById("analyse-button")){
            const analyseButton = document.createElement("a");
            analyseButton.href = `/analyse/${gameId}`;
            analyseButton.className = "game-button";
            analyseButton.textContent = "Analyse Game";
            analyseButton.id = "analyse-button"

        const blackTimerElement = document.getElementById("black-timer");
        timersElement.insertBefore(analyseButton, blackTimerElement);
        }
    }

     function startGame() {
        const gameId = document.getElementById("game_id").value;
        fetch(`/start_game/${gameId}`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "ok") {
                document.getElementById("started").value = "True";

                const turnDisplayElement = document.createElement("p");
                turnDisplayElement.className = "info-box";
                turnDisplayElement.innerHTML = 'Turn: <span id="turn-display">white</span>';

                const startGameButton = document.getElementById("start-game-button");
                startGameButton.parentNode.insertBefore(turnDisplayElement, startGameButton);

                startGameButton.remove();

                started = true;
                startTimer(turn);
                updateDraggable();
            } else {
                console.error("Failed to start the game");
            }
        });
    }
});
