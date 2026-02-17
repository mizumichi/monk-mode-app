"""
データベース操作モジュール

daily_tasks / pomodoro_sessionsテーブルに対するCRUD操作を提供する。
すべてのDB操作はこのモジュールに集約する。

主要機能:
- get_tasks_by_date: 指定日のタスク一覧取得
- create_task: タスク作成
- update_task: タスク更新
- delete_task: タスク削除
- toggle_task_completion: タスク完了状態の切り替え
- get_task_completion_rate: タスク完了率の計算
- move_task_up / move_task_down: タスクの並び替え
- get_incomplete_tasks: 未完了タスク取得
- carryover_tasks: タスク繰り越し
- save_pomodoro_session: ポモドーロセッション保存
- get_pomodoro_sessions_by_date: セッション履歴取得
- update_task_work_time: タスク作業時間更新
"""

import logging
from datetime import datetime, timedelta
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
            .order("display_order")\
            .execute()

        return response.data

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


# --- Sprint 2: タスク並び替え ---


def move_task_up(task_id: str, user_id: str, task_date: str) -> bool:
    """
    タスクを上に移動

    現在のタスクより1つ上のタスクとdisplay_orderを入れ替える。

    Args:
        task_id: 移動するタスクID
        user_id: ユーザーID
        task_date: 対象日付（YYYY-MM-DD形式）

    Returns:
        成功時True
    """
    try:
        current_task = supabase.table("daily_tasks")\
            .select("display_order")\
            .eq("id", task_id)\
            .single()\
            .execute()

        current_order = current_task.data["display_order"]

        prev_task = supabase.table("daily_tasks")\
            .select("id, display_order")\
            .eq("user_id", user_id)\
            .eq("task_date", task_date)\
            .lt("display_order", current_order)\
            .order("display_order", desc=True)\
            .limit(1)\
            .execute()

        if not prev_task.data:
            return False

        prev_order = prev_task.data[0]["display_order"]
        prev_id = prev_task.data[0]["id"]

        supabase.table("daily_tasks")\
            .update({"display_order": prev_order})\
            .eq("id", task_id)\
            .execute()

        supabase.table("daily_tasks")\
            .update({"display_order": current_order})\
            .eq("id", prev_id)\
            .execute()

        logger.info("Moved task %s up", task_id)
        return True

    except Exception as e:
        logger.error("Error moving task up %s: %s", task_id, e)
        return False


def move_task_down(task_id: str, user_id: str, task_date: str) -> bool:
    """
    タスクを下に移動

    現在のタスクより1つ下のタスクとdisplay_orderを入れ替える。

    Args:
        task_id: 移動するタスクID
        user_id: ユーザーID
        task_date: 対象日付（YYYY-MM-DD形式）

    Returns:
        成功時True
    """
    try:
        current_task = supabase.table("daily_tasks")\
            .select("display_order")\
            .eq("id", task_id)\
            .single()\
            .execute()

        current_order = current_task.data["display_order"]

        next_task = supabase.table("daily_tasks")\
            .select("id, display_order")\
            .eq("user_id", user_id)\
            .eq("task_date", task_date)\
            .gt("display_order", current_order)\
            .order("display_order")\
            .limit(1)\
            .execute()

        if not next_task.data:
            return False

        next_order = next_task.data[0]["display_order"]
        next_id = next_task.data[0]["id"]

        supabase.table("daily_tasks")\
            .update({"display_order": next_order})\
            .eq("id", task_id)\
            .execute()

        supabase.table("daily_tasks")\
            .update({"display_order": current_order})\
            .eq("id", next_id)\
            .execute()

        logger.info("Moved task %s down", task_id)
        return True

    except Exception as e:
        logger.error("Error moving task down %s: %s", task_id, e)
        return False


# --- Sprint 2: 繰り越し機能 ---


