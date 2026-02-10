# Sprint 1 実装プロンプト集 - Claude Code用

このドキュメントには、Sprint 1の各Phaseで実装する内容の詳細な指示が含まれています。
各プロンプトをClaude Codeに渡して、順番に実装を進めてください。

---

## 📋 実装の進め方

### 基本ルール
1. **順番通りに実装**: Phase 1 → Phase 2 → Phase 3 → Phase 4
2. **各プロンプト完了後に動作確認**: 必ずテストを実行
3. **エラーが出たら即座に修正**: 次に進まない
4. **詳細設計書を参照**: `sprint_1_detailed_design.md` に仕様の詳細あり

### プロンプトの使い方
各プロンプトは以下の構成:
- **目的**: 何を実装するか
- **ファイルパス**: 作成・編集するファイル
- **要件**: 実装すべき機能
- **参考コード**: 実装のヒント
- **完了確認**: 動作テスト項目

---

# Phase 1: 認証機能（3日間）

## プロンプト 1-1: Supabase認証モジュール作成

### 目的
Supabase Authを使った認証機能の基盤を構築する

### ファイルパス
`components/auth.py`

### 実装内容

以下の関数を含む認証モジュールを作成してください:

#### 1. login(email: str, password: str) -> bool
- Supabase Auth でログイン
- 成功時: セッション状態に保存、Trueを返す
- 失敗時: エラーメッセージ表示、Falseを返す

#### 2. signup(email: str, password: str, display_name: str) -> bool
- Supabase Auth でユーザー作成
- user_profilesテーブルにレコード作成
- 成功時: セッション状態に保存、Trueを返す
- 失敗時: エラーメッセージ表示、Falseを返す

#### 3. logout() -> None
- セッション状態をクリア
- Supabase Auth からサインアウト

#### 4. get_current_user() -> dict | None
- セッション状態からユーザー情報取得
- 未認証ならNone

#### 5. is_authenticated() -> bool
- 認証状態をチェック

### 要件

- すべての関数でエラーハンドリング（try-except）
- エラーメッセージはst.errorで表示
- セッション状態のキー名:
  - `st.session_state['user']`: ユーザー情報（辞書）
  - `st.session_state['authenticated']`: bool

### 参考コード

```python
import streamlit as st
from utils.supabase_client import supabase

def login(email: str, password: str) -> bool:
    """
    ログイン処理
    
    Args:
        email: メールアドレス
        password: パスワード
    
    Returns:
        bool: 成功時True、失敗時False
    """
    try:
        # Supabase Auth でログイン
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        # user_profilesから追加情報取得
        profile = supabase.table('user_profiles')\
            .select('display_name')\
            .eq('id', response.user.id)\
            .single()\
            .execute()
        
        # セッション状態に保存
        st.session_state['user'] = {
            'id': response.user.id,
            'email': response.user.email,
            'display_name': profile.data['display_name']
        }
        st.session_state['authenticated'] = True
        
        return True
        
    except Exception as e:
        st.error("メールまたはパスワードが正しくありません")
        print(f"Login error: {e}")
        return False

def signup(email: str, password: str, display_name: str) -> bool:
    """
    サインアップ処理
    
    Args:
        email: メールアドレス
        password: パスワード
        display_name: 表示名
    
    Returns:
        bool: 成功時True、失敗時False
    """
    try:
        # パスワード検証
        if len(password) < 8:
            st.error("パスワードは8文字以上にしてください")
            return False
        
        # Supabase Auth でユーザー作成
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        # user_profilesにレコード作成
        supabase.table('user_profiles').insert({
            "id": response.user.id,
            "display_name": display_name
        }).execute()
        
        # セッション状態に保存
        st.session_state['user'] = {
            'id': response.user.id,
            'email': response.user.email,
            'display_name': display_name
        }
        st.session_state['authenticated'] = True
        
        return True
        
    except Exception as e:
        if "already registered" in str(e).lower():
            st.error("このメールアドレスは既に登録されています")
        else:
            st.error("登録に失敗しました。再度お試しください")
        print(f"Signup error: {e}")
        return False

def logout() -> None:
    """ログアウト処理"""
    try:
        supabase.auth.sign_out()
        st.session_state.clear()
    except Exception as e:
        print(f"Logout error: {e}")
        st.session_state.clear()

def get_current_user() -> dict | None:
    """
    現在のユーザー情報を取得
    
    Returns:
        dict | None: ユーザー情報、未認証ならNone
    """
    return st.session_state.get('user')

def is_authenticated() -> bool:
    """
    認証状態をチェック
    
    Returns:
        bool: 認証済みならTrue
    """
    return st.session_state.get('authenticated', False)
```

### 完了確認

1. ファイルが作成されていること
2. すべての関数が定義されていること
3. エラーハンドリングが実装されていること
4. 型ヒントとdocstringがあること

次のプロンプトに進む前に、このファイルをコミットしてください。

---

## プロンプト 1-2: 認証画面（ログイン・サインアップ）作成

### 目的
ユーザーがログイン・サインアップできる画面を作成する

### ファイルパス
`pages/0_🔐_Auth.py`

### 実装内容

