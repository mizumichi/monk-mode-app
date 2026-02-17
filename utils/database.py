"""
データベース操作モジュール

daily_tasksテーブルに対するCRUD操作を提供する。
すべてのDB操作はこのモジュールに集約する。

主要機能:
- get_tasks_by_date: 指定日のタスク一覧取得
- create_task: タスク作成
- update_task: タスク更新
- delete_task: タスク削除
- toggle_task_completion: タスク完了状態の切り替え
- get_task_completion_rate: タスク完了率の計算
"""

import logging
from datetime import datetime
from typing import List, Dict, Optional

from utils.supabase_client import supabase

logger = logging.getLogger(__name__)


def get_tasks_by_date(user_id: str, task_date: str) -> List[Dict]:
    """
    指定日のタスク一覧を取得

    未完了タスクを先に、優先度の高い順に返す。

    Args:
        user_id: ユーザーID
        task_date: 対象日付（YYYY-MM-DD形式）

    Returns:
        タスクのリスト
    """
    try:
        response = supabase.table("daily_tasks")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("task_date", task_date)\
            .order("is_completed")\
            .order("created_at")\
            .execute()

        # アプリ側で優先度ソート（Supabaseはカスタムソート順未対応のため）
        priority_order = {"high": 0, "medium": 1, "low": 2}
        tasks = response.data
        tasks.sort(key=lambda t: (
            t["is_completed"],
            priority_order.get(t["priority"], 1),
            t["created_at"],
        ))

        return tasks

    except Exception as e:
        logger.error("Error fetching tasks: %s", e)
        return []


def create_task(user_id: str, task_data: Dict) -> Optional[Dict]:
    """
    新規タスクを作成

    display_orderは既存タスクの最大値+1が自動設定される。

    Args:
        user_id: ユーザーID
        task_data: タスクデータ（title, description, category, priority, task_date）

    Returns:
        作成されたタスク。失敗時はNone。
    """
    try:
        # display_orderを計算
        max_order_response = supabase.table("daily_tasks")\
            .select("display_order")\
            .eq("user_id", user_id)\
            .eq("task_date", task_data["task_date"])\
            .order("display_order", desc=True)\
            .limit(1)\
            .execute()

        if max_order_response.data:
            new_order = max_order_response.data[0]["display_order"] + 1
        else:
            new_order = 0

        task_data["user_id"] = user_id
        task_data["display_order"] = new_order

        response = supabase.table("daily_tasks")\
            .insert(task_data)\
            .execute()

        logger.info("Created task: %s", response.data[0]["id"])
        return response.data[0] if response.data else None

    except Exception as e:
        logger.error("Error creating task: %s", e)
        return None


def update_task(task_id: str, updates: Dict) -> bool:
    """
    タスクを更新

    Args:
        task_id: タスクID
        updates: 更新内容の辞書

    Returns:
        成功時True
    """
    try:
        updates["updated_at"] = datetime.now().isoformat()

        supabase.table("daily_tasks")\
            .update(updates)\
            .eq("id", task_id)\
            .execute()

        logger.info("Updated task: %s", task_id)
        return True

    except Exception as e:
        logger.error("Error updating task %s: %s", task_id, e)
        return False


def delete_task(task_id: str) -> bool:
    """
    タスクを物理削除

    Args:
        task_id: タスクID

    Returns:
        成功時True
    """
    try:
        supabase.table("daily_tasks")\
            .delete()\
            .eq("id", task_id)\
            .execute()

        logger.info("Deleted task: %s", task_id)
        return True

    except Exception as e:
        logger.error("Error deleting task %s: %s", task_id, e)
        return False


def toggle_task_completion(task_id: str) -> bool:
    """
    タスクの完了状態を切り替え

    完了時にはcompleted_atにタイムスタンプを記録し、
    未完了に戻す場合はNoneにする。

    Args:
        task_id: タスクID

    Returns:
        成功時True
    """
    try:
        response = supabase.table("daily_tasks")\
            .select("is_completed")\
            .eq("id", task_id)\
            .single()\
            .execute()

        current_status = response.data["is_completed"]
        new_status = not current_status

        updates = {
            "is_completed": new_status,
            "completed_at": datetime.now().isoformat() if new_status else None,
            "updated_at": datetime.now().isoformat(),
        }

        supabase.table("daily_tasks")\
            .update(updates)\
            .eq("id", task_id)\
            .execute()

        logger.info("Toggled task %s: completed=%s", task_id, new_status)
        return True

    except Exception as e:
        logger.error("Error toggling task completion %s: %s", task_id, e)
        return False


def get_task_completion_rate(user_id: str, task_date: str) -> float:
    """
    指定日のタスク完了率を計算

    Args:
        user_id: ユーザーID
        task_date: 対象日付（YYYY-MM-DD形式）

    Returns:
        完了率（0.0〜1.0）。タスクが0件の場合は0.0。
    """
    try:
        tasks = get_tasks_by_date(user_id, task_date)

        if not tasks:
            return 0.0

        total = len(tasks)
        completed = len([t for t in tasks if t["is_completed"]])

        return completed / total

    except Exception as e:
        logger.error("Error calculating completion rate: %s", e)
        return 0.0
