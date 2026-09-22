from __future__ import annotations

from browser.cdp import CDP


# ============================================================
# JAVASCRIPT
# ============================================================

READ_POSITION_JS = r"""
(() => {

    // ========================================================
    // BOARD / FEN
    // ========================================================

    const board =
        document.querySelector("wc-chess-board") ||
        document.querySelector("chess-board");

    const game = board?.game;

    let fen = "";

    if (
        game &&
        typeof game.getFEN === "function"
    ) {
        try {
            fen = game.getFEN() || "";
        } catch (_) {
            fen = "";
        }
    }


    // ========================================================
    // FIND MOVE LIST
    // ========================================================

    const root =
        document.querySelector("vertical-move-list") ||
        document.querySelector("wc-move-list") ||
        document.querySelector(".move-list-component") ||
        document.querySelector("[class*='move-list']");


    // ========================================================
    // CLEAN
    // ========================================================

    const clean = value => String(value || "")
        .replace(/\u00a0/g, " ")
        .replace(/\s+/g, " ")
        .trim();


    // ========================================================
    // METHOD 1:
    // data-san
    // ========================================================

    let moves = [];

    if (root) {

        const sanNodes =
            root.querySelectorAll("[data-san]");

        if (sanNodes.length) {

            moves = Array.from(
                sanNodes,
                node =>
                    clean(
                        node.getAttribute("data-san")
                    )
            ).filter(Boolean);
        }
    }


    // ========================================================
    // METHOD 2:
    // TEXT ELEMENTS
    // ========================================================

    if (!moves.length && root) {

        const nodes = root.querySelectorAll(
            ".move-text-component, " +
            ".move-text, " +
            ".node-highlight-content, " +
            "[class*='move-text'], " +
            "[class*='node-san']"
        );

        if (nodes.length) {

            moves = Array.from(
                nodes,
                node => clean(node.textContent)
            ).filter(Boolean);
        }
    }


    // ========================================================
    // METHOD 3:
    // PARSE MOVE LIST TEXT
    //
    // Example:
    // 1. e4 g6
    // 2. d4 Bg7
    // 3. e5 d6
    // ========================================================

    if (!moves.length && root) {

        const text = clean(
            root.innerText ||
            root.textContent ||
            ""
        );

        /*
         * Match complete move-number groups.
         *
         * 1. e4 e5
         * 2. Nf3 Nc6
         *
         */

        const matches = text.matchAll(
            /(\d+)\.\s*([^\s]+)(?:\s+([^\s]+))?/g
        );

        for (const match of matches) {

            const white = clean(match[2]);
            const black = clean(match[3]);

            if (white) {
                moves.push(white);
            }

            if (black) {
                moves.push(black);
            }
        }
    }


    // ========================================================
    // CLEAN DUPLICATES
    // ========================================================

    if (moves.length > 1) {

        const cleaned = [];

        for (const move of moves) {

            if (
                !cleaned.length ||
                cleaned[cleaned.length - 1] !== move
            ) {
                cleaned.push(move);
            }
        }

        moves = cleaned;
    }


    // ========================================================
    // RETURN
    // ========================================================

    return {
        url: location.href,
        fen,
        moves
    };

})()
"""


# ============================================================
# READER
# ============================================================

class ChessComReader:

    def __init__(
        self,
        cdp: CDP,
    ):
        self.cdp = cdp

        # Python-side cache
        self._last_url = ""
        self._last_fen = ""
        self._last_moves: list[str] = []


    # ========================================================
    # READ
    # ========================================================

    def read(self) -> dict:

        result = self.cdp.evaluate(
            READ_POSITION_JS
        )

        if not result:

            return {
                "url": "",
                "fen": "",
                "moves": [],
            }


        url = result.get(
            "url",
            ""
        )

        fen = result.get(
            "fen",
            ""
        )

        moves = result.get(
            "moves",
            []
        )


        if not isinstance(moves, list):

            moves = []


        moves = [
            str(move).strip()
            for move in moves
            if str(move).strip()
        ]


        # ----------------------------------------------------
        # Python-side cache
        # ----------------------------------------------------

        self._last_url = url
        self._last_fen = fen
        self._last_moves = moves


        return {
            "url": url,
            "fen": fen,
            "moves": moves,
        }


    # ========================================================
    # LAST DATA
    # ========================================================

    @property
    def last_url(self) -> str:
        return self._last_url


    @property
    def last_fen(self) -> str:
        return self._last_fen


    @property
    def last_moves(self) -> list[str]:
        return list(self._last_moves)