タブで切り替え可能なログイン・サインアップ画面を作成してください。

#### ページ設定
```python
st.set_page_config(
    page_title="ログイン",
    page_icon="🔐",
    layout="centered"
)
```

#### 認証済みチェック
- 既にログイン済みならHome.pyへリダイレクト

#### タブ1: ログイン
**入力項目**:
- メールアドレス（text_input）
- パスワード（text_input, type="password"）
- ログインボタン

**動作**:
- ボタンクリックでlogin()関数実行
- 成功時: 成功メッセージ表示 → Home.pyへリダイレクト
- 失敗時: エラーメッセージ表示（login関数内で処理済み）

#### タブ2: サインアップ
**入力項目**:
- 表示名（text_input）
- メールアドレス（text_input）
- パスワード（text_input, type="password"）
- パスワード確認（text_input, type="password"）
- サインアップボタン

**バリデーション**:
- 表示名が空でないか
- パスワードとパスワード確認が一致するか
- パスワードが8文字以上か（signup関数でもチェック）

### 参考コード

```python
import streamlit as st
from components.auth import login, signup, is_authenticated

st.set_page_config(
    page_title="ログイン",
    page_icon="🔐",
    layout="centered"
)

# 既にログイン済みならリダイレクト
if is_authenticated():
    st.switch_page("Home.py")

# タイトル
st.title("🔐 モンクモード支援システム")
st.caption("ログインまたは新規登録してください")

# タブ
tab1, tab2 = st.tabs(["ログイン", "新規登録"])

# ログインタブ
with tab1:
    st.subheader("ログイン")
    
    with st.form("login_form"):
        email = st.text_input("メールアドレス", key="login_email")
        password = st.text_input("パスワード", type="password", key="login_password")
        
        submit = st.form_submit_button("ログイン", use_container_width=True)
        
        if submit:
            if not email or not password:
                st.error("すべての項目を入力してください")
            else:
                if login(email, password):
                    st.success("✓ ログインしました")
                    st.rerun()

# サインアップタブ
with tab2:
    st.subheader("新規登録")
    
    with st.form("signup_form"):
        display_name = st.text_input("表示名", key="signup_name")
        email = st.text_input("メールアドレス", key="signup_email")
        password = st.text_input("パスワード（8文字以上）", type="password", key="signup_password")
        password_confirm = st.text_input("パスワード確認", type="password", key="signup_password_confirm")
        
        submit = st.form_submit_button("登録", use_container_width=True)
        
        if submit:
            # バリデーション
            if not display_name or not email or not password or not password_confirm:
                st.error("すべての項目を入力してください")
            elif len(password) < 8:
                st.error("パスワードは8文字以上にしてください")
            elif password != password_confirm:
                st.error("パスワードが一致しません")
            else:
                if signup(email, password, display_name):
                    st.success("✓ 登録が完了しました")
                    st.rerun()
```

### 完了確認

以下を実際に試してください:

1. [ ] ページが表示される
2. [ ] タブの切り替えができる
3. [ ] ログインフォームが動作する
4. [ ] サインアップフォームが動作する
5. [ ] バリデーションエラーが表示される
6. [ ] ログイン成功後、Home.pyへリダイレクトされる
7. [ ] 既にログイン済みの状態でアクセスすると、Home.pyへリダイレクトされる

動作確認後、コミットしてください。

---

## プロンプト 1-3: Home.pyに認証ガード追加

### 目的
Home.pyを認証必須ページにする

### ファイルパス
`Home.py`

### 実装内容

Home.pyの冒頭に認証チェックを追加し、未認証ならログイン画面へリダイレクトしてください。
また、ヘッダーにログアウトボタンを配置してください。

### 参考コード

```python
import streamlit as st
from components.auth import is_authenticated, logout, get_current_user

st.set_page_config(
    page_title="モンクモード",
    page_icon="🧘",
    layout="wide"
)

# 認証チェック
if not is_authenticated():
    st.warning("ログインが必要です")
    st.switch_page("pages/0_🔐_Auth.py")
    st.stop()

# ユーザー情報取得
user = get_current_user()

# ヘッダー
col1, col2 = st.columns([5, 1])
with col1:
    st.title("🧘 モンクモード支援システム")
    st.caption(f"ようこそ、{user['display_name']}さん")
with col2:
    if st.button("ログアウト", type="secondary"):
        logout()
        st.rerun()

st.divider()

# 以下、ダッシュボードのコンテンツ（Phase 3で実装）
st.info("ダッシュボードは Phase 3 で実装します")
```

### 完了確認

以下を確認してください:

1. [ ] 未認証でHome.pyにアクセスすると、ログイン画面へリダイレクトされる
2. [ ] ログイン後、Home.pyが表示される
3. [ ] ユーザー名が表示される
4. [ ] ログアウトボタンをクリックすると、ログアウトしてログイン画面へ戻る

**統合テスト**:
- 新規ユーザー登録 → Home.py表示 → ログアウト → ログイン → Home.py表示

この流れが正常に動作することを確認してください。

動作確認後、Phase 1完了としてコミットしてください。

---

# Phase 2: タスク管理機能（5日間）

## プロンプト 2-1: タスクデータベース操作モジュール作成

