# Ultimate Stockfish Reader & Analyzer

A lightweight Windows desktop application for reading a live Chess.com game, displaying the move list as plaintext, and analyzing the current position with the Stockfish chess engine.

The project is designed as a learning-oriented tool for studying Python, browser integration through Chrome DevTools Protocol (CDP), chess position handling, UCI engines, and compact desktop UI development.

> **Important:** This application is an analysis/reading tool. It does not automatically click or play moves on the Chess.com board.

## Features

- Live Chess.com move-list reader.
- Reads the current board position as FEN.
- Converts FEN into a `python-chess` board.
- Uses a local `stockfish.exe`.
- Displays the move list as plaintext.
- Automatically updates as new moves appear.
- Shows Stockfish's suggested next move.
- Shows engine evaluation and search depth.
- Separate **Stockfish** and **Best Move** panels.
- Highlights the latest move in the move list.
- **Always on top** toggle.
- Fixed-size compact desktop window.
- Scrollable move history with space for approximately seven move rows.
- Analysis modes:
  - **Trắng** — analyze White's turn only.
  - **Đen** — analyze Black's turn only.
  - **Cả hai** — analyze both sides.
- Modular codebase with separate browser, Chess.com reader, chess-state, engine, controller, and UI components.

## Screenshot

Add a screenshot after creating the repository:

```md
![Ultimate Stockfish Reader](assets/screenshot.png)
```

Suggested layout:

```text
assets/
└── screenshot.png
```

## Architecture

```text
                        main.py
                           |
                           v
                  AppController
             _________/    |    \_________
            /              |              \
           v               v               v
     ChessComReader   StockfishEngine   ChessReaderUI
           |               |               |
           v               v               v
        Chrome/CDP     stockfish.exe     Tkinter
           |
           v
        FEN + moves
           |
           +------------------+
                              |
                              v
                        python-chess
                              |
                              v
                           Position
                              |
                              v
                         Stockfish
                              |
                    +---------+---------+
                    |                   |
                    v                   v
                Best move          Evaluation
                    |                   |
                    +---------+---------+
                              |
                              v
                              UI
```

### Data flow

```text
Chess.com
   |
   | Chrome DevTools Protocol
   v
chesscom/reader.py
   |
   +---- move list ----------> UI
   |
   +---- FEN ----------------> python-chess
                                  |
                                  v
                             Stockfish
                                  |
                                  +---- best move
                                  +---- evaluation
                                  +---- depth
                                         |
                                         v
                                       UI
```

The engine path uses the current FEN directly instead of reconstructing the board from the full move history. This avoids depending on an internal Chess.com history API.

## Project Structure

```text
Ultimate Stockfish Reader_Analysing/
│
├── main.py
├── requirements.txt
├── README.md
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   └── ui.py
│
├── browser/
│   ├── __init__.py
│   ├── cdp.py
│   └── launcher.py
│
├── chesscom/
│   ├── __init__.py
│   └── reader.py
│
├── core/
│   ├── __init__.py
│   ├── chess_state.py
│   └── controller.py
│
└── engine/
    ├── __init__.py
    ├── stockfish.py
    └── bin/
        └── stockfish.exe
```

### Module responsibilities

| File | Responsibility |
|---|---|
| `main.py` | Application entry point |
| `app/config.py` | Runtime paths and configuration |
| `app/ui.py` | Tkinter desktop interface |
| `browser/cdp.py` | Chrome DevTools Protocol connection |
| `browser/launcher.py` | Start/debug Chrome and select a Chess.com tab |
| `chesscom/reader.py` | Read live Chess.com moves and FEN |
| `core/chess_state.py` | FEN handling and move-list formatting |
| `core/controller.py` | Coordinate reader, engine, and UI |
| `engine/stockfish.py` | Python wrapper around the UCI engine |
| `engine/bin/stockfish.exe` | Local Stockfish executable |

## Requirements

- Windows 10/11
- Python 3.12+ recommended
- Google Chrome
- A local Stockfish executable
- Internet access for Chess.com

Python packages:

```text
python-chess
websocket-client
```

Install them with:

```powershell
pip install -r requirements.txt
```

## Installing Stockfish

This project expects the executable at:

```text
engine/bin/stockfish.exe
```

Use the official Stockfish repository/releases:

- https://github.com/official-stockfish/Stockfish
- https://github.com/official-stockfish/Stockfish/releases

Place the Windows executable here:

```text
Ultimate Stockfish Reader_Analysing/
└── engine/
    └── bin/
        └── stockfish.exe
```

The application does not require `stockfish.exe` to be added to the Windows `PATH`.

### Verify the engine

From the repository root:

```powershell
.\engine\bin\stockfish.exe
```

Stockfish should start and wait for UCI commands.

Exit with:

```text
quit
```

You can also test the Python wrapper:

```powershell
python -c "from engine.stockfish import StockfishEngine; print('StockfishEngine import OK')"
```

## Running

From the repository root:

```powershell
python main.py
```

The application will:

1. Start or connect to a Chrome debugging session.
2. Locate a Chess.com game tab.
3. Read the current move list and board FEN.
4. Convert FEN into a `python-chess` position.
5. Run Stockfish analysis.
6. Update the UI as the game changes.

## Chrome / CDP

The browser integration uses Chrome DevTools Protocol (CDP) to evaluate JavaScript in the selected Chess.com tab.

The application uses a dedicated Chrome profile for debugging rather than reusing the normal Chrome profile.

Default debugging endpoint:

