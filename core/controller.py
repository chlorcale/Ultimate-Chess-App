from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import chess

from app.config import (
    ENGINE_HASH_MB,
    ENGINE_THREADS,
    ENGINE_TIME,
    MOVE_POLL_MS,
    STOCKFISH_PATH,
)

from browser.cdp import CDP

from browser.launcher import (
    ensure_debug_chrome,
    find_chess_tab,
)

from chesscom.reader import (
    ChessComReader,
)

from core.chess_state import (
    build_board_from_fen,
    format_moves,
)

from engine.stockfish import (
    StockfishEngine,
)


class AppController:

    def __init__(self, ui):

        # ====================================================
        # UI
        # ====================================================

        self.ui = ui


        # ====================================================
        # CHROME / CDP
        # ====================================================

        self.cdp: CDP | None = None

        self.reader: ChessComReader | None = None


        # ====================================================
        # STOCKFISH
        # ====================================================

        self.engine = StockfishEngine(
            STOCKFISH_PATH,
            time_limit=ENGINE_TIME,
            threads=ENGINE_THREADS,
            hash_mb=ENGINE_HASH_MB,
        )


        # ====================================================
        # WORKER
        # ====================================================

        self.executor = ThreadPoolExecutor(
            max_workers=1
        )

        self.future = None


        # ====================================================
        # CHESS STATE
        # ====================================================

        self.current_url = ""

        self.current_fen = ""

        self.current_moves: list[str] = []


        # ====================================================
        # ANALYSIS STATE
        # ====================================================

        # white / black / both
        self.mode = "both"

        # FEN mà Stockfish đã phân tích xong
        self._analyzed_fen = ""

        # dùng để loại bỏ kết quả engine cũ
        self.position_version = 0


        # ====================================================
        # APP STATE
        # ====================================================

        self.running = True


    # ========================================================
    # START
    # ========================================================

    def start(self):

        try:

            # ------------------------------------------------
            # Chrome
            # ------------------------------------------------

            ensure_debug_chrome()


            # ------------------------------------------------
            # Tìm tab Chess.com
            # ------------------------------------------------

            target = find_chess_tab()

            if not target:

                raise RuntimeError(
                    "Không tìm thấy tab Chess.com.\n"
                    "Hãy mở một ván cờ."
                )


            # ------------------------------------------------
            # WebSocket URL
            # ------------------------------------------------

            ws_url = target.get(
                "webSocketDebuggerUrl"
            )

            if not ws_url:

                raise RuntimeError(
                    "Chess.com tab không có CDP WebSocket."
                )


            # ------------------------------------------------
            # Connect CDP
            # ------------------------------------------------

            self.cdp = CDP(
                ws_url
            )


            # ------------------------------------------------
            # Reader
            # ------------------------------------------------

            self.reader = ChessComReader(
                self.cdp
            )


            # ------------------------------------------------
            # UI
            # ------------------------------------------------

            self.ui.set_status(
                "Chess.com connected"
            )


            # ------------------------------------------------
            # Console
            # ------------------------------------------------

            print(
                "[CHESS] Tab được chọn:"
            )

            print(
                target.get(
                    "url",
                    ""
                )
            )


            print(
                "[CHESS] Reader started."
            )


            # ------------------------------------------------
            # Start polling
            # ------------------------------------------------

            self.poll()


        except Exception as exc:

            self.ui.set_status(
                "Connection error"
            )

            self.show_error(
                str(exc)
            )


    # ========================================================
    # POLLING
    # ========================================================

    def poll(self):

        if not self.running:
            return


        try:

            self._poll_once()


        except Exception as exc:

            self.ui.set_status(
                "Reader error"
            )

            print(
                "[WARNING]",
                exc
            )


        # ----------------------------------------------------
        # Poll again
        # ----------------------------------------------------

        if self.running:

            self.ui.root.after(
                MOVE_POLL_MS,
                self.poll,
            )


    # ========================================================
    # READ CHESS.COM
    # ========================================================

    def _poll_once(self):

        if not self.reader:
            return


        # ----------------------------------------------------
        # Reader
        # ----------------------------------------------------

        data = self.reader.read()

        print(
            "[READER]",
            "root=",
            data.get("moveRootFound"),
            "moves=",
            data.get("moves"),
        )
        # ----------------------------------------------------
        # Data
        # ----------------------------------------------------

        url = data.get(
            "url",
            ""
        )

        fen = data.get(
            "fen",
            ""
        )

        moves = data.get(
            "moves",
            []
        )


        # ====================================================
        # URL CHANGED
        # ====================================================

        if url != self.current_url:

            self.current_url = url

            self.current_fen = ""

            self.current_moves = []

            self._analyzed_fen = ""

            self.position_version += 1


            self.ui.set_status(
                "Reading Chess.com"
            )


            print(
                "[CHESS] Page:"
            )

            print(
                url
            )


        # ====================================================
        # MOVE LIST
        # ====================================================

        if moves != self.current_moves:

            self.current_moves = list(
                moves
            )


            self.ui.set_moves(
                format_moves(
                    self.current_moves
                )
            )


            print(
                "[CHESS]",
                " ".join(
                    self.current_moves
                )
            )


        # ====================================================
        # NO FEN
        # ====================================================

        if not fen:

            self.current_fen = ""

            self.ui.set_status(
                "Waiting for board..."
            )

            return


        # ====================================================
        # POSITION CHANGED
        # ====================================================

        if fen != self.current_fen:

            self.current_fen = fen

            self.position_version += 1

            self.ui.set_status(
                "Analyzing..."
            )


            print(
                "[FEN]",
                fen
            )


        # ====================================================
        # STOCKFISH
        # ====================================================

        try:

            board = build_board_from_fen(
                fen
            )

        except Exception as exc:

            print(
                "[CHESS] FEN error:",
                exc
            )

            return


        self._maybe_start_analysis(
            board,
            fen,
        )


    # ========================================================
    # CHECK ANALYSIS MODE
    # ========================================================

    def _should_analyze(
        self,
        board: chess.Board,
    ) -> bool:

        # ----------------------------------------------------
        # Both sides
        # ----------------------------------------------------

        if self.mode == "both":

            return True


        # ----------------------------------------------------
        # White only
        # ----------------------------------------------------

        if (
            self.mode == "white"
            and board.turn == chess.WHITE
        ):

            return True


        # ----------------------------------------------------
        # Black only
        # ----------------------------------------------------

        if (
            self.mode == "black"
            and board.turn == chess.BLACK
        ):

            return True


        return False


    # ========================================================
    # START ENGINE
    # ========================================================

    def _maybe_start_analysis(
        self,
        board: chess.Board,
        fen: str,
    ):

        if not self.running:
            return


        # ====================================================
        # GAME OVER
        # ====================================================

        if board.is_game_over():

            self.ui.set_engine_result(
                "",
                "Game over",
                0,
            )

            self._analyzed_fen = fen

            return


        # ====================================================
        # MODE FILTER
        # ====================================================

        if not self._should_analyze(
            board
        ):

            self.ui.set_engine_result(
                "",
                "",
                0,
            )

            self._analyzed_fen = fen

            return


        # ====================================================
        # ALREADY ANALYZED
        # ====================================================

        if (
            fen == self._analyzed_fen
        ):

            return


        # ====================================================
        # ENGINE BUSY
        # ====================================================

        if (
            self.future
            and not self.future.done()
        ):

            return


        # ====================================================
        # START
        # ====================================================

        version = (
            self.position_version
        )


        board_copy = board.copy()


        self.ui.set_thinking()


        print(
            "[STOCKFISH] Analyzing..."
        )


        self.future = (
            self.executor.submit(
                self._analyze_worker,
                board_copy,
                fen,
                version,
            )
        )


    # ========================================================
    # STOCKFISH WORKER
    # ========================================================

    def _analyze_worker(
        self,
        board: chess.Board,
        fen: str,
        version: int,
    ):

        try:

            result = self.engine.analyze(
                board
            )


        except Exception as exc:

            print(
                "[STOCKFISH ERROR]",
                exc
            )

            self.ui.root.after(
                0,
                lambda: self.ui.set_status(
                    "Stockfish error"
                ),
            )

            return


        if not self.running:
            return


        # ----------------------------------------------------
        # Return to Tkinter main thread
        # ----------------------------------------------------

        self.ui.root.after(
            0,
            lambda: self._apply_engine_result(
                result,
                fen,
                version,
            ),
        )


    # ========================================================
    # APPLY STOCKFISH RESULT
    # ========================================================

    def _apply_engine_result(
        self,
        result: dict,
        fen: str,
        version: int,
    ):

        if not self.running:
            return


        # ====================================================
        # OLD POSITION
        # ====================================================

        if version != self.position_version:

            print(
                "[STOCKFISH] Ignoring stale result."
            )

            return


        # ====================================================
        # FEN CHANGED
        # ====================================================

        if fen != self.current_fen:

            print(
                "[STOCKFISH] Position changed."
            )

            return


        # ====================================================
        # SAVE
        # ====================================================

        self._analyzed_fen = fen


        # ====================================================
        # RESULT
        # ====================================================

        move = result.get(
            "move",
            ""
        )

        evaluation = result.get(
            "evaluation",
            ""
        )

        depth = result.get(
            "depth",
            0
        )


        # ====================================================
        # UI
        # ====================================================

        self.ui.set_engine_result(
            move,
            evaluation,
            depth,
        )


        self.ui.set_status(
            "Stockfish ready"
        )


        # ====================================================
        # CONSOLE
        # ====================================================

        print(
            "[STOCKFISH]"
        )

        print(
            "  Best move:",
            move,
        )

        print(
            "  Evaluation:",
            evaluation,
        )

        print(
            "  Depth:",
            depth,
        )


    # ========================================================
    # CHANGE ANALYSIS MODE
    # ========================================================

    def set_mode(
        self,
        mode: str,
    ):

        if mode not in {
            "white",
            "black",
            "both",
        }:

            return


        # ----------------------------------------------------
        # Change mode
        # ----------------------------------------------------

        self.mode = mode


        # ----------------------------------------------------
        # Force new analysis
        # ----------------------------------------------------

        self._analyzed_fen = ""


        # ----------------------------------------------------
        # Invalidate old result
        # ----------------------------------------------------

        self.position_version += 1


        # ----------------------------------------------------
        # UI
        # ----------------------------------------------------

        print(
            "[STOCKFISH] Analysis mode:",
            mode,
        )


        # Nếu hiện tại là bên không được chọn,
        # xoá suggestion cũ ngay.
        if self.current_fen:

            try:

                board = build_board_from_fen(
                    self.current_fen
                )

                if not self._should_analyze(
                    board
                ):

                    self.ui.set_engine_result(
                        "",
                        "",
                        0,
                    )

            except Exception:
                pass


    # ========================================================
    # ERROR
    # ========================================================

    def show_error(
        self,
        message: str,
    ):

        print(
            "[ERROR]",
            message,
        )


    # ========================================================
    # STOP
    # ========================================================

    def stop(self):

        if not self.running:
            return


        print(
            "[APP] Stopping..."
        )


        self.running = False


        # ----------------------------------------------------
        # CDP
        # ----------------------------------------------------

        if self.cdp:

            try:
                self.cdp.close()
            except Exception:
                pass

            self.cdp = None


        # ----------------------------------------------------
        # Executor
        # ----------------------------------------------------

        try:

            self.executor.shutdown(
                wait=False,
                cancel_futures=True,
            )

        except Exception:
            pass


        # ----------------------------------------------------
        # Stockfish
        # ----------------------------------------------------

        try:

            self.engine.close()

        except Exception:
            pass


        print(
            "[APP] Stopped."
        )