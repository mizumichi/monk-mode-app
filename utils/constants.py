"""
システム全体で使用する定数定義

主要機能:
- タスク関連定数（カテゴリ、優先度、色）
- 習慣関連定数
- ポモドーロ関連定数
- UI関連定数（カラーパレット）
- 認証関連定数
"""

# タスク関連
TASK_CATEGORIES = ["運動", "学習", "健康管理", "自己研鑽", "その他"]

TASK_PRIORITIES = ["高", "中", "低"]

PRIORITY_MAP = {
    "高": "high",
    "中": "medium",
    "低": "low",
}

PRIORITY_LABELS = {
    "high": "高",
    "medium": "中",
    "low": "低",
}

PRIORITY_COLORS = {
    "high": "#FFE5E5",
    "medium": "#FFF4E5",
    "low": "#E5F2FF",
}

MAX_TASKS_PER_DAY = 20

# 習慣関連
MIN_SLEEP_HOURS = 4
MAX_SLEEP_HOURS = 12
DEFAULT_SLEEP_HOURS = 8
MAX_SCREEN_TIME_MINUTES = 180  # 3時間

# ポモドーロ
POMODORO_WORK_MINUTES = 25
POMODORO_SHORT_BREAK_MINUTES = 5
POMODORO_LONG_BREAK_MINUTES = 15
POMODORO_SESSIONS_UNTIL_LONG_BREAK = 4

# ポモドーロセッションタイプ
SESSION_TYPE_WORK = "work"
SESSION_TYPE_SHORT_BREAK = "short_break"
SESSION_TYPE_LONG_BREAK = "long_break"

SESSION_TYPE_LABELS = {
    SESSION_TYPE_WORK: "作業",
    SESSION_TYPE_SHORT_BREAK: "短い休憩",
    SESSION_TYPE_LONG_BREAK: "長い休憩",
}

SESSION_TYPE_ICONS = {
    SESSION_TYPE_WORK: "🔥",
    SESSION_TYPE_SHORT_BREAK: "☕",
    SESSION_TYPE_LONG_BREAK: "🌟",
}

# フィルタ用ラベル
FILTER_ALL_LABEL = "すべて"

PRIORITY_REVERSE_MAP = {
    "高": "high",
    "中": "medium",
    "低": "low",
}

# 認証関連
MIN_PASSWORD_LENGTH = 8
MAX_DISPLAY_NAME_LENGTH = 100
MAX_TASK_TITLE_LENGTH = 200

# UI関連
COLORS = {
    "primary": "#2C3E50",
    "secondary": "#7F8C8D",
    "accent": "#27AE60",
    "success": "#27AE60",
    "warning": "#F39C12",
    "danger": "#E74C3C",
    "background": "#F8F9FA",
    "card": "#FFFFFF",
    "border": "#E0E0E0",
    "text": "#2C3E50",
}

WEEKDAY_LABELS = ["月", "火", "水", "木", "金", "土", "日"]
