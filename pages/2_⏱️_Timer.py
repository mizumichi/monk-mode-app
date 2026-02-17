"""
ポモドーロタイマーページ

作業/休憩の切り替え、カスタマイズ可能な時間設定、セッション履歴を提供する。
タスクと連携して作業時間を自動記録する。
"""

import time
from datetime import date, datetime

import streamlit as st

from components.auth import is_authenticated, get_current_user
from utils.database import (
    get_tasks_by_date,
    save_pomodoro_session,
    get_pomodoro_sessions_by_date,
    update_task_work_time,
)
from utils.constants import (
    POMODORO_WORK_MINUTES,
    POMODORO_SHORT_BREAK_MINUTES,
    POMODORO_LONG_BREAK_MINUTES,
    POMODORO_SESSIONS_UNTIL_LONG_BREAK,
    SESSION_TYPE_WORK,
    SESSION_TYPE_SHORT_BREAK,
    SESSION_TYPE_LONG_BREAK,
    SESSION_TYPE_LABELS,
    SESSION_TYPE_ICONS,
)

st.set_page_config(
    page_title="ポモドーロタイマー",
    page_icon="⏱️",
    layout="centered",
)

# 認証チェック
if not is_authenticated():
    st.switch_page("pages/0_🔐_Auth.py")

user = get_current_user()
today = date.today()
today_str = today.isoformat()


# --- セッション状態の初期化 ---