### 目的
タスクのCRUD操作を行う関数群を作成する

### ファイルパス
`utils/database.py`

### 実装内容

以下の関数を実装してください:

#### 1. get_tasks_by_date(user_id: str, date: str) -> list
- 指定日のタスク一覧を取得
- 優先度順（高→中→低）、作成日時順でソート

#### 2. create_task(user_id: str, task_data: dict) -> dict | None
- 新規タスク作成
- display_orderは既存タスクの最大値+1

#### 3. update_task(task_id: str, updates: dict) -> bool
- タスク更新

#### 4. delete_task(task_id: str) -> bool
- タスク削除（物理削除）

#### 5. toggle_task_completion(task_id: str) -> bool
- タスクの完了状態を切り替え
- completed_atも更新

#### 6. get_task_completion_rate(user_id: str, date: str) -> float
- 指定日のタスク完了率を計算（0.0〜1.0）

### 要件

- すべての関数でエラーハンドリング
- エラー時はprint()でログ出力
- 戻り値: 失敗時はFalse、空リスト、またはNone

### 参考コード

```python
from utils.supabase_client import supabase
from datetime import datetime

def get_tasks_by_date(user_id: str, date: str) -> list:
    """
    指定日のタスク取得
    
    Args:
        user_id: ユーザーID
        date: 日付（ISO形式: YYYY-MM-DD）
    
    Returns:
        list: タスクリスト
    """
    try:
        # 優先度のマッピング（ソート用）
        priority_order = "CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END"
        
        response = supabase.table('daily_tasks')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('task_date', date)\
            .order('is_completed')\ # 未完了を先に
            .order('priority', desc=True)\ # 高優先度を先に  
            .order('created_at')\
            .execute()
        
        return response.data
    except Exception as e:
        print(f"Error fetching tasks: {e}")
        return []

def create_task(user_id: str, task_data: dict) -> dict | None:
    """
    タスク作成
    
    Args:
        user_id: ユーザーID
        task_data: タスクデータ（title, description, category, priority, task_date）
    
    Returns:
        dict | None: 作成されたタスク、失敗時はNone
    """
    try:
        # display_orderを計算
        max_order_response = supabase.table('daily_tasks')\
            .select('display_order')\
            .eq('user_id', user_id)\
            .eq('task_date', task_data['task_date'])\
            .order('display_order', desc=True)\
            .limit(1)\
            .execute()
        
        if max_order_response.data:
            new_order = max_order_response.data[0]['display_order'] + 1
        else:
            new_order = 0
        
        # タスク作成
        task_data['user_id'] = user_id
        task_data['display_order'] = new_order
        
        response = supabase.table('daily_tasks')\
            .insert(task_data)\
            .execute()
        
        return response.data[0] if response.data else None
        
    except Exception as e:
        print(f"Error creating task: {e}")
        return None

def update_task(task_id: str, updates: dict) -> bool:
    """
    タスク更新
    
    Args:
        task_id: タスクID
        updates: 更新内容の辞書
    
    Returns:
        bool: 成功時True
    """
    try:
        updates['updated_at'] = datetime.now().isoformat()
        
        supabase.table('daily_tasks')\
            .update(updates)\
            .eq('id', task_id)\
            .execute()
        
        return True
        
    except Exception as e:
        print(f"Error updating task: {e}")
        return False

def delete_task(task_id: str) -> bool:
    """
    タスク削除
    
    Args:
        task_id: タスクID
    
    Returns:
        bool: 成功時True
    """
    try:
        supabase.table('daily_tasks')\
            .delete()\
            .eq('id', task_id)\
            .execute()
        
        return True
        
    except Exception as e:
        print(f"Error deleting task: {e}")
        return False

def toggle_task_completion(task_id: str) -> bool:
    """
    タスクの完了状態を切り替え
    
    Args:
        task_id: タスクID
    
    Returns:
        bool: 成功時True
    """
    try:
        # 現在の状態を取得
        response = supabase.table('daily_tasks')\
            .select('is_completed')\
            .eq('id', task_id)\
            .single()\
            .execute()
        
        current_status = response.data['is_completed']
        new_status = not current_status
        
        # 更新
        updates = {
            'is_completed': new_status,
            'completed_at': datetime.now().isoformat() if new_status else None,
            'updated_at': datetime.now().isoformat()
        }
        
        supabase.table('daily_tasks')\
            .update(updates)\
            .eq('id', task_id)\
            .execute()
        
        return True
        
    except Exception as e:
        print(f"Error toggling task completion: {e}")
        return False

def get_task_completion_rate(user_id: str, date: str) -> float:
    """
    タスク完了率を計算
    
    Args:
        user_id: ユーザーID
        date: 日付（ISO形式）
    
    Returns:
        float: 完了率（0.0〜1.0）
    """
    try:
        tasks = get_tasks_by_date(user_id, date)
        
        if not tasks:
            return 0.0
        
        total = len(tasks)
        completed = len([t for t in tasks if t['is_completed']])
        
        return completed / total
        
    except Exception as e:
        print(f"Error calculating completion rate: {e}")
        return 0.0
```

### 完了確認

以下のテストコードで動作確認してください:

