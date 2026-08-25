from __future__ import annotations

import random
from typing import List, Tuple

from game import (
    BOARD_SIZE,
    EMPTY,
    BLACK,
    WHITE,
    Position,
    Board,
    copy_board,
    get_valid_moves,
    has_exact_five,
    has_overline,
    is_forbidden_move,
)


DIRECTIONS = [
    (1, 0),
    (0, 1),
    (1, 1),
    (1, -1),
]


def neighbors(
    board: Board,
    distance: int = 2,
) -> List[Position]:
    stones = []

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != EMPTY:
                stones.append((r, c))

    if not stones:
        center = BOARD_SIZE // 2
        return [(center, center)]

    candidates = set()

    for r, c in stones:
        for dr in range(-distance, distance + 1):
            for dc in range(-distance, distance + 1):
                if dr == 0 and dc == 0:
                    continue

                rr = r + dr
                cc = c + dc

                if (
                    0 <= rr < BOARD_SIZE
                    and 0 <= cc < BOARD_SIZE
                    and board[rr][cc] == EMPTY
                ):
                    candidates.add((rr, cc))

    return list(candidates)


def line_score(
    count: int,
    open_ends: int,
) -> int:
    if count >= 5:
        return 1000000

    if count == 4:
        if open_ends == 2:
            return 100000
        if open_ends == 1:
            return 20000

    if count == 3:
        if open_ends == 2:
            return 10000
        if open_ends == 1:
            return 1500

    if count == 2:
        if open_ends == 2:
            return 1000
        if open_ends == 1:
            return 200

    if count == 1:
        return 20

    return 0


def evaluate_direction(
    board: Board,
    row: int,
    col: int,
    player: int,
    dr: int,
    dc: int,
) -> int:
    """
    해당 방향에서 이어지는 돌의 강도를 평가한다.
    """

    count = 1

    r = row + dr
    c = col + dc

    while (
        0 <= r < BOARD_SIZE
        and 0 <= c < BOARD_SIZE
        and board[r][c] == player
    ):
        count += 1
        r += dr
        c += dc

    open_ends = 0

    if (
        0 <= r < BOARD_SIZE
        and 0 <= c < BOARD_SIZE
        and board[r][c] == EMPTY
    ):
        open_ends += 1

    r = row - dr
    c = col - dc

    while (
        0 <= r < BOARD_SIZE
        and 0 <= c < BOARD_SIZE
        and board[r][c] == player
    ):
        count += 1
        r -= dr
        c -= dc

    if (
        0 <= r < BOARD_SIZE
        and 0 <= c < BOARD_SIZE
        and board[r][c] == EMPTY
    ):
        open_ends += 1

    return line_score(count, open_ends)


def position_score(
    board: Board,
    row: int,
    col: int,
    player: int,
) -> int:
    test = copy_board(board)
    test[row][col] = player

    score = 0

    for dr, dc in DIRECTIONS:
        score += evaluate_direction(
            test,
            row,
            col,
            player,
            dr,
            dc,
        )

    # 중앙 선호
    center = BOARD_SIZE // 2
    distance = abs(row - center) + abs(col - center)

    score += max(0, 30 - distance)

    return score


def creates_win(
    board: Board,
    move: Position,
    player: int,
) -> bool:
    r, c = move

    test = copy_board(board)
    test[r][c] = player

    if player == BLACK and has_overline(
        test,
        r,
        c,
        player,
    ):
        return False

    return has_exact_five(
        test,
        r,
        c,
        player,
    )


def find_winning_move(
    board: Board,
    player: int,
) -> Position | None:
    moves = get_valid_moves(board, player)

    for move in moves:
        if creates_win(board, move, player):
            return move

    return None


def tactical_score(
    board: Board,
    move: Position,
    player: int,
) -> int:
    opponent = WHITE if player == BLACK else BLACK

    attack = position_score(
        board,
        move[0],
        move[1],
        player,
    )

    defense = position_score(
        board,
        move[0],
        move[1],
        opponent,
    )

    return attack + int(defense * 0.8)


def choose_move(
    board: Board,
    player: int,
    difficulty: str = "보통",
) -> Position | None:
    """
    AI의 다음 수를 결정한다.
    """

    valid_moves = get_valid_moves(
        board,
        player,
    )

    if not valid_moves:
        return None

    # 첫 수는 중앙
    if all(
        board[r][c] == EMPTY
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
    ):
        center = BOARD_SIZE // 2

        if (center, center) in valid_moves:
            return center, center

    opponent = WHITE if player == BLACK else BLACK

    # 1. 내가 바로 이길 수 있는 수
    winning = find_winning_move(
        board,
        player,
    )

    if winning:
        return winning

    # 2. 상대가 다음에 이기는 것을 차단
    opponent_win = find_winning_move(
        board,
        opponent,
    )

    if opponent_win and opponent_win in valid_moves:
        return opponent_win

    # 쉬움 AI
    if difficulty == "쉬움":
        candidates = neighbors(
            board,
            distance=2,
        )

        candidates = [
            move
            for move in candidates
            if move in valid_moves
        ]

        if not candidates:
            candidates = valid_moves

        return random.choice(candidates)

    # 후보를 주변 돌로 제한
    candidates = neighbors(
        board,
        distance=2,
    )

    candidates = [
        move
        for move in candidates
        if move in valid_moves
    ]

    if not candidates:
        candidates = valid_moves

    scored = []

    for move in candidates:
        score = tactical_score(
            board,
            move,
            player,
        )

        # 어려움에서는 방어 가중치 강화
        if difficulty == "어려움":
            defense = position_score(
                board,
                move[0],
                move[1],
                opponent,
            )

            score += int(defense * 1.5)

        # 약간의 랜덤성을 넣어 항상 같은 수를 두지 않음
        score += random.randint(0, 10)

        scored.append(
            (
                score,
                move,
            )
        )

    scored.sort(
        key=lambda item: item[0],
        reverse=True,
    )

    return scored[0][1]
