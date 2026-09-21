from __future__ import annotations

from browser.cdp import CDP


READ_POSITION_JS = r"""
(() => {

    // ========================================================
    // FIND MOVE LIST ROOT
    // ========================================================

    const rootSelectors = [
        "vertical-move-list",
        "wc-move-list",
        ".move-list-component",
        "[class*='move-list']"
    ];

    let root = null;

    for (const selector of rootSelectors) {

        const el = document.querySelector(selector);

        if (el) {
            root = el;
            break;
        }
    }


    // ========================================================
    // BOARD / GAME
    // ========================================================

    const board =
        document.querySelector("wc-chess-board") ||
        document.querySelector("chess-board");

    const game = board?.game || null;


    // ========================================================
    // FEN
    // ========================================================

    let fen = "";

    if (
        game &&
        typeof game.getFEN === "function"
    ) {

        try {
            fen = game.getFEN();
        } catch (e) {
            console.warn(
                "[Reader] getFEN failed:",
                e
            );
        }
    }


    // ========================================================
    // MOVE PARSER
    // ========================================================

    function looksLikeSAN(value) {

        if (!value) {
            return false;
        }

        const text = String(value).trim();

        return /^(?:O-O-O|O-O|[KQRBN]?[a-h]?[1-8]?x?[a-h][1-8](?:=[QRBN])?[+#]?)$/.test(
            text
        );
    }


    function cleanMove(value) {

        if (!value) {
            return "";
        }

        let text = String(value)
            .replace(/\u00a0/g, " ")
            .replace(/\s+/g, " ")
            .trim();

        // Remove move number
        text = text.replace(
            /^\d+\.(?:\.\.)?\s*/,
            ""
        );

        // Remove common annotation symbols
        text = text.replace(
            /[!?]+$/,
            ""
        );

        return text;
    }


    // ========================================================
    // METHOD A:
    // data-san / data-uci
    // ========================================================

    function readDataAttributes(container) {

        if (!container) {
            return [];
        }

        const selectors = [
            "[data-san]",
            "[data-uci]"
        ];

        for (const selector of selectors) {

            const nodes = [
                ...container.querySelectorAll(selector)
            ];

            if (!nodes.length) {
                continue;
            }

            const result = [];

            for (const node of nodes) {

                let value =
                    node.dataset?.san ||
                    node.dataset?.uci ||
                    "";

                value = cleanMove(value);

                if (!value) {
                    continue;
                }

                if (
                    !result.length ||
                    result[result.length - 1] !== value
                ) {
                    result.push(value);
                }
            }

            if (result.length) {
                return result;
            }
        }

        return [];
    }


    // ========================================================
    // METHOD B:
    // move text elements
    // ========================================================

    function readMoveElements(container) {

        if (!container) {
            return [];
        }

        const selectors = [
            ".move-text-component",
            ".move-text",
            ".node-highlight-content",
            "[class*='move-text']",
            "[class*='node-san']"
        ];

        for (const selector of selectors) {

            const nodes = [
                ...container.querySelectorAll(selector)
            ];

            if (!nodes.length) {
                continue;
            }

            const result = [];

            for (const node of nodes) {

                let value =
                    node.textContent || "";

                value = cleanMove(value);

                if (!value) {
                    continue;
                }

                if (!result.length ||
                    result[result.length - 1] !== value) {

                    result.push(value);
                }
            }

            if (result.length) {
                return result;
            }
        }

        return [];
    }


    // ========================================================
    // METHOD C:
    // PARSE INNER TEXT
    //
    // Example:
    //
    // 1. e4 g6
    // 2. d4 Bg7
    // 3. e5 d6
    // ========================================================

    function parseMoveText(text) {

        if (!text) {
            return [];
        }

        const result = [];

        const lines = String(text)
            .replace(/\r/g, "")
            .split("\n")
            .map(line =>
                line
                    .replace(/\u00a0/g, " ")
                    .replace(/\s+/g, " ")
                    .trim()
            )
            .filter(Boolean);


        // ----------------------------------------------------
        // First try line-by-line
        // ----------------------------------------------------

        for (const line of lines) {

            const match = line.match(
                /^\s*(\d+)\.\s+([^\s]+)(?:\s+([^\s]+))?\s*$/
            );

            if (!match) {
                continue;
            }

            const white =
                cleanMove(match[2]);

            const black =
                cleanMove(match[3] || "");


            if (
                looksLikeSAN(white)
            ) {
                result.push(white);
            }

            if (
                black &&
                looksLikeSAN(black)
            ) {
                result.push(black);
            }
        }


        if (result.length) {
            return result;
        }


        // ----------------------------------------------------
        // Second try:
        // "1. e4 g6 2. d4 Bg7 ..."
        // all on one line
        // ----------------------------------------------------

        const normalized = String(text)
            .replace(/\u00a0/g, " ")
            .replace(/\s+/g, " ")
            .trim();


        const pattern =
            /(\d+)\.\s*([A-Za-z0-9+#=x-]+)(?:\s+([A-Za-z0-9+#=x-]+))?/g;


        let match;


        while (
            (match = pattern.exec(normalized)) !== null
        ) {

            const white =
                cleanMove(match[2]);

            const black =
                cleanMove(match[3] || "");


            if (
                looksLikeSAN(white)
            ) {
                result.push(white);
            }


            if (
                black &&
                looksLikeSAN(black)
            ) {
                result.push(black);
            }
        }


        return result;
    }


    // ========================================================
    // READ MOVES
    // ========================================================

    let moves = [];

    let rawMoveText = "";


    if (root) {

        // A
        moves = readDataAttributes(root);


        // B
        if (!moves.length) {

            moves =
                readMoveElements(root);
        }


        // C
        if (!moves.length) {

            rawMoveText =
                root.innerText ||
                root.textContent ||
                "";

            moves =
                parseMoveText(
                    rawMoveText
                );
        }
    }


    // ========================================================
    // LAST RESORT:
    // Try the whole document around move-list components
    // ========================================================

    if (!moves.length) {

        const candidateRoots = [
            ...document.querySelectorAll(
                "vertical-move-list, wc-move-list, .move-list-component"
            )
        ];


        for (const candidate of candidateRoots) {

            const text =
                candidate.innerText ||
                candidate.textContent ||
                "";

            const parsed =
                parseMoveText(text);

            if (parsed.length) {

                moves = parsed;

                rawMoveText = text;

                break;
            }
        }
    }


    // ========================================================
    // DEDUPLICATE
    // ========================================================

    const cleanedMoves = [];

    for (const move of moves) {

        const clean =
            cleanMove(move);

        if (!clean) {
            continue;
        }

        if (
            !cleanedMoves.length ||
            cleanedMoves[
                cleanedMoves.length - 1
            ] !== clean
        ) {

            cleanedMoves.push(clean);
        }
    }


    // ========================================================
    // RETURN
    // ========================================================

    return {

        url: location.href,

        fen,

        moves: cleanedMoves,

        hasBoard: !!board,

        hasGame: !!game,

        moveRootFound: !!root,

        moveText: rawMoveText

    };

})()
"""


class ChessComReader:

    def __init__(
        self,
        cdp: CDP,
    ):
        self.cdp = cdp

    def read(self) -> dict:

        result = self.cdp.evaluate(
            READ_POSITION_JS
        )

        if not result:

            return {
                "url": "",
                "fen": "",
                "moves": [],
                "hasBoard": False,
                "hasGame": False,
                "moveRootFound": False,
                "moveText": "",
            }

        return result