```python
# utils/database.py の末尾に追加（テスト後削除）
if __name__ == "__main__":
    from datetime import date
    
    # テスト用ユーザーID（実際のユーザーIDに置き換え）
    test_user_id = "your-user-id-here"
    today = date.today().isoformat()
    
    # タスク作成テスト
    task_data = {
        "title": "テストタスク",
        "description": "これはテストです",
        "category": "その他",
        "priority": "medium",
        "task_date": today
    }
    
    created_task = create_task(test_user_id, task_data)
    print(f"Created task: {created_task}")
    
    # タスク取得テスト
    tasks = get_tasks_by_date(test_user_id, today)
    print(f"Tasks: {len(tasks)} found")
    
    # 完了率テスト
    rate = get_task_completion_rate(test_user_id, today)
    print(f"Completion rate: {rate * 100}%")
```

実行:
```bash
python utils/database.py
```

動作確認後、コミットしてください。

---

## プロンプト 2-2: タスクカードコンポーネント作成

### 目的
再利用可能なタスク表示コンポーネントを作成する

### ファイルパス
`components/task_card.py`

### 実装内容

タスク情報を受け取って表示するコンポーネントを作成してください。

#### 関数シグネチャ
```python
def render_task_card(
    task: dict,
    on_complete_toggle: callable = None,
    on_edit: callable = None,
    on_delete: callable = None,
    show_actions: bool = True
) -> None
```

#### 表示内容
- 完了チェックボックス
- タイトル・説明
- カテゴリと優先度
- 編集・削除ボタン（show_actions=Trueの場合）

#### デザイン
- 優先度に応じた背景色
- 完了済みタスクはグレー表示、タイトルに取り消し線

### 参考コード

```python
import streamlit as st

# 定数定義
PRIORITY_COLORS = {
    "high": "#FFE5E5",
    "medium": "#FFF4E5",
    "low": "#E5F2FF"
}

PRIORITY_LABELS = {
    "high": "高",
    "medium": "中",
    "low": "低"
}

def render_task_card(
    task: dict,
    on_complete_toggle: callable = None,
    on_edit: callable = None,
    on_delete: callable = None,
    show_actions: bool = True
) -> None:
    """
    タスクカードをレンダリング
    
    Args:
        task: タスクデータ
        on_complete_toggle: 完了切り替え時のコールバック
        on_edit: 編集時のコールバック
        on_delete: 削除時のコールバック
        show_actions: アクションボタンを表示するか
    """
    
    # 背景色設定
    bg_color = PRIORITY_COLORS.get(task['priority'], "#F0F0F0")
    
    # 完了済みの場合はグレー
    if task['is_completed']:
        bg_color = "#F5F5F5"
    
    # カードコンテナ
    with st.container():
        # カスタムCSS
        st.markdown(f"""
        <style>
        .task-card-{task['id']} {{
            background-color: {bg_color};
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border-left: 4px solid {'#28a745' if task['is_completed'] else '#6c757d'};
        }}
        </style>
        """, unsafe_allow_html=True)
        
        # 3カラムレイアウト
        col1, col2, col3 = st.columns([0.5, 8, 1.5])
        
        # チェックボックス
        with col1:
            checked = st.checkbox(
                "完了",
                value=task['is_completed'],
                key=f"check_{task['id']}",
                label_visibility="collapsed"
            )
            
            # 状態が変わったらコールバック実行
            if checked != task['is_completed'] and on_complete_toggle:
                on_complete_toggle(task['id'])
                st.rerun()
        
        # タスク内容
        with col2:
            # タイトル（完了済みなら取り消し線）
            title_style = "text-decoration: line-through; color: #999;" if task['is_completed'] else ""
            st.markdown(f"<p style='{title_style}'><strong>{task['title']}</strong></p>", unsafe_allow_html=True)
            
            # 説明
            if task.get('description'):
                st.caption(task['description'])
            
            # カテゴリと優先度
            priority_label = PRIORITY_LABELS.get(task['priority'], task['priority'])
            st.caption(f"🏷️ {task['category']} | 優先度: {priority_label}")
        
        # アクションボタン
        if show_actions:
            with col3:
                btn_col1, btn_col2 = st.columns(2)
                
                with btn_col1:
                    if st.button("✏️", key=f"edit_{task['id']}", help="編集"):
                        if on_edit:
                            on_edit(task['id'])
                
                with btn_col2:
                    if st.button("🗑️", key=f"del_{task['id']}", help="削除"):
                        if on_delete:
                            on_delete(task['id'])
```

### 完了確認

1. [ ] ファイルが作成されている
2. [ ] 関数が定義されている
3. [ ] 優先度に応じた色分けがされている
4. [ ] 完了済みタスクの表示が変わる

次のプロンプトで実際に使用します。コミットしてください。

---

## プロンプト 2-3: タスク管理ページ作成

### 目的
タスクの追加・編集・削除・完了チェックができるページを作成する

### ファイルパス
`pages/1_📋_Tasks.py`

### 実装内容

タスク管理の中心となるページを作成してください。

#### ページ構成
1. タイトルと日付表示
2. タスク追加フォーム（expander）
3. フィルタ（完了/未完了切り替え）
4. タスク一覧

