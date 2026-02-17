"""
タスク管理ページ

デイリータスクの追加・編集・削除・完了チェックを提供する。

Sprint 2追加機能:
- カテゴリ・優先度フィルタ
- タスクの並び替え（↑↓ボタン）
- 未完了タスクの翌日繰り越し
- タスクからタイマー起動
"""

import streamlit as st
from datetime import date, timedelta

from components.auth import is_authenticated, get_current_user
from components.task_card import render_task_card
from utils.database import (
    get_tasks_by_date,
    create_task,
    update_task,
    delete_task,
    toggle_task_completion,
    move_task_up,
    move_task_down,
    get_incomplete_tasks,
    carryover_tasks,
)
from utils.constants import (
    TASK_CATEGORIES,
    TASK_PRIORITIES,
    PRIORITY_MAP,
    PRIORITY_REVERSE_MAP,
    WEEKDAY_LABELS,
    FILTER_ALL_LABEL,
)

st.set_page_config(
    page_title="タスク管理",
    page_icon="📋",
    layout="wide",
)

# 認証チェック
if not is_authenticated():
    st.switch_page("pages/0_🔐_Auth.py")

user = get_current_user()
today = date.today()
today_str = today.isoformat()

# タイトル
st.title("📋 今日のタスク")
st.caption(
    f"{today.strftime('%Y年%m月%d日')} "
    f"({WEEKDAY_LABELS[today.weekday()]}曜日)"
)

# --- 前日の未完了タスク繰り越し ---
yesterday = (today - timedelta(days=1)).isoformat()
yesterday_incomplete = get_incomplete_tasks(user["id"], yesterday)

if yesterday_incomplete:
    with st.expander(
        f"⚠️ 前日の未完了タスク（{len(yesterday_incomplete)}件）",
        expanded=True,
    ):
        st.info("繰り越すタスクを選択してください")

        selected_tasks = []
        for task in yesterday_incomplete:
            if st.checkbox(
                task["title"],
                key=f"carryover_{task['id']}",
            ):
                selected_tasks.append(task["id"])

        if st.button(
            "選択したタスクを今日に繰り越す",
            disabled=not selected_tasks,
        ):
            if carryover_tasks(selected_tasks, today_str):
                st.success(
                    f"✓ {len(selected_tasks)}件のタスクを繰り越しました"
                )
                st.rerun()
            else:
                st.error("繰り越しに失敗しました")

# --- タスク追加フォーム ---
with st.expander("➕ 新しいタスクを追加", expanded=False):
    with st.form("add_task_form", clear_on_submit=True):
        title = st.text_input("タスク名*", max_chars=200)
        description = st.text_area("説明（任意）")

        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("カテゴリ*", TASK_CATEGORIES)
        with col2:
            priority_display = st.selectbox(
                "優先度*", TASK_PRIORITIES, index=1
            )
            priority = PRIORITY_MAP[priority_display]

        if st.form_submit_button("追加", use_container_width=True):
            if not title.strip():
                st.error("タスク名を入力してください")
            else:
                task_data = {
                    "title": title.strip(),
                    "description": description.strip(),
                    "category": category,
                    "priority": priority,
                    "task_date": today_str,
                }

                created = create_task(user["id"], task_data)
                if created:
                    st.success("タスクを追加しました")
                    st.rerun()
                else:
                    st.error("タスクの追加に失敗しました")

st.divider()

# --- フィルタ ---
col_f1, col_f2, col_f3 = st.columns([2, 2, 3])

with col_f1:
    show_completed = st.checkbox("完了済みを表示", value=True)

with col_f2:
    selected_category = st.selectbox(
        "カテゴリ",
        [FILTER_ALL_LABEL] + TASK_CATEGORIES,
        key="filter_category",
    )

with col_f3:
    selected_priority = st.selectbox(
        "優先度",
        [FILTER_ALL_LABEL] + TASK_PRIORITIES,
        key="filter_priority",
    )

# --- タスク取得 ---
tasks = get_tasks_by_date(user["id"], today_str)

# フィルタ適用
if not show_completed:
    tasks = [t for t in tasks if not t["is_completed"]]

