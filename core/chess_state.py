from __future__ import annotations

import chess


def build_board_from_fen(
    fen: str,
) -> chess.Board:

    if not fen:
        raise ValueError(
            "Chess.com không trả về FEN."
        )

    return chess.Board(fen)


def format_moves(
    moves: list[str],
) -> str:

    lines = []

    for i in range(0, len(moves), 2):

        number = (i // 2) + 1

        white = moves[i]

        black = (
            moves[i + 1]
            if i + 1 < len(moves)
            else ""
        )

        if black:
            lines.append(
                f"{number}. {white} {black}"
            )
        else:
            lines.append(
                f"{number}. {white}"
            )

    return "\n".join(lines)