#### タスク追加フォーム
- タイトル（必須）
- 説明（任意）
- カテゴリ選択
- 優先度選択

#### タスク一覧
- タスクカードコンポーネントを使用
- 完了チェック、編集、削除が可能

#### 編集機能（インライン）
- 編集ボタンクリックでフォーム表示
- 保存/キャンセルボタン

#### 削除機能
- 確認ダイアログ表示
- 確認後削除

### 参考コード

```python
import streamlit as st
from datetime import date
from components.auth import is_authenticated, get_current_user
from components.task_card import render_task_card
from utils.database import (
    get_tasks_by_date,
    create_task,
    update_task,
    delete_task,
    toggle_task_completion
)

st.set_page_config(
    page_title="タスク管理",
    page_icon="📋",
    layout="wide"
)

# 認証チェック
if not is_authenticated():
    st.switch_page("pages/0_🔐_Auth.py")

user = get_current_user()
today = date.today()
today_str = today.isoformat()

# タイトル
st.title("📋 今日のタスク")
st.caption(f"{today.strftime('%Y年%m月%d日')} ({['月','火','水','木','金','土','日'][today.weekday()]}曜日)")

# タスク追加フォーム
with st.expander("➕ 新しいタスクを追加", expanded=False):
    with st.form("add_task_form"):
        title = st.text_input("タスク名*", max_chars=200)
        description = st.text_area("説明（任意）")
        
        col1, col2 = st.columns(2)
        with col1:
            category = st.selectbox(
                "カテゴリ*",
                ["運動", "学習", "健康管理", "自己研鑽", "その他"]
            )
        with col2:
            priority_display = st.selectbox("優先度*", ["高", "中", "低"], index=1)
            priority_map = {"高": "high", "中": "medium", "低": "low"}
            priority = priority_map[priority_display]
        
        if st.form_submit_button("追加", use_container_width=True):
            if not title.strip():
                st.error("タスク名を入力してください")
            else:
                task_data = {
                    "title": title,
                    "description": description,
                    "category": category,
                    "priority": priority,
                    "task_date": today_str
                }
                
                created = create_task(user['id'], task_data)
                if created:
                    st.success("✓ タスクを追加しました")
                    st.rerun()
                else:
                    st.error("タスクの追加に失敗しました")

st.divider()

# フィルタ
col1, col2 = st.columns([1, 4])
with col1:
    show_completed = st.checkbox("完了済みを表示", value=True)

# タスク取得
tasks = get_tasks_by_date(user['id'], today_str)

# フィルタ適用
if not show_completed:
    tasks = [t for t in tasks if not t['is_completed']]

# タスク一覧表示
if not tasks:
    st.info("📝 今日のタスクはまだありません")
else:
    st.subheader(f"タスク一覧（{len(tasks)}件）")
    
    for task in tasks:
        # 編集モードチェック
        editing_key = f"editing_{task['id']}"
        
        if st.session_state.get(editing_key):
            # 編集フォーム表示
            with st.form(f"edit_form_{task['id']}"):
                new_title = st.text_input("タスク名", value=task['title'], max_chars=200)
                new_description = st.text_area("説明", value=task.get('description', ''))
                
                col1, col2 = st.columns(2)
                with col1:
                    new_category = st.selectbox(
                        "カテゴリ",
                        ["運動", "学習", "健康管理", "自己研鑽", "その他"],
                        index=["運動", "学習", "健康管理", "自己研鑽", "その他"].index(task['category'])
                    )
                with col2:
                    priority_labels = ["高", "中", "低"]
                    priority_values = ["high", "medium", "low"]
                    current_index = priority_values.index(task['priority'])
                    
                    new_priority_display = st.selectbox("優先度", priority_labels, index=current_index)
                    new_priority = priority_values[priority_labels.index(new_priority_display)]
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    if st.form_submit_button("保存", use_container_width=True):
                        updates = {
                            "title": new_title,
                            "description": new_description,
                            "category": new_category,
                            "priority": new_priority
                        }
                        
                        if update_task(task['id'], updates):
                            st.success("✓ タスクを更新しました")
                            del st.session_state[editing_key]
                            st.rerun()
                        else:
                            st.error("更新に失敗しました")
                
                with col_cancel:
                    if st.form_submit_button("キャンセル", use_container_width=True):
                        del st.session_state[editing_key]
                        st.rerun()
        else:
            # 通常表示（タスクカード）
            def on_edit(task_id):
                st.session_state[f"editing_{task_id}"] = True
            
            def on_delete(task_id):
                st.session_state[f"deleting_{task_id}"] = True
            
            # 削除確認
            deleting_key = f"deleting_{task['id']}"
            if st.session_state.get(deleting_key):
                st.warning(f"「{task['title']}」を削除しますか？")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("削除する", key=f"confirm_del_{task['id']}", type="primary"):
                        if delete_task(task['id']):
                            st.success("✓ タスクを削除しました")
                            del st.session_state[deleting_key]
                            st.rerun()
                        else:
                            st.error("削除に失敗しました")
                with col2:
                    if st.button("キャンセル", key=f"cancel_del_{task['id']}"):
                        del st.session_state[deleting_key]
                        st.rerun()
            else:
                # タスクカード表示
                render_task_card(
                    task,
                    on_complete_toggle=toggle_task_completion,
                    on_edit=on_edit,
                    on_delete=on_delete
                )
```

