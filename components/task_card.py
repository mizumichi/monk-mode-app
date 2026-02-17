"""
タスクカードコンポーネント

タスク情報を受け取りカード形式で表示する再利用可能コンポーネント。
優先度に応じた色分け、完了状態の視覚表現を提供する。
"""

from typing import Optional, Callable, Dict

import streamlit as st

from utils.constants import PRIORITY_COLORS, PRIORITY_LABELS


def render_task_card(
    task: Dict,
    on_complete_toggle: Optional[Callable[[str], bool]] = None,
    on_edit: Optional[Callable[[str], None]] = None,
    on_delete: Optional[Callable[[str], None]] = None,
    show_actions: bool = True,
) -> None:
    """
    タスクカードをレンダリング

    Args:
        task: タスクデータ（id, title, description, category, priority, is_completed）
        on_complete_toggle: 完了切り替え時のコールバック
        on_edit: 編集時のコールバック
        on_delete: 削除時のコールバック
        show_actions: アクションボタンを表示するか
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

        col_check, col_content, col_actions = st.columns([0.5, 8, 1.5])

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

            priority_label = PRIORITY_LABELS.get(task["priority"], task["priority"])
            st.caption(f"🏷️ {task['category']} | 優先度: {priority_label}")

        # アクションボタン
        if show_actions:
            with col_actions:
                btn_col1, btn_col2 = st.columns(2)

                with btn_col1:
                    if st.button("✏️", key=f"edit_{task['id']}", help="編集"):
                        if on_edit:
                            on_edit(task["id"])

                with btn_col2:
                    if st.button("🗑️", key=f"del_{task['id']}", help="削除"):
                        if on_delete:
                            on_delete(task["id"])
