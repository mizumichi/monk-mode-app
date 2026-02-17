"""
ダッシュボード（エントリーポイント）

認証済みユーザーに今日のタスク概要と達成率を表示する。
左カラムに進捗、中央にタスク一覧、右カラムにクイックアクション。
"""

import streamlit as st
from datetime import date

from components.auth import is_authenticated, logout, get_current_user
from utils.database import get_tasks_by_date, get_task_completion_rate
from utils.constants import WEEKDAY_LABELS

st.set_page_config(
    page_title="モンクモード",
    page_icon="🧘",
    layout="wide",
)

# 認証チェック
if not is_authenticated():
    st.warning("ログインが必要です")
    st.switch_page("pages/0_🔐_Auth.py")
    st.stop()

user = get_current_user()
today = date.today()
today_str = today.isoformat()

# ヘッダー
col1, col2 = st.columns([5, 1])
with col1:
    st.title("🧘 モンクモード支援システム")
    st.caption(
        f"{today.strftime('%Y年%m月%d日')} "
        f"({WEEKDAY_LABELS[today.weekday()]}曜日)"
    )
with col2:
    if st.button("ログアウト", type="secondary"):
        logout()
        st.rerun()

st.divider()

# タスク取得
tasks = get_tasks_by_date(user["id"], today_str)

# メインコンテンツ（3カラム）
col_left, col_center, col_right = st.columns([2, 5, 2])

# 左カラム: 進捗
with col_left:
    st.subheader("📊 進捗")
    st.metric("継続日数", "1日目")
    st.caption("※後のスプリントで実装予定")

    st.divider()

    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t["is_completed"]])
    st.metric("今日のタスク", f"{completed_tasks}/{total_tasks}")

    st.divider()

    # 作業時間統計
    total_work_minutes = sum(
        t.get("total_work_minutes") or 0 for t in tasks
    )
    st.metric("今日の作業時間", f"{total_work_minutes}分")

# 中央カラム: 今日のタスク
with col_center:
    st.subheader("📋 今日のタスク")

    if tasks:
        # 達成率
        completion_rate = get_task_completion_rate(user["id"], today_str)
        st.progress(
            completion_rate,
            text=f"達成率: {int(completion_rate * 100)}%",
        )

        st.write("")

        # タスク表示（最大5件）
        display_tasks = tasks[:5]

        for task in display_tasks:
            col_check, col_task = st.columns([0.5, 9.5])

            with col_check:
                st.checkbox(
                    "",
                    value=task["is_completed"],
                    key=f"home_task_{task['id']}",
                    disabled=True,
                    label_visibility="collapsed",
                )

            with col_task:
                work_info = ""
                work_minutes = task.get("total_work_minutes") or 0
                if work_minutes > 0:
                    work_info = f" ⏱️ {work_minutes}分"

                if task["is_completed"]:
                    st.markdown(
                        f"~~{task['title']}~~ "
                        f"🏷️ {task['category']}{work_info}",
                        help=task.get("description", ""),
                    )
                else:
                    st.markdown(
                        f"**{task['title']}** "
                        f"🏷️ {task['category']}{work_info}",
                        help=task.get("description", ""),
                    )

        # 5件を超える場合
        if len(tasks) > 5:
            st.caption(f"他 {len(tasks) - 5} 件のタスク")

        st.write("")

        if st.button("📋 タスク管理へ", use_container_width=True):
            st.switch_page("pages/1_📋_Tasks.py")

    else:
        st.info("📝 今日のタスクはまだありません")

        if st.button("➕ 最初のタスクを追加", use_container_width=True):
            st.switch_page("pages/1_📋_Tasks.py")

# 右カラム: クイックアクション
with col_right:
    st.subheader("🚀 クイック")

    if st.button("➕ タスク追加", use_container_width=True):
        st.switch_page("pages/1_📋_Tasks.py")

    if st.button("⏱️ タイマー", use_container_width=True):
        st.switch_page("pages/2_⏱️_Timer.py")

    st.divider()

    st.caption("その他の機能は後のスプリントで追加予定")
