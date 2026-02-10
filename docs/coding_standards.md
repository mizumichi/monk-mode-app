# モンクモード支援システム - コーディング規約・ベストプラクティス

## 📋 目次
1. [Python基本規約](#python基本規約)
2. [Streamlit特有の規約](#streamlit特有の規約)
3. [データベース操作規約](#データベース操作規約)
4. [エラーハンドリング規約](#エラーハンドリング規約)
5. [セキュリティ規約](#セキュリティ規約)
6. [パフォーマンス規約](#パフォーマンス規約)
7. [ドキュメンテーション規約](#ドキュメンテーション規約)
8. [Git運用規約](#git運用規約)

---

## Python基本規約

### 1.1 PEP 8準拠
**必須**: Python公式スタイルガイド（PEP 8）に従う

```python
# ✅ GOOD
def calculate_task_completion_rate(user_id: str, date: str) -> float:
    """タスク完了率を計算する"""
    pass

# ❌ BAD
def calcTaskCompRate(userId,date):  # キャメルケース、型ヒントなし
    pass
```

### 1.2 命名規則

#### 変数・関数名
- **スネークケース**使用: `user_id`, `task_list`
- **動詞で始める**（関数）: `get_tasks()`, `create_user()`, `update_profile()`
- **意味が明確**: `x`, `tmp`, `data1` などは禁止

```python
# ✅ GOOD
def get_user_tasks_by_date(user_id: str, target_date: str) -> list:
    completed_tasks = []
    pending_tasks = []
    return completed_tasks + pending_tasks

# ❌ BAD
def gettasks(uid, d):  # 省略しすぎ
    lst = []
    x = []
    return lst + x
```

#### クラス名
- **パスカルケース**: `TaskManager`, `UserProfile`
- **名詞で終わる**: `DatabaseClient`, `AuthenticationHandler`

```python
# ✅ GOOD
class HabitTracker:
    pass

# ❌ BAD
class habit_tracker:  # スネークケース禁止
    pass
```

#### 定数
- **大文字スネークケース**: `MAX_TASKS_PER_DAY`, `DEFAULT_SLEEP_HOURS`

```python
# ✅ GOOD - utils/constants.py
MAX_TASKS_PER_DAY = 20
DEFAULT_SLEEP_HOURS = 8
POMODORO_WORK_MINUTES = 25

# ❌ BAD
maxTasks = 20  # 定数が明確でない
```

### 1.3 型ヒント（必須）
**すべての関数に型ヒントを付ける**

```python
# ✅ GOOD
from typing import Optional, List, Dict
from datetime import date

def get_tasks_by_date(
    user_id: str, 
    target_date: date,
    include_completed: bool = True
) -> List[Dict[str, any]]:
    """指定日のタスク一覧を取得"""
    pass

# ❌ BAD
def get_tasks_by_date(user_id, target_date, include_completed=True):
    pass
```

### 1.4 インポート順序
**PEP 8に従った3セクション構成**

```python
# ✅ GOOD
# 1. 標準ライブラリ
import os
from datetime import datetime, date
from typing import Optional, List, Dict

# 2. サードパーティライブラリ
import streamlit as st
import pandas as pd
from supabase import Client

# 3. ローカルモジュール
from utils.database import get_tasks
from components.auth import is_authenticated

# ❌ BAD - ランダムな順序
import streamlit as st
from utils.database import get_tasks
import os
from datetime import datetime
```

---

## Streamlit特有の規約

### 2.1 ページ構成の標準テンプレート
**すべてのページで以下の構造を守る**

```python
"""
ページの説明を記載
"""
import streamlit as st
from datetime import date
from typing import Optional

# ローカルインポート
from components.auth import is_authenticated, get_current_user
from utils.database import get_data

# ページ設定（必須・最初に記載）
st.set_page_config(
    page_title="ページ名",
    page_icon="📋",
    layout="wide"  # または "centered"
)

# 認証チェック（認証必要なページのみ）
if not is_authenticated():
    st.warning("ログインが必要です")
    st.switch_page("pages/0_🔐_Auth.py")
    st.stop()

# ユーザー情報取得
user = get_current_user()

# ヘッダー（必須）
st.title("📋 ページタイトル")
st.divider()

# メインコンテンツ
# ...

# フッター（任意）
```

### 2.2 セッション状態の管理
**統一的なキー命名規則**

```python
# ✅ GOOD - 用途別プレフィックス
# 認証関連
st.session_state['user']
st.session_state['authenticated']

# データキャッシュ
st.session_state['tasks_cache']
st.session_state['habits_cache']

# UI状態
st.session_state['editing_task_id']
st.session_state['selected_date']
st.session_state['filter_category']

# タイマー
st.session_state['timer_running']
st.session_state['timer_start_time']

# ❌ BAD
st.session_state['usr']  # 省略
st.session_state['data1']  # 不明確
st.session_state['temp']  # 一時的？何の？
```

**初期化の統一パターン**

```python
# ✅ GOOD - 専用関数で初期化
def initialize_session_state():
    """セッション状態を初期化"""
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'user' not in st.session_state:
        st.session_state['user'] = None
    if 'tasks_cache' not in st.session_state:
        st.session_state['tasks_cache'] = {}

# ページの最初で呼び出す
initialize_session_state()

# ❌ BAD - ページ内で散在
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
# ... 50行後
if 'user' not in st.session_state:
    st.session_state['user'] = None
```

### 2.3 フォーム処理の標準パターン

```python
# ✅ GOOD - 明確な構造
with st.form("task_form", clear_on_submit=True):
    title = st.text_input("タスク名*", max_chars=200)
    description = st.text_area("説明", max_chars=1000)
    
    col1, col2 = st.columns(2)
    with col1:
        category = st.selectbox("カテゴリ", TASK_CATEGORIES)
    with col2:
        priority = st.selectbox("優先度", TASK_PRIORITIES)
    
    submitted = st.form_submit_button("追加", use_container_width=True)
    
    if submitted:
        # バリデーション
        if not title:
            st.error("タスク名は必須です")
            st.stop()
        
        # 処理実行
        try:
            result = create_task(user['id'], {
                "title": title,
                "description": description,
                "category": category,
                "priority": priority
            })
            st.success("✅ タスクを追加しました")
            st.rerun()  # リロード
        except Exception as e:
            st.error(f"❌ エラー: {str(e)}")

# ❌ BAD - フォームなしの直接入力
title = st.text_input("タスク名")
if st.button("追加"):  # フォーム外のボタン
    # 状態管理が複雑になる
```

### 2.4 キャッシング戦略

```python
# ✅ GOOD - 適切なキャッシング
@st.cache_data(ttl=300)  # 5分キャッシュ
def get_user_statistics(user_id: str) -> Dict:
    """ユーザー統計を取得（重い処理）"""
    # データベース集計処理
    return statistics

@st.cache_resource
def get_database_connection():
    """データベース接続をキャッシュ"""
    return supabase

# 頻繁に変わるデータはキャッシュしない
def get_today_tasks(user_id: str, date: str) -> List[Dict]:
    """今日のタスクを取得（キャッシュなし）"""
    return fetch_tasks()

# ❌ BAD
@st.cache_data  # TTLなし、永久キャッシュ
def get_today_tasks(user_id: str):
    # 今日のタスクなのに更新されない
    pass
```

---

## データベース操作規約

### 3.1 CRUD操作の統一パターン
**utils/database.py に集約**

```python
# ✅ GOOD - 標準テンプレート
from utils.supabase_client import supabase
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

def get_tasks_by_date(user_id: str, date: str) -> List[Dict]:
    """
    指定日のタスク一覧を取得
    
    Args:
        user_id: ユーザーID
        date: 対象日付（YYYY-MM-DD形式）
    
    Returns:
        タスクのリスト
    
    Raises:
        Exception: データベースエラー時
    """
    try:
        response = supabase.table('daily_tasks')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('task_date', date)\
            .order('display_order')\
            .execute()
        
        logger.info(f"Fetched {len(response.data)} tasks for user {user_id}")
        return response.data
        
    except Exception as e:
        logger.error(f"Error fetching tasks: {e}")
        raise  # 再スロー

def create_task(user_id: str, task_data: Dict) -> Dict:
    """
    新規タスクを作成
    
    Args:
        user_id: ユーザーID
        task_data: タスクデータ
    
    Returns:
        作成されたタスク
    """
    try:
        # バリデーション
        required_fields = ['title', 'category', 'priority', 'task_date']
        for field in required_fields:
            if field not in task_data:
                raise ValueError(f"必須フィールドが不足: {field}")
        
        # データ挿入
        task_data['user_id'] = user_id
        response = supabase.table('daily_tasks')\
            .insert(task_data)\
            .execute()
        
        logger.info(f"Created task: {response.data[0]['id']}")
        return response.data[0]
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise

# ❌ BAD - エラーハンドリングなし、ドキュメントなし
def get_tasks(uid, d):
    resp = supabase.table('daily_tasks').select('*').eq('user_id', uid).eq('task_date', d).execute()
    return resp.data
```

### 3.2 トランザクション処理
**複数操作は一貫性を保証**

```python
# ✅ GOOD
def complete_task_and_log(task_id: str, user_id: str) -> bool:
    """タスク完了とログ記録をセットで実行"""
    try:
        # 1. タスク更新
        supabase.table('daily_tasks')\
            .update({
                'is_completed': True,
                'completed_at': datetime.now().isoformat()
            })\
            .eq('id', task_id)\
            .execute()
        
        # 2. ログ記録
        supabase.table('task_logs')\
            .insert({
                'user_id': user_id,
                'task_id': task_id,
                'action': 'completed'
            })\
            .execute()
        
        return True
        
    except Exception as e:
        logger.error(f"Transaction failed: {e}")
        # ロールバックは手動で実装（必要に応じて）
        return False

# ❌ BAD - 片方失敗したら不整合
def complete_task(task_id):
    supabase.table('daily_tasks').update({'is_completed': True}).eq('id', task_id).execute()
    # ここでエラーが起きたら？
    supabase.table('task_logs').insert({'task_id': task_id}).execute()
```

### 3.3 クエリ最適化

```python
# ✅ GOOD - 必要なカラムのみ取得
def get_task_titles(user_id: str, date: str) -> List[str]:
    """タスクタイトルのみ取得"""
    response = supabase.table('daily_tasks')\
        .select('title')\
        .eq('user_id', user_id)\
        .eq('task_date', date)\
        .execute()
    return [task['title'] for task in response.data]

# ✅ GOOD - ページネーション
def get_journals_paginated(
    user_id: str, 
    page: int = 1, 
    per_page: int = 10
) -> Dict:
    """日記を ページング取得"""
    offset = (page - 1) * per_page
    
    response = supabase.table('journals')\
        .select('*', count='exact')\
        .eq('user_id', user_id)\
        .order('journal_date', desc=True)\
        .range(offset, offset + per_page - 1)\
        .execute()
    
    return {
        'data': response.data,
        'total': response.count,
        'page': page,
        'per_page': per_page
    }

# ❌ BAD - 全データ取得してアプリ側でフィルタ
def get_task_titles(user_id, date):
    response = supabase.table('daily_tasks').select('*').execute()
    return [t['title'] for t in response.data if t['user_id'] == user_id]
```

---

## エラーハンドリング規約

### 4.1 例外処理の階層
**3段階のエラーハンドリング**

```python
# ✅ GOOD - レイヤー別エラー処理

# Layer 1: データベース層（utils/database.py）
def get_tasks(user_id: str, date: str) -> List[Dict]:
    """タスク取得 - DB例外を上位に伝播"""
    try:
        response = supabase.table('daily_tasks')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('task_date', date)\
            .execute()
        return response.data
    except Exception as e:
        logger.error(f"Database error: {e}")
        raise DatabaseError(f"タスク取得に失敗: {e}")

# Layer 2: ビジネスロジック層（components/）
def load_user_tasks(user_id: str, date: str) -> List[Dict]:
    """タスク読み込み - ビジネスルール適用"""
    try:
        tasks = get_tasks(user_id, date)
        # ビジネスロジック（並び替え、フィルタリング等）
        return sorted(tasks, key=lambda x: x['priority'])
    except DatabaseError as e:
        logger.warning(f"Task loading failed: {e}")
        return []  # 空リスト返却（アプリは継続）

# Layer 3: UI層（pages/）
def render_tasks_page():
    """タスクページ - ユーザーにエラー表示"""
    try:
        tasks = load_user_tasks(user['id'], today)
        if not tasks:
            st.info("タスクがありません")
        else:
            for task in tasks:
                render_task_card(task)
    except Exception as e:
        st.error(f"⚠️ タスクの読み込みに失敗しました: {str(e)}")
        logger.exception("Unexpected error in tasks page")
```

### 4.2 カスタム例外クラス

```python
# ✅ GOOD - utils/exceptions.py
class MonkModeException(Exception):
    """基底例外クラス"""
    pass

class DatabaseError(MonkModeException):
    """データベース操作エラー"""
    pass

class AuthenticationError(MonkModeException):
    """認証エラー"""
    pass

class ValidationError(MonkModeException):
    """バリデーションエラー"""
    pass

# 使用例
def create_task(user_id: str, task_data: Dict) -> Dict:
    if not task_data.get('title'):
        raise ValidationError("タスク名は必須です")
    
    try:
        # DB操作
        pass
    except Exception as e:
        raise DatabaseError(f"タスク作成失敗: {e}")
```

### 4.3 ユーザーフレンドリーなエラーメッセージ

```python
# ✅ GOOD - 具体的で親切なメッセージ
try:
    create_task(user_id, task_data)
    st.success("✅ タスクを追加しました")
except ValidationError as e:
    st.error(f"⚠️ 入力エラー: {str(e)}")
except DatabaseError as e:
    st.error("❌ タスクの保存に失敗しました。しばらくしてから再度お試しください。")
    logger.error(f"DB error: {e}")
except Exception as e:
    st.error("❌ 予期しないエラーが発生しました。サポートにお問い合わせください。")
    logger.exception("Unexpected error")

# ❌ BAD - 技術的すぎる・不親切
try:
    create_task(user_id, task_data)
except Exception as e:
    st.error(str(e))  # "INSERT INTO failed: duplicate key value"
```

---

## セキュリティ規約

### 5.1 環境変数の管理

```python
# ✅ GOOD - utils/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """設定管理クラス"""
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    
    @classmethod
    def validate(cls):
        """必須環境変数のチェック"""
        required = ["SUPABASE_URL", "SUPABASE_KEY"]
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise EnvironmentError(f"環境変数が不足: {', '.join(missing)}")

# 起動時にバリデーション
Config.validate()

# ❌ BAD - ハードコーディング
SUPABASE_URL = "https://xxxxx.supabase.co"  # 絶対禁止
SUPABASE_KEY = "eyJhbG..."  # 絶対禁止
```

### 5.2 入力バリデーション

```python
# ✅ GOOD - すべての入力を検証
import re
from typing import Optional

def validate_email(email: str) -> bool:
    """メールアドレスの形式チェック"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> Optional[str]:
    """
    パスワードの強度チェック
    
    Returns:
        エラーメッセージ（問題なければNone）
    """
    if len(password) < 8:
        return "パスワードは8文字以上必要です"
    if not re.search(r'[A-Z]', password):
        return "大文字を1文字以上含めてください"
    if not re.search(r'[a-z]', password):
        return "小文字を1文字以上含めてください"
    if not re.search(r'[0-9]', password):
        return "数字を1文字以上含めてください"
    return None

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """入力のサニタイズ"""
    # XSS対策
    text = text.strip()
    text = text[:max_length]
    # HTMLタグを除去（必要に応じて）
    return text

# ❌ BAD - 検証なし
def create_user(email, password):
    # そのまま使用 - 危険
    pass
```

### 5.3 SQLインジェクション対策

```python
# ✅ GOOD - Supabase SDKのパラメータバインディング使用
def get_user_by_email(email: str) -> Optional[Dict]:
    """メールアドレスでユーザー検索"""
    # SDKが自動的にエスケープ
    response = supabase.table('user_profiles')\
        .select('*')\
        .eq('email', email)\
        .execute()
    return response.data[0] if response.data else None

# ❌ BAD - 生SQLの文字列結合（絶対禁止）
def get_user_by_email(email):
    query = f"SELECT * FROM user_profiles WHERE email = '{email}'"
    # SQLインジェクションの危険
```

---

## パフォーマンス規約

### 6.1 不要な再計算を避ける

```python
# ✅ GOOD - 計算結果をキャッシュ
import functools

@functools.lru_cache(maxsize=128)
def calculate_streak_days(user_id: str) -> int:
    """連続達成日数を計算（キャッシュ付き）"""
    # 重い計算
    pass

# Streamlitの場合
@st.cache_data(ttl=3600)  # 1時間キャッシュ
def get_monthly_statistics(user_id: str, year: int, month: int) -> Dict:
    """月次統計を取得"""
    # 集計処理
    pass

# ❌ BAD - 毎回再計算
def calculate_streak_days(user_id):
    # ページ更新のたびに実行される
    pass
```

### 6.2 N+1問題の回避

```python
# ✅ GOOD - 一括取得
def get_tasks_with_categories(user_id: str, date: str) -> List[Dict]:
    """タスクとカテゴリ情報を一括取得"""
    response = supabase.table('daily_tasks')\
        .select('*, categories(*)')\
        .eq('user_id', user_id)\
        .eq('task_date', date)\
        .execute()
    return response.data

# ❌ BAD - N+1クエリ
def get_tasks_with_categories(user_id, date):
    tasks = get_tasks(user_id, date)
    for task in tasks:
        # 各タスクごとにクエリ実行（遅い）
        category = get_category(task['category_id'])
        task['category'] = category
    return tasks
```

### 6.3 大量データの処理

```python
# ✅ GOOD - ページング + ジェネレータ
from typing import Generator

def get_all_journals_generator(user_id: str) -> Generator[Dict, None, None]:
    """全日記をジェネレータで取得"""
    page = 1
    per_page = 50
    
    while True:
        offset = (page - 1) * per_page
        response = supabase.table('journals')\
            .select('*')\
            .eq('user_id', user_id)\
            .range(offset, offset + per_page - 1)\
            .execute()
        
        if not response.data:
            break
        
        for journal in response.data:
            yield journal
        
        page += 1

# 使用例
for journal in get_all_journals_generator(user_id):
    process_journal(journal)

# ❌ BAD - 全データを一度にメモリに
def get_all_journals(user_id):
    response = supabase.table('journals').select('*').eq('user_id', user_id).execute()
    return response.data  # メモリ不足の危険
```

---

## ドキュメンテーション規約

### 7.1 Docstring規約（Google Style）

```python
# ✅ GOOD - 完全なdocstring
def create_habit_record(
    user_id: str,
    record_date: str,
    habit_data: Dict[str, any]
) -> Dict:
    """
    習慣記録を作成または更新する
    
    同じ日付のレコードが存在する場合は更新、存在しない場合は新規作成を行う。
    
    Args:
        user_id: ユーザーID（UUID形式）
        record_date: 記録日付（YYYY-MM-DD形式）
        habit_data: 習慣データ
            - sleep_hours (float): 睡眠時間
            - exercise_done (bool): 運動実施フラグ
            - mood_rating (int): 気分評価（1-5）
    
    Returns:
        作成・更新された習慣レコード
        
    Raises:
        ValidationError: 入力データが不正な場合
        DatabaseError: データベース操作が失敗した場合
    
    Example:
        >>> habit_data = {
        ...     'sleep_hours': 7.5,
        ...     'exercise_done': True,
        ...     'mood_rating': 4
        ... }
        >>> record = create_habit_record('user-123', '2024-02-10', habit_data)
        >>> print(record['id'])
        'record-456'
    """
    # 実装
    pass

# ❌ BAD - docstringなし、または不完全
def create_habit_record(user_id, record_date, habit_data):
    """習慣記録を作成"""  # 情報不足
    pass
```

### 7.2 コメント規約

```python
# ✅ GOOD - WHYを説明するコメント
def calculate_completion_rate(tasks: List[Dict]) -> float:
    """タスク完了率を計算"""
    if not tasks:
        # タスクがない場合は100%とみなす
        # （何もやることがないので達成済み）
        return 1.0
    
    completed = sum(1 for task in tasks if task['is_completed'])
    return completed / len(tasks)

# ✅ GOOD - 複雑なロジックの説明
def get_next_routine_time(routine: Dict, current_time: datetime) -> datetime:
    """次のルーティン実行時刻を計算"""
    # 週次ルーティンの場合、次の該当曜日を探す
    if routine['frequency'] == 'weekly':
        target_weekdays = routine['weekdays']
        current_weekday = current_time.weekday()
        
        # 今日が該当曜日かチェック
        if current_weekday in target_weekdays:
            # 既に実行時刻を過ぎていれば翌週
            if current_time.time() > routine['scheduled_time']:
                days_ahead = 7
            else:
                days_ahead = 0
        else:
            # 次の該当曜日までの日数を計算
            days_ahead = min(
                (day - current_weekday) % 7 
                for day in target_weekdays
            )
        
        return current_time + timedelta(days=days_ahead)

# ❌ BAD - 自明なコメント（不要）
def get_task_count(tasks):
    # タスクの数を数える
    return len(tasks)

# ❌ BAD - コードと矛盾するコメント
def is_task_overdue(task):
    # タスクが期限内かチェック
    return task['due_date'] < datetime.now()  # 実際は期限切れチェック
```

### 7.3 README/ドキュメント

```markdown
# ✅ GOOD - 各ファイルにモジュールdocstring

"""
タスク管理モジュール

このモジュールはデイリータスクのCRUD操作を提供します。

主要機能:
- タスクの取得・作成・更新・削除
- タスク完了率の計算
- タスクの優先度変更

使用例:
    >>> from utils.database import get_tasks_by_date, create_task
    >>> tasks = get_tasks_by_date('user-123', '2024-02-10')
    >>> new_task = create_task('user-123', {'title': '運動'})

Author: Your Name
Created: 2024-02-10
"""
```

---

## Git運用規約

### 8.1 コミットメッセージ規約

```bash
# ✅ GOOD - プレフィックス付き明確なメッセージ
git commit -m "feat: タスク完了チェック機能を追加"
git commit -m "fix: タスク削除時のエラーを修正"
git commit -m "docs: README に環境構築手順を追加"
git commit -m "refactor: データベース関数を utils に移動"
git commit -m "style: PEP 8に従ってフォーマット修正"
git commit -m "test: タスクCRUD操作のテストを追加"

# プレフィックス一覧
# feat: 新機能
# fix: バグ修正
# docs: ドキュメント
# style: コードフォーマット
# refactor: リファクタリング
# test: テスト追加・修正
# chore: ビルド、設定変更

# ❌ BAD - 不明確なメッセージ
git commit -m "update"
git commit -m "fix bug"
git commit -m "changes"
```

### 8.2 ブランチ戦略

**シンプルなスプリント単位管理**

```bash
# ブランチ構造
main                        # 本番（保護ブランチ）
├── claude/sprint-1         # Sprint 1全体
├── claude/sprint-2         # Sprint 2全体
├── claude/sprint-3         # Sprint 3全体
└── claude/bugfix-XXXX      # 緊急バグ修正のみ

# ブランチ命名規則
claude/sprint-<番号>        # スプリント実装（基本）
claude/bugfix-<問題名>      # 緊急バグ修正のみ

例:
claude/sprint-1
claude/sprint-2
claude/bugfix-login-error
```

**ワークフロー:**

```bash
# 1. Sprint開始 - Claude Codeがブランチ作成
git checkout -b claude/sprint-1
git push -u origin claude/sprint-1

# 2. 実装・コミット・プッシュ（繰り返し）
git add [files]
git commit -m "feat: 機能を実装"
git push origin claude/sprint-1

# 3. あなたがローカルで確認
git checkout claude/sprint-1
git pull origin claude/sprint-1
# 動作確認...

# 4. 問題なければ次の実装を指示、繰り返し

# 5. Sprint完了後、あなたがPR作成・マージ
# GitHub上で base: main ← compare: claude/sprint-1
# マージ後、ブランチ削除
```

**利点:**
- ✅ シンプル：1スプリント = 1ブランチ
- ✅ 柔軟：Phase区切りなく継続的に開発
- ✅ 安全：mainブランチを保護
- ✅ 明確：履歴が追いやすい

# ❌ BAD - claude/プレフィックスなし
sprint-1                # Claude Codeが操作不可
feature/auth           # 複雑化
```

### 8.3 コミット粒度

```bash
# ✅ GOOD - 適切な粒度
git add components/auth.py
git commit -m "feat: ログイン機能を実装"

git add components/auth.py
git commit -m "feat: サインアップ機能を実装"

git add pages/1_Tasks.py
git commit -m "feat: タスク一覧表示を実装"

# ❌ BAD - 大きすぎる
git add .
git commit -m "Sprint 1完了"  # 何十個もの変更を一度に

# ❌ BAD - 小さすぎる
git commit -m "fix: スペース削除"
git commit -m "fix: インデント修正"
git commit -m "fix: コメント追加"
```

---

## コードレビューチェックリスト

### 新規コード追加時の確認事項

```markdown
## 機能実装
- [ ] 要件を満たしている
- [ ] エッジケースを考慮している
- [ ] エラーハンドリングが適切

## コード品質
- [ ] PEP 8に準拠
- [ ] 型ヒントがある
- [ ] docstringがある
- [ ] 変数・関数名が明確
- [ ] マジックナンバーを定数化

## セキュリティ
- [ ] 入力バリデーションがある
- [ ] 環境変数を使用（ハードコードなし）
- [ ] SQLインジェクション対策済み

## パフォーマンス
- [ ] 不要なクエリがない
- [ ] N+1問題がない
- [ ] 適切にキャッシュしている

## テスト
- [ ] 正常系をテスト
- [ ] 異常系をテスト
- [ ] エッジケースをテスト

## ドキュメント
- [ ] README更新（必要に応じて）
- [ ] コメント記載（複雑な処理）
- [ ] 変更履歴記録
```

---

## まとめ：最重要ルール Top 10

1. **PEP 8準拠** - Pythonの標準スタイルに従う
2. **型ヒント必須** - すべての関数に型を明記
3. **エラーハンドリング** - try-exceptを適切に使用
4. **セキュリティ** - 環境変数、入力検証を徹底
5. **docstring** - すべての関数に説明を記載
6. **命名規則** - 明確でわかりやすい名前を使用
7. **DRY原則** - コードの重複を避ける
8. **単一責任** - 1関数1責務を守る
9. **コミットメッセージ** - 明確なプレフィックス付き
10. **レビュー** - 実装前にこの規約をチェック

---

このルールブックを常に参照し、一貫性のある高品質なコードを維持してください。
