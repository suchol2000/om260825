import streamlit as st

from game import (
    BOARD_SIZE,
    EMPTY,
    BLACK,
    WHITE,
    create_board,
    get_forbidden_moves,
    is_board_full,
    place_stone,
)

from ai import choose_move


st.set_page_config(
    page_title="AI 렌주 오목",
    page_icon="⚫",
    layout="centered",
)


# --------------------------------------------------
# 세션 초기화
# --------------------------------------------------

def initialize_game():
    st.session_state.board = create_board()
    st.session_state.current_player = BLACK
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.message = "흑돌부터 시작합니다."
    st.session_state.last_move = None


if "board" not in st.session_state:
    initialize_game()


# --------------------------------------------------
# 사이드바
# --------------------------------------------------

st.sidebar.title("🎮 게임 설정")

game_mode = st.sidebar.radio(
    "게임 모드",
    [
        "🤖 사람 vs 컴퓨터",
        "👥 사람 vs 사람",
    ],
)

difficulty = st.sidebar.selectbox(
    "컴퓨터 난이도",
    [
        "쉬움",
        "보통",
        "어려움",
    ],
)

if game_mode == "🤖 사람 vs 컴퓨터":
    human_color = st.sidebar.radio(
        "내 돌",
        [
            "⚫ 흑",
            "⚪ 백",
        ],
    )

    human_player = (
        BLACK
        if human_color == "⚫ 흑"
        else WHITE
    )

    ai_player = (
        WHITE
        if human_player == BLACK
        else BLACK
    )
else:
    human_player = None
    ai_player = None


st.sidebar.markdown("---")

if st.sidebar.button(
    "🔄 새 게임",
    use_container_width=True,
):
    initialize_game()
    st.rerun()


st.sidebar.markdown("---")

st.sidebar.info(
    """
### 📜 렌주 규칙

흑돌에는 금칙이 적용됩니다.

- 3-3 금지
- 4-4 금지
- 6목 이상 장목 금지
- 정확히 5목은 승리

백돌은 금칙이 없습니다.
"""
)


# --------------------------------------------------
# 제목
# --------------------------------------------------

st.title("⚫ AI 렌주 오목")

st.caption(
    "15 × 15 · 3-3 / 4-4 / 장목 금칙"
)


# --------------------------------------------------
# 게임 상태 표시
# --------------------------------------------------

if st.session_state.game_over:
    if st.session_state.winner == BLACK:
        st.success("🏆 흑돌 승리!")
    elif st.session_state.winner == WHITE:
        st.success("🏆 백돌 승리!")
    else:
        st.info("🤝 무승부!")
else:
    if st.session_state.current_player == BLACK:
        st.markdown("### 현재 차례: ⚫ 흑")
    else:
        st.markdown("### 현재 차례: ⚪ 백")

    if st.session_state.message:
        st.caption(st.session_state.message)


# --------------------------------------------------
# 오목판 CSS
# --------------------------------------------------

