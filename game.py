from __future__ import annotations

from typing import List, Tuple, Optional

BOARD_SIZE = 15

EMPTY = 0
BLACK = 1
WHITE = 2

DIRECTIONS = [
    (1, 0),
    (0, 1),
    (1, 1),
    (1, -1),
]

Board = List[List[int]]
Position = Tuple[int, int]


def create_board() -> Board:
    return [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]


def copy_board(board: Board) -> Board:
    return [row[:] for row in board]


def is_valid_position(row: int, col: int) -> bool:
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def is_empty(board: Board, row: int, col: int) -> bool:
    return (
        is_valid_position(row, col)
        and board[row][col] == EMPTY
    )


def get_line(
    board: Board,
    row: int,
    col: int,
    dr: int,
    dc: int,
    player: int,
) -> Tuple[int, int]:
    """
    해당 위치를 기준으로 같은 돌이 연결된 개수를 센다.

    반환값:
        (연결된 돌의 총 개수, 해당 방향에서 가장 먼 끝까지의 거리)
    """

    count = 1
    distance = 0

    r = row + dr
    c = col + dc

    while is_valid_position(r, c) and board[r][c] == player:
        count += 1
        distance += 1
        r += dr
        c += dc

    r = row - dr
    c = col - dc

    while is_valid_position(r, c) and board[r][c] == player:
        count += 1
        distance += 1
        r -= dr
        c -= dc

    return count, distance


def count_direction(
    board: Board,
    row: int,
    col: int,
    dr: int,
    dc: int,
    player: int,
) -> int:
    count = 1

    r = row + dr
    c = col + dc

    while is_valid_position(r, c) and board[r][c] == player:
        count += 1
        r += dr
        c += dc

    r = row - dr
    c = col - dc

    while is_valid_position(r, c) and board[r][c] == player:
        count += 1
        r -= dr
        c -= dc

    return count


def max_connected(
    board: Board,
    row: int,
    col: int,
    player: int,
) -> int:
    maximum = 0

    for dr, dc in DIRECTIONS:
        maximum = max(
            maximum,
            count_direction(
                board,
                row,
                col,
                dr,
                dc,
                player,
            ),
        )

    return maximum


def has_exact_five(
    board: Board,
    row: int,
    col: int,
    player: int,
) -> bool:
    """
    정확히 5목이 만들어졌는지 검사한다.

    흑의 경우 6목 이상은 승리로 인정하지 않고
    장목 금칙으로 처리하기 위해 별도로 검사한다.
    """

    for dr, dc in DIRECTIONS:
        count = count_direction(
            board,
            row,
            col,
            dr,
            dc,
            player,
        )

        if count == 5:
            return True

    return False


def has_overline(
    board: Board,
    row: int,
    col: int,
    player: int,
) -> bool:
    """
    6목 이상인지 검사.
    """

    return max_connected(board, row, col, player) >= 6


def board_to_strings(board: Board) -> List[str]:
    """
    디버깅 및 패턴 분석용.
    """

    result = []

    for row in board:
        line = ""

        for cell in row:
            if cell == BLACK:
                line += "X"
            elif cell == WHITE:
                line += "O"
            else:
                line += "."

        result.append(line)

    return result


def count_open_threes(
    board: Board,
    player: int,
) -> int:
    """
    활삼 후보를 계산한다.

    빈칸에 돌을 놓았을 때 해당 방향에서
    열린 3 형태가 몇 개 만들어지는지를 계산한다.

    렌주의 모든 복잡한 패턴을 완전히 대체하는
    공식 판정기가 아니라 게임용 금칙 판정기다.
    """

    count = 0

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != player:
                continue

            for dr, dc in DIRECTIONS:
                # 같은 패턴은 한 방향에서 한 번만 센다.
                pr = r - dr
                pc = c - dc

                if (
                    is_valid_position(pr, pc)
                    and board[pr][pc] == player
                ):
                    continue

                cells = []

                for i in range(-1, 6):
                    rr = r + dr * i
                    cc = c + dc * i

                    if is_valid_position(rr, cc):
                        cells.append(board[rr][cc])
                    else:
                        cells.append(-1)

                pattern = cells

                # .XXX.
                if len(pattern) >= 5:
                    for start in range(len(pattern) - 4):
                        segment = pattern[start:start + 5]

                        if segment == [
                            EMPTY,
                            player,
                            player,
                            player,
                            EMPTY,
                        ]:
                            count += 1

    return count


