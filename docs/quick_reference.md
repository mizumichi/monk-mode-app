# コーディング規約 クイックリファレンス

## 🚀 実装開始前の必読チェックリスト

### ファイル作成時
```python
"""
[モジュールの説明を1行で]

[詳細な説明]

主要機能:
- 機能1
- 機能2

Author: [名前]
Created: [日付]
"""

# 標準ライブラリ
import os
from datetime import datetime

# サードパーティ
import streamlit as st

# ローカル
from utils.database import get_data
```

---

## 📝 関数テンプレート

### 標準関数
```python
def function_name(
    param1: str,
    param2: int,
    optional_param: bool = True
) -> Dict[str, any]:
    """
    関数の目的を1行で説明
    
    詳細な説明（必要に応じて）
    
    Args:
        param1: パラメータ1の説明
        param2: パラメータ2の説明
        optional_param: オプションパラメータの説明
    
    Returns:
        戻り値の説明
    
    Raises:
        ErrorType: エラーが発生する条件
    
    Example:
        >>> result = function_name("test", 123)
        >>> print(result)
        {'key': 'value'}
    """
    try:
        # 処理
        result = {}
        return result
    except Exception as e:
        logger.error(f"Error in function_name: {e}")
        raise
```

### データベース関数
```python
def get_entity_by_id(entity_id: str) -> Optional[Dict]:
    """エンティティをIDで取得"""
    try:
        response = supabase.table('table_name')\
            .select('*')\
            .eq('id', entity_id)\
            .single()\
            .execute()
        
        logger.info(f"Fetched entity: {entity_id}")
        return response.data
        
    except Exception as e:
        logger.error(f"Error fetching entity {entity_id}: {e}")
        raise DatabaseError(f"取得失敗: {e}")

def create_entity(user_id: str, data: Dict) -> Dict:
    """エンティティを作成"""
    try:
        # バリデーション
        required = ['field1', 'field2']
        for field in required:
            if field not in data:
                raise ValidationError(f"必須: {field}")
        
        # 作成
        data['user_id'] = user_id
        response = supabase.table('table_name')\
            .insert(data)\
            .execute()
        
        logger.info(f"Created entity: {response.data[0]['id']}")
        return response.data[0]
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error creating entity: {e}")
        raise DatabaseError(f"作成失敗: {e}")

def update_entity(entity_id: str, updates: Dict) -> bool:
    """エンティティを更新"""
    try:
        supabase.table('table_name')\
            .update(updates)\
            .eq('id', entity_id)\
            .execute()
        
        logger.info(f"Updated entity: {entity_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error updating entity {entity_id}: {e}")
        return False

def delete_entity(entity_id: str) -> bool:
    """エンティティを削除"""
    try:
        supabase.table('table_name')\
            .delete()\
            .eq('id', entity_id)\
            .execute()
        
        logger.info(f"Deleted entity: {entity_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting entity {entity_id}: {e}")
        return False
```

---

## 🎨 Streamlitページテンプレート

### 標準ページ構造
```python
"""
[ページ名] - [簡単な説明]
"""
import streamlit as st
from datetime import date, datetime
from typing import Optional, List, Dict

from components.auth import is_authenticated, get_current_user, logout
from utils.database import get_data, create_data, update_data
from utils.constants import CATEGORIES, PRIORITIES

# ページ設定
st.set_page_config(
    page_title="ページ名",
    page_icon="📋",
    layout="wide"
)

# 認証チェック
if not is_authenticated():
    st.warning("ログインが必要です")
    st.switch_page("pages/0_🔐_Auth.py")
    st.stop()

user = get_current_user()

# セッション状態初期化
def init_session_state():
    """セッション状態を初期化"""
    if 'key1' not in st.session_state:
        st.session_state['key1'] = default_value

init_session_state()

# ヘッダー
st.title("📋 ページタイトル")
st.divider()

# メインコンテンツ
def render_main_content():
    """メインコンテンツをレンダリング"""
    col1, col2, col3 = st.columns([2, 5, 2])
    
    with col1:
        # 左カラム
        pass
    
    with col2:
        # 中央カラム
        pass
    
    with col3:
        # 右カラム
        pass

render_main_content()

# フッター（任意）
st.divider()
st.caption("モンクモード支援システム v1.0")
```

### フォーム付きページ
```python
# データ追加フォーム
with st.expander("➕ 新規追加", expanded=False):
    with st.form("add_form", clear_on_submit=True):
        # 入力フィールド
        field1 = st.text_input("フィールド1*", max_chars=200)
        field2 = st.text_area("フィールド2", max_chars=1000)
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox("カテゴリ", CATEGORIES)
        with col2:
            priority = st.selectbox("優先度", PRIORITIES)
        
        submitted = st.form_submit_button("追加", use_container_width=True)
        
        if submitted:
            # バリデーション
            if not field1:
                st.error("⚠️ フィールド1は必須です")
                st.stop()
            
            # 処理
            try:
                data = {
                    "field1": field1,
                    "field2": field2,
                    "category": category,
                    "priority": priority
                }
                result = create_data(user['id'], data)
                st.success("✅ 追加しました")
                st.rerun()
                
            except ValidationError as e:
                st.error(f"⚠️ 入力エラー: {e}")
            except DatabaseError as e:
                st.error("❌ 保存に失敗しました")
                logger.error(f"Form submission error: {e}")
            except Exception as e:
                st.error("❌ 予期しないエラーが発生しました")
                logger.exception("Unexpected error in form")
```

