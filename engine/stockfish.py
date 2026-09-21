from __future__ import annotations

from pathlib import Path

import chess
import chess.engine


class StockfishEngine:
    """
    Wrapper đơn giản cho Stockfish UCI engine.
    """

    def __init__(
        self,
        path: Path,
        time_limit: float = 0.4,
        threads: int = 2,
        hash_mb: int = 128,
    ):
        self.path = Path(path)

        if not self.path.exists():
            raise FileNotFoundError(
                f"Không tìm thấy Stockfish:\n{self.path}"
            )

        if not self.path.is_file():
            raise FileNotFoundError(
                f"Đường dẫn Stockfish không phải file:\n{self.path}"
            )

        print(f"[STOCKFISH] Loading: {self.path}")

        self.engine = chess.engine.SimpleEngine.popen_uci(
            str(self.path)
        )

        self.time_limit = float(time_limit)

        # Một số build Stockfish hỗ trợ các option này.
        try:
            self.engine.configure(
                {
                    "Threads": int(threads),
                    "Hash": int(hash_mb),
                }
            )
        except Exception as exc:
            print(
                f"[STOCKFISH] Không thể configure Threads/Hash: {exc}"
            )

        print("[STOCKFISH] Ready.")


    def analyze(
        self,
        board: chess.Board,
    ) -> dict:
        """
        Phân tích position hiện tại và trả về:

        {
            "move": "Nf3",
            "evaluation": "+0.42",
            "depth": 18
        }
        """

        if board.is_game_over():
            return {
                "move": "",
                "evaluation": "Game over",
                "depth": 0,
            }

        info = self.engine.analyse(
            board,
            chess.engine.Limit(
                time=self.time_limit
            ),
        )

        pv = info.get("pv", [])

        if not pv:
            return {
                "move": "",
                "evaluation": "--",
                "depth": info.get("depth", 0),
            }

        best_move = pv[0]

        # Chuyển UCI move -> SAN
        san = board.san(best_move)

        # Đánh giá theo góc nhìn bên Trắng
        score = info["score"].pov(chess.WHITE)

        mate = score.mate()

        if mate is not None:
            if mate > 0:
                evaluation = f"+M{mate}"
            elif mate < 0:
                evaluation = f"-M{abs(mate)}"
            else:
                evaluation = "M0"
        else:
            centipawns = score.score(
                mate_score=100000
            )

            if centipawns is None:
                evaluation = "0.00"
            else:
                evaluation = f"{centipawns / 100:+.2f}"

        return {
            "move": san,
            "evaluation": evaluation,
            "depth": info.get("depth", 0),
        }


    def close(self) -> None:
        """
        Đóng Stockfish.
        """

        try:
            self.engine.quit()
        except Exception:
            pass