### 完了確認

以下を実際に試してください:

1. [ ] タスク追加（全項目入力）
2. [ ] タスク追加（タイトルのみ）
3. [ ] タイトル空で追加（エラー表示）
4. [ ] タスク完了チェック
5. [ ] タスク未完了に戻す
6. [ ] タスク編集（保存）
7. [ ] タスク編集（キャンセル）
8. [ ] タスク削除（確認あり）
9. [ ] 完了済みフィルタ
10. [ ] 複数タスク追加後の表示順確認（優先度順）

すべて動作したら、Phase 2完了としてコミットしてください。

---

# Phase 3: ダッシュボード（3日間）

## プロンプト 3-1: ダッシュボード完成

### 目的
Home.pyをダッシュボードとして完成させる

### ファイルパス
`Home.py`

### 実装内容

ダッシュボードのメインコンテンツを実装してください。

#### レイアウト
- 3カラム: 左（進捗）、中央（タスク）、右（クイックアクション）

#### 左カラム: モンクモード進捗
- 継続日数（Sprint 1では固定値「1日目」）
- 後のスプリントで実装予定

#### 中央カラム: 今日のタスク
- 今日のタスク一覧（最大5件）
- 達成率プログレスバー
- タスク管理ページへのボタン

#### 右カラム: クイックアクション
- 「➕ タスク追加」ボタン

### 参考コード

```python
import streamlit as st
from datetime import date
from components.auth import is_authenticated, logout, get_current_user
from utils.database import get_tasks_by_date, get_task_completion_rate

st.set_page_config(
    page_title="モンクモード",
    page_icon="🧘",
    layout="wide"
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
    st.caption(f"{today.strftime('%Y年%m月%d日')} ({['月','火','水','木','金','土','日'][today.weekday()]}曜日)")
with col2:
    if st.button("ログアウト", type="secondary"):
        logout()
        st.rerun()

st.divider()

# メインコンテンツ（3カラム）
col_left, col_center, col_right = st.columns([2, 5, 2])

# 左カラム: 進捗
with col_left:
    st.subheader("📊 進捗")
    st.metric("継続日数", "1日目")
    st.caption("※後のスプリントで実装予定")
    
    st.divider()
    
    # 簡易統計
    tasks = get_tasks_by_date(user['id'], today_str)
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t['is_completed']])
    
    st.metric("今日のタスク", f"{completed_tasks}/{total_tasks}")

# 中央カラム: 今日のタスク
with col_center:
    st.subheader("📋 今日のタスク")
    
    tasks = get_tasks_by_date(user['id'], today_str)
    
    if tasks:
        # 達成率
        completion_rate = get_task_completion_rate(user['id'], today_str)
        st.progress(completion_rate, text=f"達成率: {int(completion_rate * 100)}%")
        
        st.write("")  # スペース
        
        # タスク表示（最大5件）
        display_tasks = tasks[:5]
        
        for task in display_tasks:
            # チェックボックスは表示のみ（disabled）
            col_check, col_task = st.columns([0.5, 9.5])
            
            with col_check:
                st.checkbox(
                    "",
                    value=task['is_completed'],
                    key=f"home_task_{task['id']}",
                    disabled=True,
                    label_visibility="collapsed"
                )
            
            with col_task:
                # 完了済みはグレー表示
                if task['is_completed']:
                    st.markdown(f"~~{task['title']}~~ 🏷️ {task['category']}", help=task.get('description', ''))
                else:
                    st.markdown(f"**{task['title']}** 🏷️ {task['category']}", help=task.get('description', ''))
        
        # 5件を超える場合
        if len(tasks) > 5:
            st.caption(f"他 {len(tasks) - 5} 件のタスク")
        
        st.write("")  # スペース
        
        # タスク管理ページへ
        if st.button("📋 タスク管理へ", use_container_width=True):
            st.switch_page("pages/1_📋_Tasks.py")
    
    else:
        # タスクがない場合
        st.info("📝 今日のタスクはまだありません")
        
        if st.button("➕ 最初のタスクを追加", use_container_width=True):
            st.switch_page("pages/1_📋_Tasks.py")

# 右カラム: クイックアクション
with col_right:
    st.subheader("🚀 クイック")
    
    if st.button("➕ タスク追加", use_container_width=True):
        st.switch_page("pages/1_📋_Tasks.py")
    
    st.divider()
    
    st.caption("その他の機能は後のスプリントで追加予定")
```

### 完了確認

以下を確認してください:

1. [ ] ダッシュボードが表示される
2. [ ] 今日のタスクが表示される（最大5件）
3. [ ] 達成率が正しく表示される
4. [ ] タスクが0件の時の表示が適切
5. [ ] タスクが6件以上の時に「他X件」表示
6. [ ] タスク管理ページへのボタンが動作する
7. [ ] チェックボックスがdisabled（クリック不可）