def get_incomplete_tasks(user_id: str, task_date: str) -> List[Dict]:
    """
    指定日の未完了タスクを取得

    Args:
        user_id: ユーザーID
        task_date: 日付（YYYY-MM-DD形式）

    Returns:
        未完了タスクのリスト
    """
    try:
        response = supabase.table("daily_tasks")\
            .select("*")\
            .eq("user_id", user_id)\
            .eq("task_date", task_date)\
            .eq("is_completed", False)\
            .order("display_order")\
            .execute()

        return response.data

    except Exception as e:
        logger.error("Error fetching incomplete tasks: %s", e)
        return []


def carryover_tasks(task_ids: List[str], new_date: str) -> bool:
    """
    タスクを新しい日付に繰り越す

    元のタスクの日付を更新する方式（移動）。
    繰り越し先の日付で最後尾に追加される。

    Args:
        task_ids: 繰り越すタスクIDのリスト
        new_date: 新しい日付（YYYY-MM-DD形式）

    Returns:
        成功時True
    """
    try:
        for task_id in task_ids:
            supabase.table("daily_tasks")\
                .update({
                    "task_date": new_date,
                    "updated_at": datetime.now().isoformat(),
                })\
                .eq("id", task_id)\
                .execute()

        logger.info("Carried over %d tasks to %s", len(task_ids), new_date)
        return True

    except Exception as e:
        logger.error("Error carrying over tasks: %s", e)
        return False


# --- Sprint 2: ポモドーロセッション ---


def save_pomodoro_session(
    user_id: str,
    session_type: str,
    duration_seconds: int,
    task_id: Optional[str] = None,
) -> Optional[Dict]:
    """
    ポモドーロセッションを記録

    Args:
        user_id: ユーザーID
        session_type: 'work', 'short_break', 'long_break'
        duration_seconds: セッション時間（秒）
        task_id: 関連タスクID（オプション）

    Returns:
        保存されたセッション。失敗時はNone。
    """
    try:
        now = datetime.now()
        started_at = (now - timedelta(seconds=duration_seconds)).isoformat()

        session_data = {
            "user_id": user_id,
            "session_type": session_type,
            "duration_minutes": duration_seconds // 60,
            "started_at": started_at,
            "ended_at": now.isoformat(),
            "completed": True,
        }

        if task_id:
            session_data["task_id"] = task_id

        response = supabase.table("pomodoro_sessions")\
            .insert(session_data)\
            .execute()

        logger.info("Saved pomodoro session: %s", session_type)
        return response.data[0] if response.data else None

    except Exception as e:
        logger.error("Error saving pomodoro session: %s", e)
        return None


def get_pomodoro_sessions_by_date(
    user_id: str, target_date: str
) -> List[Dict]:
    """
    指定日のポモドーロセッション一覧を取得

    Args:
        user_id: ユーザーID
        target_date: 対象日付（YYYY-MM-DD形式）

    Returns:
        セッションのリスト
    """
    try:
        response = supabase.table("pomodoro_sessions")\
            .select("*")\
            .eq("user_id", user_id)\
            .gte("started_at", f"{target_date}T00:00:00")\
            .lte("started_at", f"{target_date}T23:59:59")\
            .order("started_at", desc=True)\
            .execute()

        return response.data

    except Exception as e:
        logger.error("Error fetching pomodoro sessions: %s", e)
        return []


def update_task_work_time(task_id: str, minutes: int) -> bool:
    """
    タスクの作業時間を加算更新

    Args:
        task_id: タスクID
        minutes: 追加する作業時間（分）

    Returns:
        成功時True
    """
    try:
        task = supabase.table("daily_tasks")\
            .select("total_work_minutes")\
            .eq("id", task_id)\
            .single()\
            .execute()

        current_minutes = task.data.get("total_work_minutes") or 0
        new_total = current_minutes + minutes

        supabase.table("daily_tasks")\
            .update({"total_work_minutes": new_total})\
            .eq("id", task_id)\
            .execute()

        logger.info(
            "Updated task %s work time: +%d min (total: %d)",
            task_id, minutes, new_total,
        )
        return True

    except Exception as e:
        logger.error("Error updating task work time %s: %s", task_id, e)
        return False