---

## 🗂️ コンポーネントテンプレート

### 再利用可能コンポーネント
```python
"""
[コンポーネント名]コンポーネント

[説明]
"""
import streamlit as st
from typing import Dict, Callable, Optional

def render_component(
    data: Dict,
    on_action: Optional[Callable] = None,
    **kwargs
) -> None:
    """
    コンポーネントをレンダリング
    
    Args:
        data: 表示データ
        on_action: アクション時のコールバック
        **kwargs: 追加オプション
    """
    with st.container():
        # スタイル定義
        style = """
            <style>
            .component-class {
                /* スタイル */
            }
            </style>
        """
        st.markdown(style, unsafe_allow_html=True)
        
        # コンテンツ
        col1, col2, col3 = st.columns([1, 8, 1])
        
        with col1:
            # アイコン等
            pass
        
        with col2:
            # メインコンテンツ
            st.markdown(f"**{data['title']}**")
            if data.get('description'):
                st.caption(data['description'])
        
        with col3:
            # アクションボタン
            if st.button("🗑️", key=f"btn_{data['id']}"):
                if on_action:
                    on_action(data['id'])

# 使用例
# render_component(data, on_action=handle_delete)
```

---

## 🔧 ユーティリティテンプレート

### 定数定義（utils/constants.py）
```python
"""
システム全体で使用する定数定義
"""

# タスク関連
TASK_CATEGORIES = ["運動", "学習", "健康管理", "自己研鑽", "その他"]
TASK_PRIORITIES = ["高", "中", "低"]
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

# UI関連
COLORS = {
    'primary': '#2C3E50',
    'secondary': '#34495E',
    'accent': '#27AE60',
    'warning': '#E67E22',
    'danger': '#E74C3C',
    'background': '#ECF0F1',
}
```

### 日付ユーティリティ（utils/date_utils.py）
```python
"""
日付処理ユーティリティ
"""
from datetime import datetime, date, timedelta
from typing import List

def get_today() -> date:
    """今日の日付を取得"""
    return date.today()

def format_date_japanese(d: date) -> str:
    """日本語形式で日付を整形"""
    weekdays = ['月', '火', '水', '木', '金', '土', '日']
    weekday = weekdays[d.weekday()]
    return f"{d.year}年{d.month}月{d.day}日 ({weekday})"

def get_week_range(d: date) -> tuple[date, date]:
    """指定日を含む週の範囲を取得（月曜始まり）"""
    start = d - timedelta(days=d.weekday())
    end = start + timedelta(days=6)
    return start, end

def get_date_range(start: date, end: date) -> List[date]:
    """日付範囲のリストを生成"""
    days = (end - start).days + 1
    return [start + timedelta(days=i) for i in range(days)]
```

---

## ⚠️ エラーハンドリングパターン

### カスタム例外（utils/exceptions.py）
```python
"""カスタム例外クラス"""

class MonkModeException(Exception):
    """基底例外"""
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

class NotFoundError(MonkModeException):
    """リソース未発見エラー"""
    pass
```

### エラーハンドリング使用例
```python
from utils.exceptions import ValidationError, DatabaseError, NotFoundError
import logging

logger = logging.getLogger(__name__)

def some_function():
    try:
        # 処理
        result = perform_operation()
        return result
        
    except ValidationError as e:
        # バリデーションエラー（ユーザー起因）
        st.error(f"⚠️ 入力エラー: {str(e)}")
        logger.warning(f"Validation error: {e}")
        
    except NotFoundError as e:
        # リソース未発見
        st.error(f"⚠️ データが見つかりません: {str(e)}")
        logger.info(f"Not found: {e}")
        
    except DatabaseError as e:
        # データベースエラー（システム起因）
        st.error("❌ データベースエラーが発生しました。しばらくしてから再度お試しください。")
        logger.error(f"Database error: {e}")
        
    except Exception as e:
        # 予期しないエラー
        st.error("❌ 予期しないエラーが発生しました。")
        logger.exception(f"Unexpected error: {e}")
```

---

## 🧪 テストパターン

### 単体テスト例
```python
"""
tests/test_database.py
"""
import pytest
from datetime import date
from utils.database import get_tasks_by_date, create_task
from utils.exceptions import ValidationError

def test_get_tasks_by_date_success():
    """タスク取得が成功する"""
    user_id = "test-user-123"
    target_date = date.today().isoformat()
    
    tasks = get_tasks_by_date(user_id, target_date)
    
    assert isinstance(tasks, list)
    for task in tasks:
        assert task['user_id'] == user_id
        assert task['task_date'] == target_date

def test_create_task_validation_error():
    """必須フィールドなしでエラー"""
    user_id = "test-user-123"
    invalid_data = {}  # titleなし
    
    with pytest.raises(ValidationError):
        create_task(user_id, invalid_data)

def test_create_task_success():
    """タスク作成が成功する"""
    user_id = "test-user-123"
    task_data = {
        "title": "テストタスク",
        "category": "学習",
        "priority": "高",
        "task_date": date.today().isoformat()
    }
    
    result = create_task(user_id, task_data)
    
    assert result['title'] == task_data['title']
    assert 'id' in result
```