**統合テスト**:
1. タスク管理ページで3件追加
2. 1件完了にする
3. ダッシュボードに戻る
4. 達成率33%が表示される

すべて動作したら、Phase 3完了としてコミットしてください。

---

# Phase 4: テスト・調整（3日間）

## プロンプト 4-1: 統合テスト実施

### 目的
Sprint 1の全機能を通してテストし、問題を修正する

### テストシナリオ

以下のテストを実施し、すべてパスすることを確認してください。

#### 1. 認証フロー
- [ ] 新規ユーザー登録（正常系）
  - 表示名、メール、パスワード入力
  - 登録成功 → ダッシュボード表示
- [ ] 既存メールで登録（エラー表示確認）
- [ ] パスワード8文字未満（エラー表示確認）
- [ ] パスワード不一致（エラー表示確認）
- [ ] ログイン（正常系）
- [ ] 間違ったパスワードでログイン（エラー表示確認）
- [ ] ログアウト → ログイン画面へリダイレクト
- [ ] 未認証でHome.pyアクセス → ログイン画面へリダイレクト
- [ ] 未認証でタスク管理アクセス → ログイン画面へリダイレクト

#### 2. タスク管理
- [ ] タスク追加（全項目入力）→ 正常に追加される
- [ ] タスク追加（タイトルのみ）→ 正常に追加される
- [ ] タイトル空でタスク追加 → エラー表示
- [ ] タスク完了チェック → is_completedがtrueになる
- [ ] タスク未完了に戻す → is_completedがfalseになる
- [ ] タスク編集（タイトル変更）→ 保存 → 変更反映
- [ ] タスク編集 → キャンセル → 変更されない
- [ ] タスク削除 → 確認ダイアログ表示 → 削除
- [ ] タスク削除 → 確認ダイアログ → キャンセル → 削除されない
- [ ] 同じ日に複数タスク追加 → すべて表示される
- [ ] 優先度による自動ソート確認（高→中→低）
- [ ] 完了済みフィルタ → 完了タスクが非表示になる

#### 3. ダッシュボード
- [ ] タスク0件 → 「まだありません」メッセージ表示
- [ ] タスク1件 → 1件表示、達成率0%
- [ ] タスク3件、1件完了 → 達成率33%
- [ ] タスク5件 → 5件表示、「他X件」表示なし
- [ ] タスク7件 → 5件表示、「他2件」表示
- [ ] 達成率100% → プログレスバーが満タン
- [ ] 「タスク管理へ」ボタン → ページ遷移
- [ ] 「タスク追加」ボタン → ページ遷移

#### 4. UI/UX
- [ ] エラーメッセージが赤色
- [ ] 成功メッセージが緑色
- [ ] ボタンがすべてクリック可能
- [ ] フォーム送信後のページリロード
- [ ] ページ遷移がスムーズ
- [ ] 完了済みタスクがグレー表示
- [ ] 優先度による色分け

#### 5. データ整合性
- [ ] タスク追加後、データベースに保存確認
- [ ] タスク削除後、データベースから削除確認
- [ ] ユーザーAのタスクがユーザーBに見えない
- [ ] ログアウト → ログイン → データが保持されている

### 問題が見つかった場合

1. エラーログを確認（print文の出力）
2. 該当箇所を特定
3. 修正
4. 再テスト
5. すべてパスするまで繰り返し

### 完了確認

- [ ] すべてのテストがパスした
- [ ] エラーログに異常なし
- [ ] ユーザー体験がスムーズ

---

## プロンプト 4-2: コード品質改善

### 目的
コードの可読性、保守性を高める

### 改善項目

以下の観点でコードをレビューし、改善してください:

#### 1. コードの可読性
- [ ] 関数名・変数名が適切
- [ ] マジックナンバーを定数化
  ```python
  # ❌ 悪い例
  if len(password) < 8:
  
  # ✅ 良い例
  MIN_PASSWORD_LENGTH = 8
  if len(password) < MIN_PASSWORD_LENGTH:
  ```
- [ ] 重複コードを関数化

#### 2. ドキュメント
- [ ] すべての関数にdocstringがある
  ```python
  def create_task(user_id: str, task_data: dict) -> dict | None:
      """
      タスクを作成する
      
      Args:
          user_id: ユーザーID
          task_data: タスクデータ
      
      Returns:
          dict | None: 作成されたタスク、失敗時はNone
      """
  ```
- [ ] 複雑なロジックにコメント追加
- [ ] README.mdにセットアップ手順が記載されている

#### 3. エラーハンドリング
- [ ] すべてのDB操作でtry-except
- [ ] ユーザーフレンドリーなエラーメッセージ
- [ ] print()でエラーログ出力

#### 4. 型ヒント
- [ ] 関数の引数と戻り値に型ヒント
  ```python
  def get_tasks_by_date(user_id: str, date: str) -> list:
  ```

#### 5. 定数の整理
- [ ] utils/constants.py に定数をまとめる
  ```python
  # utils/constants.py
  
  # タスク関連
  TASK_CATEGORIES = [
      "運動",
      "学習",
      "健康管理",
      "自己研鑽",
      "その他"
  ]
  
  PRIORITY_VALUES = ["high", "medium", "low"]
  PRIORITY_LABELS = ["高", "中", "低"]
  
  PRIORITY_COLORS = {
      "high": "#FFE5E5",
      "medium": "#FFF4E5",
      "low": "#E5F2FF"
  }
  
  # 認証関連
  MIN_PASSWORD_LENGTH = 8
  ```

