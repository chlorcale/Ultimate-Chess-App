from pathlib import Path
import os
import sys


def get_runtime_root() -> Path:
    """
    Root directory for both:
    - normal Python execution
    - PyInstaller executable
    """

    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS)

    return Path(__file__).resolve().parents[1]


PROJECT_ROOT = get_runtime_root()


# ============================================================
# STOCKFISH
# ============================================================

STOCKFISH_PATH = (
    PROJECT_ROOT
    / "engine"
    / "bin"
    / "stockfish.exe"
)


# ============================================================
# CHROME
# ============================================================

CHROME_PROFILE_DIR = (
    Path(
        os.environ.get(
            "LOCALAPPDATA",
            str(Path.home()),
        )
    )
    / "ChessMoveMonitorChrome"
)


# ============================================================
# CDP
# ============================================================

CDP_HOST = "127.0.0.1"
CDP_PORT = 9222

CHROME_START_URL = "https://www.chess.com/"


# ============================================================
# POLLING
# ============================================================

MOVE_POLL_MS = 300


# ============================================================
# STOCKFISH SETTINGS
# ============================================================

ENGINE_TIME = 0.40
ENGINE_THREADS = 2
ENGINE_HASH_MB = 128


# ============================================================
# UI
# ============================================================

WINDOW_WIDTH = 470
WINDOW_HEIGHT = 390

WINDOW_TITLE = "Ultimate Stockfish Reader"