---

## 📊 ログ設定

### ログ設定（utils/logger.py）
```python
"""ログ設定"""
import logging
import sys

def setup_logger(name: str) -> logging.Logger:
    """ロガーをセットアップ"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # ハンドラ設定
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # フォーマッタ設定
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    return logger

# 使用例
logger = setup_logger(__name__)
logger.info("情報メッセージ")
logger.warning("警告メッセージ")
logger.error("エラーメッセージ")
```

---

## 💾 Git操作クイックガイド（Claude Code版）

### 基本ワークフロー

```bash
# 1. Sprint開始 - ブランチ作成
git checkout -b claude/sprint-1
git push -u origin claude/sprint-1

# 2. 実装・コミット・プッシュ（繰り返し）
# ... 実装 ...
git add [変更したファイル]
git commit -m "feat: 〇〇機能を実装"
git push origin claude/sprint-1

# 3. 次の実装を続ける
# ... 実装 ...
git add [変更したファイル]
git commit -m "feat: △△機能を実装"
git push origin claude/sprint-1

# 4. Sprint完了を報告
echo "Sprint 1完了。claude/sprint-1 を確認してください。"
```

### ブランチ命名規則

```bash
# ✅ GOOD - シンプル
claude/sprint-1         # Sprint 1全体
claude/sprint-2         # Sprint 2全体
claude/bugfix-login     # 緊急バグ修正

# ❌ BAD
sprint-1                # claude/プレフィックスなし
claude/sprint-1-auth    # 細かく分けすぎ
feature/auth            # Claude Codeが操作不可
```

### コミットメッセージ

```bash
# ✅ GOOD - プレフィックス付き
git commit -m "feat: ログイン機能を実装"
git commit -m "fix: タスク削除エラーを修正"
git commit -m "style: フォーマット修正"

# ❌ BAD
git commit -m "update"
git commit -m "変更"
```

### コミットメッセージプレフィックス
```
feat:     新機能追加
fix:      バグ修正
docs:     ドキュメント変更
style:    フォーマット修正（機能変更なし）
refactor: リファクタリング
test:     テスト追加・修正
chore:    ビルド、設定変更
```

### よくある操作

```bash
# 最新を取得
git pull origin claude/sprint-1

# 現在のブランチ確認
git branch

# 変更状態確認
git status

# コミット履歴確認
git log --oneline

# 間違えたコミットメッセージを修正（プッシュ前）
git commit --amend -m "feat: 正しいメッセージ"
```

---

## 🔍 コードレビューチェックリスト

実装完了後、以下を確認:

```markdown
### 機能
- [ ] 要件を満たしている
- [ ] エッジケースを考慮
- [ ] エラーハンドリングが適切

### コード品質
- [ ] PEP 8準拠
- [ ] 型ヒントあり
- [ ] docstringあり
- [ ] 変数名が明確
- [ ] マジックナンバーなし

### セキュリティ
- [ ] 入力バリデーション
- [ ] 環境変数使用
- [ ] SQLインジェクション対策

### パフォーマンス
- [ ] 不要なクエリなし
- [ ] N+1問題なし
- [ ] キャッシング適切

### テスト
- [ ] 正常系テスト
- [ ] 異常系テスト
- [ ] エッジケーステスト
```

---

## 🚨 絶対禁止事項

```python
# ❌ ハードコーディング（絶対禁止）
SUPABASE_URL = "https://xxxxx.supabase.co"
API_KEY = "secret123"

# ❌ 型ヒントなし
def get_data(id):
    pass

# ❌ docstringなし
def important_function():
    pass

# ❌ エラー無視
try:
    risky_operation()
except:
    pass  # エラーを握りつぶす

# ❌ SQL文字列結合
query = f"SELECT * FROM users WHERE id = '{user_id}'"

# ❌ 不明確な変数名
x = get_data()
tmp = process(x)
result = tmp.data

# ❌ 全データ取得
all_data = supabase.table('huge_table').select('*').execute()
```

---

## ✅ 実装開始時のチェックリスト

コーディング開始前に確認:

1. [ ] `coding_standards.md` を読んだ
2. [ ] 実装するファイルの役割を理解した
3. [ ] 関数名・変数名を考えた
4. [ ] エラーハンドリングを計画した
5. [ ] テストケースを考えた
6. [ ] 既存コードの重複がないか確認した
7. [ ] 環境変数が必要か確認した
8. [ ] ログを仕込む箇所を決めた

---

このクイックリファレンスを常に手元に置いて実装してください！
