from pathlib import Path
import os


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]

STOCKFISH_PATH = (
    PROJECT_ROOT
    / "engine"
    / "bin"
    / "stockfish.exe"
)

CHROME_PROFILE_DIR = (
    Path(
        os.environ.get(
            "LOCALAPPDATA",
            str(Path.home())
        )
    )
    / "ChessMoveMonitorChrome"
)


# ============================================================
# CHROME / CDP
# ============================================================

CDP_HOST = "127.0.0.1"
CDP_PORT = 9222

CHROME_START_URL = "https://www.chess.com/"


# ============================================================
# POLLING
# ============================================================

MOVE_POLL_MS = 300


# ============================================================
# STOCKFISH
# ============================================================

ENGINE_TIME = 0.40
ENGINE_THREADS = 2
ENGINE_HASH_MB = 128


# ============================================================
# UI
# ============================================================

WINDOW_WIDTH = 430
WINDOW_HEIGHT = 360

WINDOW_TITLE = "Ultimate Stockfish Reader"