st.markdown(
    """
    <style>
    div[data-testid="stHorizontalBlock"] {
        gap: 0rem;
    }

    div[data-testid="stButton"] button {
        min-width: 36px;
        width: 36px;
        height: 36px;
        padding: 0;
        border-radius: 0;
        border: 1px solid #9b7653;
        background-color: #e8b86a;
        color: #111111;
        font-size: 22px;
        line-height: 1;
    }

    div[data-testid="stButton"] button:hover {
        border-color: #333333;
        background-color: #f0c77b;
    }

    @media (max-width: 700px) {
        div[data-testid="stButton"] button {
            min-width: 22px;
            width: 22px;
            height: 22px;
            font-size: 14px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# 돌 표시
# --------------------------------------------------

def stone_text(value):
    if value == BLACK:
        return "●"

    if value == WHITE:
        return "○"

    return "·"


# --------------------------------------------------
# 돌 놓기
# --------------------------------------------------

def handle_move(row, col):
    if st.session_state.game_over:
        return

    player = st.session_state.current_player

    success, message = place_stone(
        st.session_state.board,
        row,
        col,
        player,
    )

    if not success:
        st.session_state.message = f"⚠️ {message}"
        return

    st.session_state.last_move = (
        row,
        col,
    )

    # 승리
    if message == "승리!":
        st.session_state.game_over = True
        st.session_state.winner = player

        if player == BLACK:
            st.session_state.message = "⚫ 흑돌이 5목을 완성했습니다!"
        else:
            st.session_state.message = "⚪ 백돌이 5목을 완성했습니다!"

        return

    # 무승부
    if is_board_full(
        st.session_state.board
    ):
        st.session_state.game_over = True
        st.session_state.winner = None
        st.session_state.message = "더 이상 놓을 곳이 없습니다."
        return

    # 턴 변경
    st.session_state.current_player = (
        WHITE
        if player == BLACK
        else BLACK
    )

    st.session_state.message = "돌을 놓았습니다."


# --------------------------------------------------
# 컴퓨터 턴
# --------------------------------------------------

def handle_ai_turn():
    if st.session_state.game_over:
        return

    if game_mode != "🤖 사람 vs 컴퓨터":
        return

    if st.session_state.current_player != ai_player:
        return

    move = choose_move(
        st.session_state.board,
        ai_player,
        difficulty,
    )

    if move is None:
        st.session_state.game_over = True
        st.session_state.winner = None
        st.session_state.message = "무승부!"
        return

    row, col = move

    success, message = place_stone(
        st.session_state.board,
        row,
        col,
        ai_player,
    )

    if not success:
        st.session_state.message = (
            f"AI 오류: {message}"
        )
        return

    st.session_state.last_move = (
        row,
        col,
    )

    if message == "승리!":
        st.session_state.game_over = True
        st.session_state.winner = ai_player

        if ai_player == BLACK:
            st.session_state.message = (
                "🤖 컴퓨터(흑)가 승리했습니다!"
            )
        else:
            st.session_state.message = (
                "🤖 컴퓨터(백)가 승리했습니다!"
            )

        return

    if is_board_full(
        st.session_state.board
    ):
        st.session_state.game_over = True
        st.session_state.winner = None
        st.session_state.message = "무승부!"
        return

    st.session_state.current_player = (
        WHITE
        if ai_player == BLACK
        else BLACK
    )

    st.session_state.message = (
        f"🤖 컴퓨터가 {row + 1}행 {col + 1}열에 놓았습니다."
    )


# --------------------------------------------------
# AI가 흑이고 선공인 경우
# --------------------------------------------------

if (
    game_mode == "🤖 사람 vs 컴퓨터"
    and ai_player == BLACK
    and st.session_state.current_player == BLACK
    and not st.session_state.game_over
):
    handle_ai_turn()
    st.rerun()


# --------------------------------------------------
# 금칙 위치
# --------------------------------------------------

forbidden_moves = set()

if (
    st.session_state.current_player == BLACK
    and not st.session_state.game_over
):
    forbidden_moves = set(
        get_forbidden_moves(
            st.session_state.board,
            BLACK,
        )
    )


# --------------------------------------------------
# 오목판
# --------------------------------------------------

for row in range(BOARD_SIZE):
    columns = st.columns(BOARD_SIZE)

    for col in range(BOARD_SIZE):
        with columns[col]:

            value = st.session_state.board[row][col]

            if value == BLACK:
                label = "●"

            elif value == WHITE:
                label = "○"

            else:
                if (row, col) in forbidden_moves:
                    label = "×"
                else:
                    label = "·"

            disabled = (
                st.session_state.game_over
                or value != EMPTY
            )

            # 사람 vs 컴퓨터에서는 사람 차례만 클릭 가능
            if (
                game_mode == "🤖 사람 vs 컴퓨터"
                and st.session_state.current_player != human_player
            ):
                disabled = True

            if st.button(
                label,
                key=f"cell_{row}_{col}",
                disabled=disabled,
                use_container_width=True,
            ):
                handle_move(
                    row,
                    col,
                )

                st.rerun()


# --------------------------------------------------
# AI 자동 실행
# --------------------------------------------------

if (
    game_mode == "🤖 사람 vs 컴퓨터"
    and not st.session_state.game_over
    and st.session_state.current_player == ai_player
):
    handle_ai_turn()
    st.rerun()


# --------------------------------------------------
# 하단 안내
# --------------------------------------------------

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "판 크기",
        "15 × 15",
    )

with col2:
    if st.session_state.current_player == BLACK:
        st.metric("현재", "⚫ 흑")
    else:
        st.metric("현재", "⚪ 백")

with col3:
    if st.session_state.last_move:
        r, c = st.session_state.last_move
        st.metric(
            "마지막 수",
            f"{r + 1},{c + 1}",
        )
    else:
        st.metric(
            "마지막 수",
            "-",
        )

st.caption(
    "× 표시가 있는 위치는 현재 흑에게 금칙으로 판정된 위치입니다."
)