### 完了確認

- [ ] すべての関数にdocstringがある
- [ ] 型ヒントが追加されている
- [ ] 定数が整理されている
- [ ] コメントが適切
- [ ] エラーハンドリングが適切

---

## プロンプト 4-3: README.md更新

### 目的
プロジェクトのドキュメントを整備する

### ファイルパス
`README.md`

### 内容

以下の内容でREADME.mdを更新してください:

```markdown
# モンクモード支援システム

モンクモードの実践を支援するWebアプリケーション

## 機能（Sprint 1完了時点）

### ✅ 実装済み
- ユーザー認証（登録・ログイン・ログアウト）
- タスク管理
  - タスクの追加・編集・削除
  - タスクの完了チェック
  - カテゴリ・優先度設定
- ダッシュボード
  - 今日のタスク表示
  - 達成率表示

### 🚧 今後実装予定（Sprint 2以降）
- タスクの手動並び替え
- ポモドーロタイマー
- 習慣トラッカー
- 日記機能
- 統計・分析
- 通知機能

## 技術スタック

- **フロントエンド**: Streamlit
- **バックエンド**: Supabase (PostgreSQL)
- **認証**: Supabase Auth
- **言語**: Python 3.9+

## セットアップ

### 前提条件
- Python 3.9以上
- Supabaseアカウント

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd monk-mode-app
```

### 2. 仮想環境の作成

```bash
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate
```

### 3. パッケージのインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数の設定

`.env`ファイルを作成:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
```

### 5. データベースのセットアップ

Supabaseのプロジェクトで、`database_design.md`のSQLを実行してください。

### 6. アプリの起動

```bash
streamlit run Home.py
```

ブラウザで http://localhost:8501 を開きます。

## プロジェクト構造

```
monk-mode-app/
├── Home.py                  # ダッシュボード
├── pages/                   # 各ページ
│   ├── 0_🔐_Auth.py        # 認証
│   └── 1_📋_Tasks.py       # タスク管理
├── components/              # UIコンポーネント
│   ├── auth.py             # 認証関連
│   └── task_card.py        # タスクカード
├── utils/                   # ユーティリティ
│   ├── supabase_client.py  # Supabase接続
│   ├── database.py         # DB操作
│   └── constants.py        # 定数定義
├── .env                     # 環境変数（gitignore）
└── requirements.txt         # 依存パッケージ
```

## 使い方

### 1. アカウント作成
1. 「新規登録」タブから表示名、メール、パスワードを入力
2. 登録ボタンをクリック

### 2. タスク追加
1. 「タスク管理」ページへ
2. 「新しいタスクを追加」をクリック
3. タスク情報を入力して追加

### 3. タスク完了
1. タスク一覧のチェックボックスをクリック
2. ダッシュボードで達成率を確認

## 開発

### テスト実行

```bash
# 各モジュールのテスト
python utils/database.py
```

### コミットルール

- 機能追加: `feat: タスク管理機能追加`
- バグ修正: `fix: ログインエラー修正`
- ドキュメント: `docs: README更新`

## ライセンス

MIT License

## 開発者

[Your Name]
```

### 完了確認

- [ ] README.mdが更新されている
- [ ] セットアップ手順が明確
- [ ] 使い方の説明がある

---

# Sprint 1 完了チェックリスト

すべての項目がチェックされたら、Sprint 1完了です。

## 機能面
- [ ] ユーザー登録が動作する
- [ ] ログインが動作する
- [ ] ログアウトが動作する
- [ ] タスク追加が動作する
- [ ] タスク編集が動作する
- [ ] タスク削除が動作する
- [ ] タスク完了チェックが動作する
- [ ] ダッシュボードにタスクが表示される
- [ ] 達成率が正しく表示される

## 技術面
- [ ] Supabase接続が安定
- [ ] エラーハンドリングが適切
- [ ] RLSポリシーが機能
- [ ] コードが整理されている
- [ ] docstringがある
- [ ] 型ヒントがある

## ドキュメント
- [ ] README.mdが更新されている
- [ ] コードにコメントがある

## テスト
- [ ] すべてのテストシナリオがパス
- [ ] エラーログに異常なし

## デモ
「新規登録 → ログイン → タスク3件追加 → 1件完了 → ダッシュボードで達成率33%確認 → ログアウト」
が問題なく動作する

---

# 次のステップ

Sprint 1完了後:

1. **最終コミット**
   ```bash
   git add .
   git commit -m "Sprint 1完了: 認証・タスク管理・ダッシュボード実装"
   git push
   ```

2. **Sprint 1振り返り**
   - うまくいったこと
   - 改善すべきこと
   - Sprint 2への引き継ぎ事項

3. **Sprint 2準備**
   - タスク機能拡張（ドラグ&ドロップ）
   - ポモドーロタイマー
   - タスク連携タイマー

お疲れ様でした！ 🎉