if selected_category != FILTER_ALL_LABEL:
    tasks = [t for t in tasks if t["category"] == selected_category]

if selected_priority != FILTER_ALL_LABEL:
    priority_value = PRIORITY_REVERSE_MAP[selected_priority]
    tasks = [t for t in tasks if t["priority"] == priority_value]


# --- コールバック関数 ---


def _on_edit(task_id: str) -> None:
    """編集モードへ切り替え"""
    st.session_state[f"editing_{task_id}"] = True


def _on_delete(task_id: str) -> None:
    """削除確認モードへ切り替え"""
    st.session_state[f"deleting_{task_id}"] = True


def _on_move_up(task_id: str) -> None:
    """タスクを上へ移動"""
    move_task_up(task_id, user["id"], today_str)
    st.rerun()


def _on_move_down(task_id: str) -> None:
    """タスクを下へ移動"""
    move_task_down(task_id, user["id"], today_str)
    st.rerun()


def _on_start_timer(task_id: str) -> None:
    """タスクに紐づけてタイマーページへ遷移"""
    st.session_state["timer_task_id"] = task_id
    st.switch_page("pages/2_⏱️_Timer.py")


# --- タスク一覧表示 ---
if not tasks:
    st.info("📝 今日のタスクはまだありません")
else:
    st.subheader(f"タスク一覧（{len(tasks)}件）")

    for idx, task in enumerate(tasks):
        editing_key = f"editing_{task['id']}"
        deleting_key = f"deleting_{task['id']}"

        # 編集モード
        if st.session_state.get(editing_key):
            with st.form(f"edit_form_{task['id']}"):
                new_title = st.text_input(
                    "タスク名", value=task["title"], max_chars=200
                )
                new_description = st.text_area(
                    "説明", value=task.get("description", "")
                )

                col1, col2 = st.columns(2)
                with col1:
                    current_cat_index = (
                        TASK_CATEGORIES.index(task["category"])
                        if task["category"] in TASK_CATEGORIES
                        else 0
                    )
                    new_category = st.selectbox(
                        "カテゴリ",
                        TASK_CATEGORIES,
                        index=current_cat_index,
                        key=f"edit_cat_{task['id']}",
                    )
                with col2:
                    priority_values = ["high", "medium", "low"]
                    current_pri_index = (
                        priority_values.index(task["priority"])
                        if task["priority"] in priority_values
                        else 1
                    )
                    new_priority_display = st.selectbox(
                        "優先度",
                        TASK_PRIORITIES,
                        index=current_pri_index,
                        key=f"edit_pri_{task['id']}",
                    )
                    new_priority = PRIORITY_MAP[new_priority_display]

                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button(
                        "保存", use_container_width=True
                    ):
                        updates = {
                            "title": new_title.strip(),
                            "description": new_description.strip(),
                            "category": new_category,
                            "priority": new_priority,
                        }
                        if update_task(task["id"], updates):
                            st.success("タスクを更新しました")
                            del st.session_state[editing_key]
                            st.rerun()
                        else:
                            st.error("更新に失敗しました")

                with col_cancel:
                    if st.form_submit_button(
                        "キャンセル", use_container_width=True
                    ):
                        del st.session_state[editing_key]
                        st.rerun()

        # 削除確認
        elif st.session_state.get(deleting_key):
            st.warning(f"「{task['title']}」を削除しますか？")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "削除する",
                    key=f"confirm_del_{task['id']}",
                    type="primary",
                ):
                    if delete_task(task["id"]):
                        st.success("タスクを削除しました")
                        del st.session_state[deleting_key]
                        st.rerun()
                    else:
                        st.error("削除に失敗しました")
            with col2:
                if st.button(
                    "キャンセル", key=f"cancel_del_{task['id']}"
                ):
                    del st.session_state[deleting_key]
                    st.rerun()

        # 通常表示
        else:
            render_task_card(
                task,
                on_complete_toggle=toggle_task_completion,
                on_edit=_on_edit,
                on_delete=_on_delete,
                on_move_up=_on_move_up,
                on_move_down=_on_move_down,
                on_start_timer=_on_start_timer,
                is_first=(idx == 0),
                is_last=(idx == len(tasks) - 1),
            )