def _initialize_timer_state() -> None:
    """タイマー関連のセッション状態を初期化"""
    defaults = {
        "timer_running": False,
        "timer_paused": False,
        "timer_start_time": None,
        "timer_duration_seconds": 0,
        "timer_session_type": SESSION_TYPE_WORK,
        "pomodoro_count": 0,
        "custom_work_minutes": POMODORO_WORK_MINUTES,
        "custom_short_break_minutes": POMODORO_SHORT_BREAK_MINUTES,
        "custom_long_break_minutes": POMODORO_LONG_BREAK_MINUTES,
        "timer_task_id": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


_initialize_timer_state()


# --- タイマーユーティリティ関数 ---


def _get_remaining_seconds() -> int:
    """
    残り時間を計算

    Returns:
        残り秒数（0以上）
    """
    if not st.session_state["timer_running"]:
        return st.session_state.get("timer_duration_seconds", 0)

    start_time = st.session_state["timer_start_time"]
    duration = st.session_state["timer_duration_seconds"]

    elapsed = (datetime.now() - start_time).total_seconds()
    remaining = duration - elapsed

    return max(0, int(remaining))


def _format_time(seconds: int) -> str:
    """
    秒をMM:SS形式にフォーマット

    Args:
        seconds: 秒数

    Returns:
        MM:SS形式の文字列
    """
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def _start_timer(session_type: str, duration_seconds: int) -> None:
    """
    タイマーを開始

    Args:
        session_type: 'work', 'short_break', 'long_break'
        duration_seconds: タイマー時間（秒）
    """
    st.session_state["timer_running"] = True
    st.session_state["timer_paused"] = False
    st.session_state["timer_start_time"] = datetime.now()
    st.session_state["timer_duration_seconds"] = duration_seconds
    st.session_state["timer_session_type"] = session_type


def _pause_timer() -> None:
    """タイマーを一時停止（残り時間をdurationとして保持）"""
    remaining = _get_remaining_seconds()
    st.session_state["timer_duration_seconds"] = remaining
    st.session_state["timer_running"] = False
    st.session_state["timer_paused"] = True


def _resume_timer() -> None:
    """一時停止中のタイマーを再開"""
    duration = st.session_state["timer_duration_seconds"]
    st.session_state["timer_running"] = True
    st.session_state["timer_paused"] = False
    st.session_state["timer_start_time"] = datetime.now()
    st.session_state["timer_duration_seconds"] = duration


def _reset_timer() -> None:
    """タイマーをリセット"""
    st.session_state["timer_running"] = False
    st.session_state["timer_paused"] = False
    st.session_state["timer_start_time"] = None
    st.session_state["timer_duration_seconds"] = 0
    st.session_state["pomodoro_count"] = 0


def _complete_session() -> None:
    """
    現在のセッションを完了して記録し、次のセッションを開始する

    作業セッション完了時はポモドーロカウントを加算し、
    タスク紐づけがあれば作業時間を加算する。
    """
    session_type = st.session_state["timer_session_type"]
    task_id = st.session_state.get("timer_task_id")
    pomodoro_count = st.session_state.get("pomodoro_count", 0)

    if session_type == SESSION_TYPE_WORK:
        pomodoro_count += 1
        st.session_state["pomodoro_count"] = pomodoro_count

        # セッション記録
        work_minutes = st.session_state.get(
            "custom_work_minutes", POMODORO_WORK_MINUTES
        )
        duration_seconds = work_minutes * 60
        save_pomodoro_session(
            user["id"], SESSION_TYPE_WORK, duration_seconds, task_id
        )

        # タスクの作業時間を更新
        if task_id:
            update_task_work_time(task_id, work_minutes)

        # 次のセッション: 4セットごとに長い休憩
        if pomodoro_count % POMODORO_SESSIONS_UNTIL_LONG_BREAK == 0:
            break_minutes = st.session_state.get(
                "custom_long_break_minutes", POMODORO_LONG_BREAK_MINUTES
            )
            _start_timer(SESSION_TYPE_LONG_BREAK, break_minutes * 60)
        else:
            break_minutes = st.session_state.get(
                "custom_short_break_minutes", POMODORO_SHORT_BREAK_MINUTES
            )
            _start_timer(SESSION_TYPE_SHORT_BREAK, break_minutes * 60)

    else:
        # 休憩完了 → 作業へ
        break_duration = st.session_state.get(
            "custom_short_break_minutes", POMODORO_SHORT_BREAK_MINUTES
        )
        if session_type == SESSION_TYPE_LONG_BREAK:
            break_duration = st.session_state.get(
                "custom_long_break_minutes", POMODORO_LONG_BREAK_MINUTES
            )

        save_pomodoro_session(
            user["id"], session_type, break_duration * 60
        )

        work_minutes = st.session_state.get(
            "custom_work_minutes", POMODORO_WORK_MINUTES
        )
        _start_timer(SESSION_TYPE_WORK, work_minutes * 60)


def _skip_session() -> None:
    """現在のセッションをスキップ（記録せず次のセッションへ）"""
    session_type = st.session_state["timer_session_type"]

    if session_type == SESSION_TYPE_WORK:
        # 作業スキップ → 短い休憩（カウントは加算しない）
        break_minutes = st.session_state.get(
            "custom_short_break_minutes", POMODORO_SHORT_BREAK_MINUTES
        )
        _start_timer(SESSION_TYPE_SHORT_BREAK, break_minutes * 60)
    else:
        # 休憩スキップ → 作業
        work_minutes = st.session_state.get(
            "custom_work_minutes", POMODORO_WORK_MINUTES
        )
        _start_timer(SESSION_TYPE_WORK, work_minutes * 60)


# --- UI ---

st.title("⏱️ ポモドーロタイマー")

# タスク選択
tasks = get_tasks_by_date(user["id"], today_str)
incomplete_tasks = [t for t in tasks if not t["is_completed"]]

if incomplete_tasks:
    task_options = ["なし"] + [t["id"] for t in incomplete_tasks]

    def _format_task_option(task_id: str) -> str:
        """タスク選択肢のフォーマット"""
        if task_id == "なし":
            return "タスクなし（フリー作業）"
        for t in incomplete_tasks:
            if t["id"] == task_id:
                return t["title"]
        return task_id

    # タスクページから遷移してきた場合のデフォルト値
    default_task_id = st.session_state.get("timer_task_id")
    default_index = 0
    if default_task_id and default_task_id in task_options:
        default_index = task_options.index(default_task_id)

    selected_task_id = st.selectbox(
        "タスクを選択（オプション）",
        options=task_options,
        index=default_index,
        format_func=_format_task_option,
        key="selected_task_for_timer",
        disabled=st.session_state["timer_running"],
    )

    if selected_task_id != "なし":
        st.session_state["timer_task_id"] = selected_task_id
    else:
        st.session_state["timer_task_id"] = None

st.divider()

# タブ
tab_timer, tab_history = st.tabs(["ポモドーロ", "履歴"])

with tab_timer:
    timer_running = st.session_state["timer_running"]
    timer_paused = st.session_state["timer_paused"]
    session_type = st.session_state["timer_session_type"]

    # セッションタイプ表示
    icon = SESSION_TYPE_ICONS.get(session_type, "")
    label = SESSION_TYPE_LABELS.get(session_type, "")
    pomodoro_count = st.session_state.get("pomodoro_count", 0)

    st.subheader(f"{icon} {label}")
    if pomodoro_count > 0:
        st.caption(f"完了ポモドーロ: {pomodoro_count}セット")

    # 残り時間表示
    if timer_running:
        remaining = _get_remaining_seconds()

        if remaining > 0:
            st.markdown(
                f"<h1 style='text-align: center; font-size: 72px;'>"
                f"{_format_time(remaining)}</h1>",
                unsafe_allow_html=True,
            )

            # プログレスバー
            total_duration = st.session_state["timer_duration_seconds"]
            if total_duration > 0:
                elapsed_ratio = 1 - (remaining / total_duration)
                st.progress(min(elapsed_ratio, 1.0))

            # 更新ボタン
            if st.button("🔄 更新", key="refresh_timer"):
                st.rerun()

            # 自動更新オプション
            if st.checkbox("自動更新（5秒ごと）", value=False):
                time.sleep(5)
                st.rerun()

        else:
            # タイマー完了
            st.success("✓ セッション完了！")
            st.balloons()

            if st.button(
                "次のセッションへ",
                type="primary",
                use_container_width=True,
            ):
                _complete_session()
                st.rerun()

    elif timer_paused:
        # 一時停止中
        paused_remaining = st.session_state["timer_duration_seconds"]
        st.markdown(
            f"<h1 style='text-align: center; font-size: 72px; "
            f"color: #F39C12;'>{_format_time(paused_remaining)}</h1>",
            unsafe_allow_html=True,
        )
        st.caption("⏸️ 一時停止中")

    else:
        # タイマー未稼働
        work_minutes = st.session_state.get(
            "custom_work_minutes", POMODORO_WORK_MINUTES
        )
        st.markdown(
            f"<h1 style='text-align: center; font-size: 72px;'>"
            f"{_format_time(work_minutes * 60)}</h1>",
            unsafe_allow_html=True,
        )

    st.divider()

    # 時間設定
    with st.expander(
        "⚙️ 時間設定",
        expanded=not timer_running and not timer_paused,
    ):
        col_s1, col_s2, col_s3 = st.columns(3)

        with col_s1:
            work_minutes = st.number_input(
                "作業時間（分）",
                min_value=1,
                max_value=60,
                value=st.session_state.get(
                    "custom_work_minutes", POMODORO_WORK_MINUTES
                ),
                disabled=timer_running or timer_paused,
                key="input_work_minutes",
            )

        with col_s2:
            short_break = st.number_input(
                "短い休憩（分）",
                min_value=1,
                max_value=30,
                value=st.session_state.get(
                    "custom_short_break_minutes",
                    POMODORO_SHORT_BREAK_MINUTES,
                ),
                disabled=timer_running or timer_paused,
                key="input_short_break",
            )

        with col_s3:
            long_break = st.number_input(
                "長い休憩（分）",
                min_value=1,
                max_value=60,
                value=st.session_state.get(
                    "custom_long_break_minutes",
                    POMODORO_LONG_BREAK_MINUTES,
                ),
                disabled=timer_running or timer_paused,
                key="input_long_break",
            )

        if not timer_running and not timer_paused:
            st.session_state["custom_work_minutes"] = work_minutes
            st.session_state["custom_short_break_minutes"] = short_break
            st.session_state["custom_long_break_minutes"] = long_break

    st.divider()

    # コントロールボタン
    col_c1, col_c2, col_c3 = st.columns(3)

    with col_c1:
        if not timer_running and not timer_paused:
            # 開始ボタン
            if st.button(
                "▶️ 開始",
                use_container_width=True,
                type="primary",
            ):
                duration = st.session_state.get(
                    "custom_work_minutes", POMODORO_WORK_MINUTES
                ) * 60
                _start_timer(SESSION_TYPE_WORK, duration)
                st.rerun()
        elif timer_paused:
            # 再開ボタン
            if st.button(
                "▶️ 再開",
                use_container_width=True,
                type="primary",
            ):
                _resume_timer()
                st.rerun()
        else:
            # 一時停止ボタン
            if st.button("⏸️ 一時停止", use_container_width=True):
                _pause_timer()
                st.rerun()

    with col_c2:
        if st.button(
            "⏹️ リセット",
            use_container_width=True,
            disabled=not timer_running and not timer_paused,
        ):
            _reset_timer()
            st.rerun()

    with col_c3:
        if st.button(
            "⏭️ スキップ",
            use_container_width=True,
            disabled=not timer_running and not timer_paused,
        ):
            _skip_session()
            st.rerun()

with tab_history:
    sessions = get_pomodoro_sessions_by_date(user["id"], today_str)

    if not sessions:
        st.info("今日のセッション履歴はまだありません")
    else:
        # 統計
        total_work_minutes = sum(
            s["duration_minutes"]
            for s in sessions
            if s["session_type"] == SESSION_TYPE_WORK
        )
        work_session_count = sum(
            1 for s in sessions
            if s["session_type"] == SESSION_TYPE_WORK
        )

        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.metric("今日の総作業時間", f"{total_work_minutes}分")
        with col_m2:
            st.metric("完了セッション", f"{work_session_count}回")

        st.divider()

        # セッション一覧
        st.subheader("セッション履歴")

        for session in sessions:
            session_type = session["session_type"]
            icon = SESSION_TYPE_ICONS.get(session_type, "")
            label = SESSION_TYPE_LABELS.get(session_type, session_type)

            with st.container():
                col_h1, col_h2, col_h3 = st.columns([2, 3, 2])

                with col_h1:
                    st.write(f"{icon} {label}")

                with col_h2:
                    started_at = datetime.fromisoformat(
                        session["started_at"]
                    )
                    st.caption(started_at.strftime("%H:%M"))

                with col_h3:
                    st.caption(f"{session['duration_minutes']}分")