```text
127.0.0.1:9222
```

The project includes handling for Chrome's remote-debugging WebSocket origin checks.

> Chrome and Chess.com can change their browser behavior or internal page structure. The CDP and DOM-reading code may therefore need maintenance over time.

## UI

The UI is intentionally compact so it can stay beside a chess board.

```text
┌────────────────────────────────────────────┐
│ ♟ STOCKFISH READER          Stockfish ready│
│                                            │
│ ☑ Always on top   Phân tích: ○ Trắng ...   │
│                                            │
│ MOVE LIST                                  │
│ 1. e4 e5                                   │
│ 2. Nf3 Nc6                                 │
│ 3. Bb5 a6                                  │
│ 4. Ba4 Nf6                                 │
│ 5. O-O Be7                                 │
│ 6. Re1 b5                                  │
│ 7. Bb3 d6                                  │
│                                            │
├──────────────────────┬─────────────────────┤
│ STOCKFISH            │ BEST MOVE           │
│ Đánh giá: +0.34      │        Re1          │
│ Depth: 20            │    NƯỚC TIẾP THEO   │
└──────────────────────┴─────────────────────┘
```

The move-list area is scrollable while the bottom engine section stays visible.

## Analysis Modes

### Trắng

Only analyze positions where it is White's turn.

```text
White to move  -> Stockfish ON
Black to move  -> Stockfish OFF
```

### Đen

Only analyze positions where it is Black's turn.

```text
White to move  -> Stockfish OFF
Black to move  -> Stockfish ON
```

### Cả hai

Analyze both sides.

```text
White to move  -> Stockfish ON
Black to move  -> Stockfish ON
```

## Engine Output

The application displays:

- **Best move** — first move of the engine principal variation, shown in SAN.
- **Evaluation** — centipawn evaluation from White's point of view, or mate notation.
- **Depth** — search depth reported by the engine.

Example:

```text
BEST MOVE

exd6
NƯỚC TIẾP THEO
```

and:

```text
STOCKFISH

Đánh giá: -0.19
Depth: 20
```

## Configuration

Edit:

```text
app/config.py
```

For example:

```python
ENGINE_TIME = 0.40
ENGINE_THREADS = 2
ENGINE_HASH_MB = 128
```

These affect engine analysis speed and resource usage.

## Development Notes

The project intentionally keeps `main.py` small.

Its job is to create the UI, create the controller, and start the application. Feature-specific code belongs in its corresponding module.

This makes the project easier to debug and extend without turning `main.py` into a monolithic script.

## Troubleshooting

### `ModuleNotFoundError`

Example:

```text
ModuleNotFoundError: No module named 'chesscom'
```

Check that:

```text
chesscom/
├── __init__.py
└── reader.py
```

exists and run:

```powershell
python main.py
```

from the repository root.

### `StockfishEngine` import error

Check:

```text
engine/stockfish.py
```

contains:

```python
class StockfishEngine:
    ...
```

Then test:

```powershell
python -c "from engine.stockfish import StockfishEngine; print('OK')"
```

### Stockfish executable not found

Check:

```powershell
Test-Path .\engine\bin\stockfish.exe
```

Expected:

```text
True
```

### Chrome CDP 403

Check the Chrome launch settings in:

```text
browser/launcher.py
```

and the WebSocket connection options in:

```text
browser/cdp.py
```

The CDP client should use the appropriate origin handling for the Chrome instance.

### Move list is empty but Stockfish works

This indicates that FEN detection is working while the Chess.com move-list parser needs adjustment.

The most likely file to update is:

```text
chesscom/reader.py
```

### Several Chess.com tabs are open

The browser launcher prioritizes game-like Chess.com URLs and then attempts to select the focused tab. Multiple simultaneous game tabs may require stricter selection rules.

## Learning Goals

This project is also a practical learning exercise in:

- Python application architecture
- Object-oriented programming
- Tkinter
- ThreadPoolExecutor/background workers
- Chrome DevTools Protocol
- DOM inspection
- JavaScript execution from Python
- FEN notation
- SAN move notation
- `python-chess`
- UCI engine communication
- Stockfish integration
- State/version management
- Real-time polling
- Windows application development

## Roadmap

- [ ] Highlight the exact source and destination squares of the best move.
- [ ] Show `from -> to` coordinates beside SAN.
- [ ] Add a compact evaluation bar.
- [ ] Add configurable Stockfish depth/time.
- [ ] Add engine top-N candidate moves.
- [ ] Improve focused-tab selection.
- [ ] Add a settings panel.
- [ ] Add optional text-to-speech output.
- [ ] Save analyzed games as PGN.
- [ ] Add an evaluation graph.
- [ ] Add automated tests.
- [ ] Package the application for Windows.

## Third-Party Software

### Stockfish

https://github.com/official-stockfish/Stockfish

Stockfish is distributed under the GNU General Public License version 3 (GPLv3).

Review the upstream license before redistributing a build containing Stockfish:

https://github.com/official-stockfish/Stockfish/blob/master/Copying.txt

### python-chess

https://github.com/niklasf/python-chess

### websocket-client

https://github.com/websocket-client/websocket-client

## License

The license for this repository's own source code should be specified in a separate `LICENSE` file.

This project also uses third-party software with separate licenses. In particular, Stockfish is GPLv3-licensed.

## Disclaimer

This project is provided for educational and research purposes.

It is intended to help developers learn about chess software, browser integration, engine communication, and desktop application development. Users are responsible for following the terms and rules of the chess services they use with the application.
