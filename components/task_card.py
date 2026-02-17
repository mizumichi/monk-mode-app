"""
タスクカードコンポーネント

タスク情報を受け取りカード形式で表示する再利用可能コンポーネント。
優先度に応じた色分け、完了状態の視覚表現を提供する。

Sprint 2追加機能:
- 並び替えボタン（↑↓）
- タイマー起動ボタン
- 作業時間表示
"""

from typing import Optional, Callable, Dict

import streamlit as st

from utils.constants import PRIORITY_COLORS, PRIORITY_LABELS


def render_task_card(
    task: Dict,
    on_complete_toggle: Optional[Callable[[str], bool]] = None,
    on_edit: Optional[Callable[[str], None]] = None,
    on_delete: Optional[Callable[[str], None]] = None,
    on_move_up: Optional[Callable[[str], None]] = None,
    on_move_down: Optional[Callable[[str], None]] = None,
    on_start_timer: Optional[Callable[[str], None]] = None,
    show_actions: bool = True,
    is_first: bool = False,
    is_last: bool = False,
) -> None:
    """
    タスクカードをレンダリング

    Args:
        task: タスクデータ（id, title, description, category, priority, is_completed）
        on_complete_toggle: 完了切り替え時のコールバック
        on_edit: 編集時のコールバック
        on_delete: 削除時のコールバック
        on_move_up: 上へ移動時のコールバック
        on_move_down: 下へ移動時のコールバック
        on_start_timer: タイマー起動時のコールバック
        show_actions: アクションボタンを表示するか
        is_first: 最上位のタスクか（↑ボタン無効化）
        is_last: 最下位のタスクか（↓ボタン無効化）
    """
    bg_color = PRIORITY_COLORS.get(task["priority"], "#F0F0F0")
    if task["is_completed"]:
        bg_color = "#F5F5F5"

    border_color = "#28a745" if task["is_completed"] else "#6c757d"

    with st.container():
        st.markdown(
            f"""<div style="
                background-color: {bg_color};
                padding: 0.5rem 1rem;
                border-radius: 8px;
                margin: 0.25rem 0;
                border-left: 4px solid {border_color};
            "></div>""",
            unsafe_allow_html=True,
        )

        col_check, col_content, col_actions = st.columns([0.5, 7, 2.5])

        # チェックボックス
        with col_check:
            checked = st.checkbox(
                "完了",
                value=task["is_completed"],
                key=f"check_{task['id']}",
                label_visibility="collapsed",
            )

            if checked != task["is_completed"] and on_complete_toggle:
                on_complete_toggle(task["id"])
                st.rerun()

        # タスク内容
        with col_content:
            if task["is_completed"]:
                st.markdown(
                    f"<p style='text-decoration: line-through; color: #999;'>"
                    f"<strong>{task['title']}</strong></p>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(f"**{task['title']}**")

            if task.get("description"):
                st.caption(task["description"])

            priority_label = PRIORITY_LABELS.get(
                task["priority"], task["priority"]
            )
            meta_parts = [
                f"🏷️ {task['category']}",
                f"優先度: {priority_label}",
            ]

            # 作業時間表示
            work_minutes = task.get("total_work_minutes") or 0
            if work_minutes > 0:
                meta_parts.append(f"⏱️ {work_minutes}分")

            st.caption(" | ".join(meta_parts))

        # アクションボタン
        if show_actions:
            with col_actions:
                btn_cols = st.columns(5)

                with btn_cols[0]:
                    if st.button(
                        "⏱️",
                        key=f"timer_{task['id']}",
                        help="タイマー",
                        disabled=task["is_completed"],
                    ):
                        if on_start_timer:
                            on_start_timer(task["id"])

                with btn_cols[1]:
                    if st.button(
                        "↑",
                        key=f"up_{task['id']}",
                        disabled=is_first,
                        help="上へ",
                    ):
                        if on_move_up:
                            on_move_up(task["id"])

                with btn_cols[2]:
                    if st.button(
                        "↓",
                        key=f"down_{task['id']}",
                        disabled=is_last,
                        help="下へ",
                    ):
                        if on_move_down:
                            on_move_down(task["id"])

                with btn_cols[3]:
                    if st.button(
                        "✏️",
                        key=f"edit_{task['id']}",
                        help="編集",
                    ):
                        if on_edit:
                            on_edit(task["id"])

                with btn_cols[4]:
                    if st.button(
                        "🗑️",
                        key=f"del_{task['id']}",
                        help="削除",
                    ):
                        if on_delete:
                            on_delete(task["id"])
