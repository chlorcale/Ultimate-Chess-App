from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

from app.config import (
    CDP_HOST,
    CDP_PORT,
    CHROME_PROFILE_DIR,
    CHROME_START_URL,
)

from browser.cdp import (
    CDP,
    get_targets,
)


# ============================================================
# FIND CHROME
# ============================================================

def find_chrome() -> str | None:

    candidates = [
        Path(
            os.environ.get(
                "PROGRAMFILES",
                ""
            )
        )
        / "Google/Chrome/Application/chrome.exe",

        Path(
            os.environ.get(
                "PROGRAMFILES(X86)",
                ""
            )
        )
        / "Google/Chrome/Application/chrome.exe",

        Path(
            os.environ.get(
                "LOCALAPPDATA",
                ""
            )
        )
        / "Google/Chrome/Application/chrome.exe",
    ]

    for path in candidates:

        if path.exists():

            return str(path)

    return None


# ============================================================
# ENSURE DEBUG CHROME
# ============================================================

def ensure_debug_chrome() -> None:

    targets = get_targets(
        CDP_HOST,
        CDP_PORT,
    )

    if targets:

        return

    chrome = find_chrome()

    if not chrome:

        raise RuntimeError(
            "Không tìm thấy Google Chrome."
        )

    CHROME_PROFILE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "[CHROME] Đang mở debug Chrome..."
    )

    subprocess.Popen(
        [
            chrome,

            f"--remote-debugging-port={CDP_PORT}",

            # Giới hạn origin thay vì *
            (
                "--remote-allow-origins="
                f"http://{CDP_HOST}:{CDP_PORT}"
            ),

            f"--user-data-dir={CHROME_PROFILE_DIR}",

            CHROME_START_URL,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    for _ in range(30):

        time.sleep(0.5)

        targets = get_targets(
            CDP_HOST,
            CDP_PORT,
        )

        if targets:

            print(
                "[CHROME] CDP đã sẵn sàng."
            )

            return

    raise RuntimeError(
        "Chrome không mở được CDP."
    )


# ============================================================
# PICK CHESS.COM TAB
# ============================================================

def find_chess_tab() -> dict | None:

    targets = get_targets(
        CDP_HOST,
        CDP_PORT,
    )

    chess_tabs = []

    for target in targets:

        if target.get("type") != "page":
            continue

        url = target.get(
            "url",
            "",
        )

        if "chess.com" not in url.lower():
            continue

        chess_tabs.append(target)

    if not chess_tabs:

        return None


    # --------------------------------------------------------
    # Ưu tiên các tab thực sự đang chơi
    # --------------------------------------------------------

    game_tabs = []

    for target in chess_tabs:

        url = target.get(
            "url",
            "",
        ).lower()

        if (
            "/play/" in url
            or "/game/" in url
        ):

            game_tabs.append(target)

    candidates = (
        game_tabs
        if game_tabs
        else chess_tabs
    )


    # --------------------------------------------------------
    # Chỉ có một tab
    # --------------------------------------------------------

    if len(candidates) == 1:

        return candidates[0]


    # --------------------------------------------------------
    # Nhiều tab -> tìm tab focus
    # --------------------------------------------------------

    for target in candidates:

        ws_url = target.get(
            "webSocketDebuggerUrl"
        )

        if not ws_url:
            continue

        try:

            cdp = CDP(ws_url)

            value = cdp.evaluate(
                """
                ({
                    focused: document.hasFocus(),
                    url: location.href
                })
                """
            )

            cdp.close()

            if (
                value
                and value.get("focused")
            ):

                return target

        except Exception:

            continue


    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    return candidates[0]