def count_four_threats(
    board: Board,
    player: int,
) -> int:
    """
    현재 위치에서 한 수로 5목을 만들 수 있는
    서로 다른 빈칸의 개수를 계산한다.

    4-4 판정에 사용한다.
    """

    threats = set()

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != EMPTY:
                continue

            test = copy_board(board)
            test[r][c] = player

            if has_exact_five(test, r, c, player):
                threats.add((r, c))

    return len(threats)


def is_forbidden_move(
    board: Board,
    row: int,
    col: int,
    player: int,
) -> Tuple[bool, str]:
    """
    해당 수가 금칙인지 판단한다.

    반환:
        (금칙 여부, 이유)
    """

    if player != BLACK:
        return False, ""

    if not is_empty(board, row, col):
        return True, "이미 돌이 놓여 있습니다."

    test = copy_board(board)
    test[row][col] = player

    # 1. 장목
    if has_overline(test, row, col, player):
        # 정확히 5목은 장목이 아님
        if not has_exact_five(test, row, col, player):
            return True, "장목(6목 이상) 금칙입니다."

    # 장목이면 이후 금칙 검사 불필요
    if has_overline(test, row, col, player):
        return True, "장목(6목 이상) 금칙입니다."

    # 2. 4-4
    four_count = count_four_threats(test, player)

    if four_count >= 2:
        return True, "4-4 금칙입니다."

    # 3. 3-3
    three_count = count_open_threes(test, player)

    if three_count >= 2:
        return True, "3-3 금칙입니다."

    return False, ""


def place_stone(
    board: Board,
    row: int,
    col: int,
    player: int,
) -> Tuple[bool, str]:
    """
    실제 돌을 놓는다.

    반환:
        성공 여부, 메시지
    """

    if not is_valid_position(row, col):
        return False, "잘못된 위치입니다."

    if not is_empty(board, row, col):
        return False, "이미 돌이 놓여 있습니다."

    forbidden, reason = is_forbidden_move(
        board,
        row,
        col,
        player,
    )

    if forbidden:
        return False, reason

    board[row][col] = player

    if player == BLACK:
        if has_overline(board, row, col, player):
            board[row][col] = EMPTY
            return False, "장목은 금지됩니다."

    if has_exact_five(board, row, col, player):
        return True, "승리!"

    return True, "OK"


def check_winner(
    board: Board,
    row: int,
    col: int,
    player: int,
) -> bool:
    if not is_valid_position(row, col):
        return False

    if board[row][col] != player:
        return False

    if player == BLACK and has_overline(
        board,
        row,
        col,
        player,
    ):
        return False

    return has_exact_five(
        board,
        row,
        col,
        player,
    )


def is_board_full(board: Board) -> bool:
    return all(
        board[r][c] != EMPTY
        for r in range(BOARD_SIZE)
        for c in range(BOARD_SIZE)
    )


def get_valid_moves(
    board: Board,
    player: int,
) -> List[Position]:
    moves = []

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != EMPTY:
                continue

            if player == BLACK:
                forbidden, _ = is_forbidden_move(
                    board,
                    r,
                    c,
                    player,
                )

                if forbidden:
                    continue

            moves.append((r, c))

    return moves


def get_forbidden_moves(
    board: Board,
    player: int,
) -> List[Position]:
    if player != BLACK:
        return []

    result = []

    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if board[r][c] != EMPTY:
                continue

            forbidden, _ = is_forbidden_move(
                board,
                r,
                c,
                player,
            )

            if forbidden:
                result.append((r, c))

    return result
