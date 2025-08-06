# UniChess

UniChess is a web-based chess application built using Django and Python. It allows players to engage in games against the Stockfish engine through a dynamic web interface. The project is modular, lightweight, and focuses on both backend architecture and frontend interactivity.

## Features

### Chess Gameplay

- Play chess against other players in real-time.
- Move validation and board updates using asynchronous communication.
- Automatic response from Stockfish with best move computation.
- Game state persistence using Django models and SQLite.

### Engine Integration

- Communicates with Stockfish via the UCI (Universal Chess Interface) protocol.
- The Stockfish binary is bundled locally under the `stockfish/` directory.
- Commands and evaluations are handled by Python subprocesses.

### Web Interface

- Chessboard rendered using HTML5/CSS with static piece images.
- JavaScript handles move input and sends data to the backend for processing.
- Responsive UI layout with static asset management under `static/`.

### Django Backend

- Modular app structure (`website`) containing routing, views, and logic.
- SQLite database by default (can be extended to PostgreSQL).
- Simple routing with clear URL-to-view mapping (`urls.py`).

## Technologies Used

- **Language:** Python 3
- **Framework:** Django
- **Engine:** Stockfish (UCI protocol)
- **Frontend:** HTML, CSS, JavaScript
- **Database:** SQLite
- **Other Tools:** Python-dotenv, Subprocess, Django Templating

## Project Structure

```
unichess/
├── main.py                    # Entry point
├── .env                       # Environment config (e.g. path to Stockfish)
├── uni_chess/
│   ├── manage.py              # Django admin script
│   ├── db.sqlite3             # Default database
│   ├── templates/             # HTML templates
│   ├── staticfiles/           # CSS, JS, image assets
│   ├── stockfish/             # Stockfish engine binary
│   └── website/
│       ├── views.py           # Request handlers and game logic
│       ├── urls.py            # URL routing
│       └── static/            # Local static assets (chess pieces, board)
├── .venv/                     # Virtual environment (not included in repo)
└── requirements.txt           # Python dependencies
```

## Setup Instructions

### Prerequisites

- Python 3.10+
- pip (Python package manager)
- Stockfish binary placed under `stockfish/` directory
- Virtual environment recommended

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/unichess.git
   cd unichess
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate      # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```bash
   python uni_chess/manage.py migrate
   ```

5. Run the development server:
   ```bash
   python uni_chess/manage.py runserver
   ```

6. Open your browser at:
   ```
   http://127.0.0.1:8000/
   ```

## Environment Variables

Add a `.env` file in the root directory with the following (example):
```
STOCKFISH_PATH=./uni_chess/stockfish/stockfish
```

## Example Usage

- Load the home page to display the chessboard.
- Move a piece via the web interface.
- The backend validates and responds with the Stockfish move.
- The board updates automatically.

## License

This project is licensed under the MIT License.

## Acknowledgements

- [Stockfish](https://stockfishchess.org/) — open-source chess engine
- [Django](https://www.djangoproject.com/) — Python web framework
- All static piece assets are assumed to be open-source or self-created.
