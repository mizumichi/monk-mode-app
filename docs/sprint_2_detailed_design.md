# Sprint 2 詳細設計書

## スプリント概要
- **目標**: タスクを効率的に管理し、集中して取り組める
- **期間**: 2週間
- **最終成果物**: タスク管理強化 + ポモドーロタイマー + タスク連携タイマー

---

## 📋 実装する機能一覧

### Phase 1: タスク管理機能の強化（5日間）
1. タスクの優先度設定（Sprint 1で実装済み、UI強化）
2. カテゴリ分類（Sprint 1で実装済み、フィルタ強化）
3. タスクの並び替え（ボタンで上下移動）
4. 未完了タスクの翌日繰り越し機能（手動選択）

### Phase 2: ポモドーロタイマー（4日間）
1. 基本タイマー機能（作業/休憩の切り替え）
2. カスタマイズ可能な時間設定
3. 開始/一時停止/リセット
4. タイマー完了時の音声通知
5. セッション履歴の保存

### Phase 3: タスク連携タイマー（3日間）
1. タスクごとにタイマー起動
2. タスクに費やした時間の自動記録
3. 1日の総作業時間表示
4. タスク別作業時間表示

### Phase 4: テスト・調整（2日間）
1. 統合テスト
2. バグ修正
3. UI/UX調整

---

## 🎨 設計仕様詳細

## Phase 1: タスク管理機能の強化

### 1.1 タスクの並び替え機能

#### 1.1.1 実装方式
**選択**: ボタンで上下移動方式

**理由**:
- Streamlitのドラッグ&ドロップライブラリ（streamlit-sortables）は不安定
- ボタン方式はシンプルで確実
- モバイル対応も容易

#### 1.1.2 UI設計
```
┌─────────────────────────────────────────┐
│ [ ] タスクA                             │
│     説明...                              │
│     🏷️ 運動 | 優先度: 高                │
│              [↑] [↓] [編集] [削除]      │
└─────────────────────────────────────────┘
```

**ボタン配置**:
- ↑（上へ移動）: display_order を -1
- ↓（下へ移動）: display_order を +1
- 最上位のタスクは↑ボタン無効
- 最下位のタスクは↓ボタン無効

#### 1.1.3 データベース操作
```python
def move_task_up(task_id: str, user_id: str, date: str) -> bool:
    """
    タスクを上に移動
    
    Args:
        task_id: 移動するタスクID
        user_id: ユーザーID
        date: 対象日付
    
    Returns:
        bool: 成功時True
    """
    try:
        # 現在のタスクを取得
        current_task = supabase.table('daily_tasks')\
            .select('display_order')\
            .eq('id', task_id)\
            .single()\
            .execute()
        
        current_order = current_task.data['display_order']
        
        # 現在のタスクより1つ上のタスクを探す
        prev_task = supabase.table('daily_tasks')\
            .select('id, display_order')\
            .eq('user_id', user_id)\
            .eq('task_date', date)\
            .lt('display_order', current_order)\
            .order('display_order', desc=True)\
            .limit(1)\
            .execute()
        
        if not prev_task.data:
            return False  # 既に最上位
        
        prev_order = prev_task.data[0]['display_order']
        prev_id = prev_task.data[0]['id']
        
        # 順序を入れ替え
        supabase.table('daily_tasks')\
            .update({'display_order': prev_order})\
            .eq('id', task_id)\
            .execute()
        
        supabase.table('daily_tasks')\
            .update({'display_order': current_order})\
            .eq('id', prev_id)\
            .execute()
        
        return True
        
    except Exception as e:
        print(f"Error moving task up: {e}")
        return False

def move_task_down(task_id: str, user_id: str, date: str) -> bool:
    """
    タスクを下に移動
    
    実装は move_task_up と同様、gt（greater than）で次のタスクを検索
    """
    # 実装省略（move_task_upの逆）
```

#### 1.1.4 注意点
- **競合回避**: 同時に複数ユーザーが操作しても問題ない（user_idで分離）
- **display_order の正規化**: 定期的に0から連番に振り直す必要はない（差分があれば動作する）

---

### 1.2 カテゴリフィルタの強化

#### 1.2.1 現状（Sprint 1）
- 完了/未完了の切り替えのみ

#### 1.2.2 Sprint 2での追加
**フィルタUI**:
```python
col1, col2, col3 = st.columns([2, 2, 3])

with col1:
    show_completed = st.checkbox("完了済みを表示", value=True)

with col2:
    selected_category = st.selectbox(
        "カテゴリ",
        ["すべて", "運動", "学習", "健康管理", "自己研鑽", "その他"]
    )

with col3:
    selected_priority = st.selectbox(
        "優先度",
        ["すべて", "高", "中", "低"]
    )
```

**フィルタロジック**:
```python
# タスク取得
tasks = get_tasks_by_date(user['id'], today_str)

# 完了フィルタ
if not show_completed:
    tasks = [t for t in tasks if not t['is_completed']]

# カテゴリフィルタ
if selected_category != "すべて":
    tasks = [t for t in tasks if t['category'] == selected_category]

# 優先度フィルタ
if selected_priority != "すべて":
    priority_map = {"高": "high", "中": "medium", "低": "low"}
    tasks = [t for t in tasks if t['priority'] == priority_map[selected_priority]]
```

---

### 1.3 未完了タスクの繰り越し機能（手動選択式）

#### 1.3.1 UI配置
**場所**: タスク管理ページ（1_📋_Tasks.py）の上部

**デザイン**:
```python
# 前日の未完了タスクがあるかチェック
yesterday = (date.today() - timedelta(days=1)).isoformat()
yesterday_incomplete = get_incomplete_tasks(user['id'], yesterday)

if yesterday_incomplete:
    with st.expander(f"⚠️ 前日の未完了タスク（{len(yesterday_incomplete)}件）", expanded=True):
        st.info("繰り越すタスクを選択してください")
        
        selected_tasks = []
        for task in yesterday_incomplete:
            if st.checkbox(task['title'], key=f"carryover_{task['id']}"):
                selected_tasks.append(task['id'])
        
        if st.button("選択したタスクを今日に繰り越す", disabled=not selected_tasks):
            carryover_tasks(selected_tasks, date.today().isoformat())
            st.success(f"✓ {len(selected_tasks)}件のタスクを繰り越しました")
            st.rerun()
```

#### 1.3.2 繰り越しロジック
```python
def get_incomplete_tasks(user_id: str, date: str) -> list:
    """
    指定日の未完了タスクを取得
    
    Args:
        user_id: ユーザーID
        date: 日付（ISO形式）
    
    Returns:
        list: 未完了タスクのリスト
    """
    try:
        response = supabase.table('daily_tasks')\
            .select('*')\
            .eq('user_id', user_id)\
            .eq('task_date', date)\
            .eq('is_completed', False)\
            .execute()
        
        return response.data
    except Exception as e:
        print(f"Error fetching incomplete tasks: {e}")
        return []

def carryover_tasks(task_ids: list, new_date: str) -> bool:
    """
    タスクを新しい日付に繰り越す（日付を更新）
    
    Args:
        task_ids: 繰り越すタスクIDのリスト
        new_date: 新しい日付（ISO形式）
    
    Returns:
        bool: 成功時True
    """
    try:
        for task_id in task_ids:
            supabase.table('daily_tasks')\
                .update({
                    'task_date': new_date,
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('id', task_id)\
                .execute()
        
        return True
        
    except Exception as e:
        print(f"Error carrying over tasks: {e}")
        return False
```

#### 1.3.3 注意点
- **繰り越し方式**: 日付のみ更新（元のタスクを移動）
- **履歴**: タスクは移動するだけなので、元の日付の履歴は残らない
- **display_order**: 繰り越し先の日付で自動的に最後尾に追加される

---

### 1.4 タスクカードコンポーネントの更新

#### 1.4.1 変更点
Sprint 1の `render_task_card` に **↑↓ボタンを追加**

```python
def render_task_card(
    task: dict,
    on_complete_toggle: callable = None,
    on_edit: callable = None,
    on_delete: callable = None,
    on_move_up: callable = None,      # 新規追加
    on_move_down: callable = None,    # 新規追加
    show_actions: bool = True,
    is_first: bool = False,           # 新規追加
    is_last: bool = False             # 新規追加
) -> None:
    """
    タスクカードをレンダリング（Sprint 2版）
    
    Args:
        task: タスクデータ
        on_complete_toggle: 完了切り替え時のコールバック
        on_edit: 編集時のコールバック
        on_delete: 削除時のコールバック
        on_move_up: 上へ移動時のコールバック（新規）
        on_move_down: 下へ移動時のコールバック（新規）
        show_actions: アクションボタンを表示するか
        is_first: 最上位のタスクか（新規）
        is_last: 最下位のタスクか（新規）
    """
    
    # ... 既存のコード ...
    
    # アクションボタン
    if show_actions:
        with col3:
            btn_cols = st.columns(4)  # 4列に変更
            
            # 上へ移動ボタン
            with btn_cols[0]:
                if st.button("↑", key=f"up_{task['id']}", disabled=is_first, help="上へ"):
                    if on_move_up:
                        on_move_up(task['id'])
            
            # 下へ移動ボタン
            with btn_cols[1]:
                if st.button("↓", key=f"down_{task['id']}", disabled=is_last, help="下へ"):
                    if on_move_down:
                        on_move_down(task['id'])
            
            # 編集ボタン
            with btn_cols[2]:
                if st.button("✏️", key=f"edit_{task['id']}", help="編集"):
                    if on_edit:
                        on_edit(task['id'])
            
            # 削除ボタン
            with btn_cols[3]:
                if st.button("🗑️", key=f"del_{task['id']}", help="削除"):
                    if on_delete:
                        on_delete(task['id'])
```

---

## Phase 2: ポモドーロタイマー

### 2.1 基本仕様

#### 2.1.1 デフォルト時間設定
```python
# utils/constants.py
POMODORO_WORK_MINUTES = 25
POMODORO_SHORT_BREAK_MINUTES = 5
POMODORO_LONG_BREAK_MINUTES = 15
POMODORO_SESSIONS_UNTIL_LONG_BREAK = 4
```

#### 2.1.2 タイマー状態
```python
# セッション状態の構造
st.session_state = {
    # タイマー状態
    'timer_running': bool,              # タイマー稼働中か
    'timer_start_time': datetime,       # 開始時刻
    'timer_duration_seconds': int,      # 設定時間（秒）
    'timer_session_type': str,          # 'work' / 'short_break' / 'long_break'
    'pomodoro_count': int,              # 完了したポモドーロ数
    
    # カスタム設定
    'custom_work_minutes': int,
    'custom_short_break_minutes': int,
    'custom_long_break_minutes': int,
}
```

### 2.2 実装方式（シンプル実装）

#### 2.2.1 技術的制約
- Streamlitはリアルタイム更新が苦手
- `st.rerun()`を使った定期更新は重い

#### 2.2.2 選択した実装方式
**開始時刻記録方式**:
1. タイマー開始時に `start_time` と `duration` を記録
2. 表示時に現在時刻との差分で残り時間を計算
3. ユーザーが手動で「更新」ボタンをクリック、または自動リロード（オプション）

```python
def get_remaining_seconds() -> int:
    """
    残り時間を計算
    
    Returns:
        int: 残り秒数（負の場合は0）
    """
    if not st.session_state.get('timer_running'):
        return 0
    
    start_time = st.session_state['timer_start_time']
    duration = st.session_state['timer_duration_seconds']
    
    elapsed = (datetime.now() - start_time).total_seconds()
    remaining = duration - elapsed
    
    return max(0, int(remaining))

def format_time(seconds: int) -> str:
    """
    秒を MM:SS 形式にフォーマット
    
    Args:
        seconds: 秒数
    
    Returns:
        str: MM:SS形式の文字列
    """
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"
```

### 2.3 UI設計

#### 2.3.1 ページ構成（2_⏱️_Timer.py）

```python
st.title("⏱️ ポモドーロタイマー")

# タブで切り替え
tab1, tab2 = st.tabs(["ポモドーロ", "履歴"])

with tab1:
    # メインタイマーUI
    render_pomodoro_timer()

with tab2:
    # セッション履歴
    render_session_history()
```

#### 2.3.2 タイマーUI詳細

```python
def render_pomodoro_timer():
    """ポモドーロタイマーのメインUI"""
    
    # 現在の状態
    timer_running = st.session_state.get('timer_running', False)
    session_type = st.session_state.get('timer_session_type', 'work')
    
    # セッションタイプ表示
    session_labels = {
        'work': '🔥 作業中',
        'short_break': '☕ 短い休憩',
        'long_break': '🌟 長い休憩'
    }
    
    st.subheader(session_labels.get(session_type, ''))
    
    # 残り時間表示
    if timer_running:
        remaining = get_remaining_seconds()
        
        if remaining > 0:
            # 大きく表示
            st.markdown(f"<h1 style='text-align: center; font-size: 72px;'>{format_time(remaining)}</h1>", 
                        unsafe_allow_html=True)
            
            # プログレスバー
            progress = 1 - (remaining / st.session_state['timer_duration_seconds'])
            st.progress(progress)
            
            # 更新ボタン
            if st.button("🔄 更新", key="refresh_timer"):
                st.rerun()
            
            # 自動リロード（オプション）
            if st.checkbox("自動更新（5秒ごと）", value=False):
                time.sleep(5)
                st.rerun()
        
        else:
            # タイマー完了
            st.success("✓ セッション完了！")
            
            # 音声通知（ブラウザの音声再生）
            st.markdown("""
            <audio autoplay>
                <source src="data:audio/wav;base64,..." type="audio/wav">
            </audio>
            """, unsafe_allow_html=True)
            
            # 次のセッションへ
            if st.button("次のセッションへ"):
                start_next_session()
                st.rerun()
    
    else:
        # タイマー未稼働
        st.markdown("<h1 style='text-align: center; font-size: 72px;'>00:00</h1>", 
                    unsafe_allow_html=True)
    
    st.divider()
    
    # 時間設定
    with st.expander("⚙️ 時間設定", expanded=not timer_running):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            work_minutes = st.number_input(
                "作業時間（分）",
                min_value=1,
                max_value=60,
                value=st.session_state.get('custom_work_minutes', POMODORO_WORK_MINUTES),
                disabled=timer_running
            )
        
        with col2:
            short_break = st.number_input(
                "短い休憩（分）",
                min_value=1,
                max_value=30,
                value=st.session_state.get('custom_short_break_minutes', POMODORO_SHORT_BREAK_MINUTES),
                disabled=timer_running
            )
        
        with col3:
            long_break = st.number_input(
                "長い休憩（分）",
                min_value=1,
                max_value=60,
                value=st.session_state.get('custom_long_break_minutes', POMODORO_LONG_BREAK_MINUTES),
                disabled=timer_running
            )
        
        # 設定を保存
        if not timer_running:
            st.session_state['custom_work_minutes'] = work_minutes
            st.session_state['custom_short_break_minutes'] = short_break
            st.session_state['custom_long_break_minutes'] = long_break
    
    st.divider()
    
    # コントロールボタン
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if not timer_running:
            if st.button("▶️ 開始", use_container_width=True, type="primary"):
                start_timer('work', work_minutes * 60)
                st.rerun()
        else:
            if st.button("⏸️ 一時停止", use_container_width=True):
                pause_timer()
                st.rerun()
    
    with col2:
        if st.button("⏹️ リセット", use_container_width=True, disabled=not timer_running):
            reset_timer()
            st.rerun()
    
    with col3:
        if st.button("⏭️ スキップ", use_container_width=True, disabled=not timer_running):
            skip_session()
            st.rerun()
```

### 2.4 タイマー制御関数

```python
def start_timer(session_type: str, duration_seconds: int) -> None:
    """
    タイマーを開始
    
    Args:
        session_type: 'work', 'short_break', 'long_break'
        duration_seconds: タイマー時間（秒）
    """
    st.session_state['timer_running'] = True
    st.session_state['timer_start_time'] = datetime.now()
    st.session_state['timer_duration_seconds'] = duration_seconds
    st.session_state['timer_session_type'] = session_type

def pause_timer() -> None:
    """タイマーを一時停止"""
    # 残り時間を計算
    remaining = get_remaining_seconds()
    
    # 新しい duration として保存
    st.session_state['timer_duration_seconds'] = remaining
    st.session_state['timer_running'] = False

def reset_timer() -> None:
    """タイマーをリセット"""
    st.session_state['timer_running'] = False
    st.session_state['pomodoro_count'] = 0

def skip_session() -> None:
    """現在のセッションをスキップ"""
    start_next_session()

def start_next_session() -> None:
    """次のセッションを開始"""
    session_type = st.session_state.get('timer_session_type', 'work')
    pomodoro_count = st.session_state.get('pomodoro_count', 0)
    
    if session_type == 'work':
        # 作業完了 → 休憩へ
        pomodoro_count += 1
        st.session_state['pomodoro_count'] = pomodoro_count
        
        # セッション記録
        save_pomodoro_session('work', st.session_state['timer_duration_seconds'])
        
        # 4セットごとに長い休憩
        if pomodoro_count % POMODORO_SESSIONS_UNTIL_LONG_BREAK == 0:
            duration = st.session_state.get('custom_long_break_minutes', POMODORO_LONG_BREAK_MINUTES) * 60
            start_timer('long_break', duration)
        else:
            duration = st.session_state.get('custom_short_break_minutes', POMODORO_SHORT_BREAK_MINUTES) * 60
            start_timer('short_break', duration)
    
    else:
        # 休憩完了 → 作業へ
        save_pomodoro_session(session_type, st.session_state['timer_duration_seconds'])
        
        duration = st.session_state.get('custom_work_minutes', POMODORO_WORK_MINUTES) * 60
        start_timer('work', duration)
```

### 2.5 セッション履歴の保存

#### 2.5.1 データベース操作
```python
def save_pomodoro_session(session_type: str, duration_seconds: int, task_id: str = None) -> dict | None:
    """
    ポモドーロセッションを記録
    
    Args:
        session_type: 'work', 'short_break', 'long_break'
        duration_seconds: セッション時間（秒）
        task_id: 関連タスクID（オプション）
    
    Returns:
        dict | None: 保存されたセッション、失敗時はNone
    """
    try:
        user = get_current_user()
        
        session_data = {
            'user_id': user['id'],
            'session_type': session_type,
            'duration_minutes': duration_seconds // 60,
            'started_at': (datetime.now() - timedelta(seconds=duration_seconds)).isoformat(),
            'ended_at': datetime.now().isoformat(),
            'completed': True
        }
        
        if task_id:
            session_data['task_id'] = task_id
        
        response = supabase.table('pomodoro_sessions')\
            .insert(session_data)\
            .execute()
        
        return response.data[0] if response.data else None
        
    except Exception as e:
        print(f"Error saving pomodoro session: {e}")
        return None
```

#### 2.5.2 履歴表示
```python
def render_session_history():
    """セッション履歴を表示"""
    user = get_current_user()
    today = date.today().isoformat()
    
    # 今日のセッション取得
    sessions = supabase.table('pomodoro_sessions')\
        .select('*')\
        .eq('user_id', user['id'])\
        .gte('started_at', f"{today}T00:00:00")\
        .order('started_at', desc=True)\
        .execute()
    
    if not sessions.data:
        st.info("今日のセッション履歴はまだありません")
        return
    
    # 統計
    total_work_minutes = sum(
        s['duration_minutes'] 
        for s in sessions.data 
        if s['session_type'] == 'work'
    )
    
    st.metric("今日の総作業時間", f"{total_work_minutes}分")
    
    st.divider()
    
    # セッション一覧
    st.subheader("セッション履歴")
    
    session_labels = {
        'work': '🔥 作業',
        'short_break': '☕ 短い休憩',
        'long_break': '🌟 長い休憩'
    }
    
    for session in sessions.data:
        with st.container():
            col1, col2, col3 = st.columns([2, 3, 2])
            
            with col1:
                st.write(session_labels.get(session['session_type'], ''))
            
            with col2:
                start_time = datetime.fromisoformat(session['started_at'])
                st.caption(start_time.strftime('%H:%M'))
            
            with col3:
                st.caption(f"{session['duration_minutes']}分")
```

### 2.6 音声通知

#### 2.6.1 実装方式
**HTML5 Audio要素を使用**:
```python
# タイマー完了時
def play_notification_sound():
    """通知音を再生"""
    # Base64エンコードされた音声データ
    # 実際には assets/sounds/timer_done.mp3 を base64 化
    audio_base64 = "..."
    
    st.markdown(f"""
    <audio autoplay>
        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
    </audio>
    """, unsafe_allow_html=True)
```

#### 2.6.2 音声ファイル
- **場所**: `assets/sounds/timer_done.mp3`
- **長さ**: 3秒程度
- **音量**: 中程度（ユーザーの通知設定に依存）

---

## Phase 3: タスク連携タイマー

### 3.1 連携方式

#### 3.1.1 タスク一覧からタイマー起動
**タスクカードに「⏱️ タイマー」ボタンを追加**:

```python
def render_task_card(
    task: dict,
    # ... 既存の引数 ...
    on_start_timer: callable = None,  # 新規追加
    # ...
) -> None:
    """
    タスクカードをレンダリング（Phase 3版）
    """
    
    # ... 既存のコード ...
    
    # アクションボタン
    if show_actions:
        with col3:
            btn_cols = st.columns(5)  # 5列に変更
            
            # タイマーボタン（新規）
            with btn_cols[0]:
                if st.button("⏱️", key=f"timer_{task['id']}", help="タイマー"):
                    if on_start_timer:
                        on_start_timer(task['id'])
            
            # 既存のボタン...
```

**タイマー起動処理**:
```python
def on_start_timer(task_id: str):
    """タスクのタイマーを起動"""
    st.session_state['timer_task_id'] = task_id
    st.switch_page("pages/2_⏱️_Timer.py")
```

#### 3.1.2 タイマーページでタスク選択
**タイマーページ（2_⏱️_Timer.py）にタスク選択を追加**:

```python
# タイマーページの冒頭
st.title("⏱️ ポモドーロタイマー")

# タスク選択
user = get_current_user()
today = date.today().isoformat()
tasks = get_tasks_by_date(user['id'], today)

# 未完了タスクのみ
incomplete_tasks = [t for t in tasks if not t['is_completed']]

if incomplete_tasks:
    selected_task_id = st.selectbox(
        "タスクを選択（オプション）",
        options=["なし"] + [t['id'] for t in incomplete_tasks],
        format_func=lambda x: "なし" if x == "なし" else next(t['title'] for t in incomplete_tasks if t['id'] == x),
        key="selected_task_for_timer"
    )
    
    # セッション状態に保存
    if selected_task_id != "なし":
        st.session_state['timer_task_id'] = selected_task_id
    else:
        st.session_state['timer_task_id'] = None

st.divider()
```

### 3.2 作業時間の記録

#### 3.2.1 データベース更新
**タスクテーブルに作業時間を記録**:

```python
def update_task_work_time(task_id: str, minutes: int) -> bool:
    """
    タスクの作業時間を更新
    
    Args:
        task_id: タスクID
        minutes: 追加する作業時間（分）
    
    Returns:
        bool: 成功時True
    """
    try:
        # 現在の作業時間を取得
        task = supabase.table('daily_tasks')\
            .select('total_work_minutes')\
            .eq('id', task_id)\
            .single()\
            .execute()
        
        current_minutes = task.data.get('total_work_minutes', 0)
        new_total = current_minutes + minutes
        
        # 更新
        supabase.table('daily_tasks')\
            .update({'total_work_minutes': new_total})\
            .eq('id', task_id)\
            .execute()
        
        return True
        
    except Exception as e:
        print(f"Error updating task work time: {e}")
        return False
```

#### 3.2.2 ポモドーロ完了時の処理
**`start_next_session()` を更新**:

```python
def start_next_session() -> None:
    """次のセッションを開始（Phase 3版）"""
    session_type = st.session_state.get('timer_session_type', 'work')
    pomodoro_count = st.session_state.get('pomodoro_count', 0)
    task_id = st.session_state.get('timer_task_id')  # タスクID取得
    
    if session_type == 'work':
        pomodoro_count += 1
        st.session_state['pomodoro_count'] = pomodoro_count
        
        # セッション記録（task_id付き）
        duration_minutes = st.session_state['timer_duration_seconds'] // 60
        save_pomodoro_session('work', st.session_state['timer_duration_seconds'], task_id)
        
        # タスクの作業時間を更新
        if task_id:
            update_task_work_time(task_id, duration_minutes)
        
        # ... 休憩へ ...
    
    else:
        # 休憩完了 → 作業へ
        save_pomodoro_session(session_type, st.session_state['timer_duration_seconds'])
        
        duration = st.session_state.get('custom_work_minutes', POMODORO_WORK_MINUTES) * 60
        start_timer('work', duration)
```

### 3.3 統計表示

#### 3.3.1 ダッシュボードへの追加
**Home.py の左カラムに追加**:

```python
with col_left:
    st.subheader("📊 進捗")
    st.metric("継続日数", "1日目")
    
    st.divider()
    
    # タスク統計
    tasks = get_tasks_by_date(user['id'], today_str)
    total_tasks = len(tasks)
    completed_tasks = len([t for t in tasks if t['is_completed']])
    
    st.metric("今日のタスク", f"{completed_tasks}/{total_tasks}")
    
    # 作業時間統計（新規）
    total_work_minutes = sum(t.get('total_work_minutes', 0) for t in tasks)
    st.metric("今日の作業時間", f"{total_work_minutes}分")
```

#### 3.3.2 タスク別作業時間表示
**タスクカードに作業時間を表示**:

```python
def render_task_card(task: dict, ...):
    """タスクカードをレンダリング（Phase 3版）"""
    
    # ... 既存のコード ...
    
    with col2:
        # タイトル
        title_style = "text-decoration: line-through; color: #999;" if task['is_completed'] else ""
        st.markdown(f"<p style='{title_style}'><strong>{task['title']}</strong></p>", unsafe_allow_html=True)
        
        # 説明
        if task.get('description'):
            st.caption(task['description'])
        
        # カテゴリと優先度
        priority_label = PRIORITY_LABELS.get(task['priority'], task['priority'])
        st.caption(f"🏷️ {task['category']} | 優先度: {priority_label}")
        
        # 作業時間（新規）
        work_minutes = task.get('total_work_minutes', 0)
        if work_minutes > 0:
            st.caption(f"⏱️ 作業時間: {work_minutes}分")
```

---

## 🗄️ データベース変更

### 必要な変更

#### 1. daily_tasks テーブル
**追加カラム**:
```sql
ALTER TABLE daily_tasks 
ADD COLUMN total_work_minutes INTEGER DEFAULT 0;
```

#### 2. pomodoro_sessions テーブル
既に `database_design.md` で定義済み（変更なし）

---

## 🎨 UI/UX 詳細設計

### 1. タスク管理ページの最終レイアウト

```
┌─────────────────────────────────────────────────────────┐
│ 📋 今日のタスク                                          │
│ 2026年2月10日（月）                                      │
├─────────────────────────────────────────────────────────┤
│ ⚠️ 前日の未完了タスク（3件）[展開]                      │
│   [ ] タスクA                                           │
│   [ ] タスクB                                           │
│   [ ] タスクC                                           │
│   [選択したタスクを今日に繰り越す]                       │
├─────────────────────────────────────────────────────────┤
│ ➕ 新しいタスクを追加 [折りたたみ]                      │
├─────────────────────────────────────────────────────────┤
│ フィルタ:                                               │
│ [☑ 完了済みを表示] [すべて▼] [すべて▼]                │
├─────────────────────────────────────────────────────────┤
│ タスク一覧（5件）                                        │
│                                                         │
│ ┌───────────────────────────────────────────────────┐   │
│ │ [ ] タスクタイトル                                 │   │
│ │     説明文...                                      │   │
│ │     🏷️ 運動 | 優先度: 高 | ⏱️ 25分              │   │
│ │              [⏱️][↑][↓][✏️][🗑️]                │   │
│ └───────────────────────────────────────────────────┘   │
│ ... (他のタスク)                                        │
└─────────────────────────────────────────────────────────┘
```

### 2. タイマーページのレイアウト

```
┌─────────────────────────────────────────────────────────┐
│ ⏱️ ポモドーロタイマー                                    │
├─────────────────────────────────────────────────────────┤
│ タスクを選択: [タスクA ▼]                               │
├─────────────────────────────────────────────────────────┤
│ [ポモドーロ] [履歴]                                      │
├─────────────────────────────────────────────────────────┤
│              🔥 作業中                                   │
│                                                         │
│                  24:35                                  │
│              ████████░░░░░                              │
│                                                         │
│              [🔄 更新]                                  │
│              [☑ 自動更新（5秒ごと）]                    │
├─────────────────────────────────────────────────────────┤
│ ⚙️ 時間設定 [折りたたみ]                                │
│   作業時間: [25] 短休憩: [5] 長休憩: [15]              │
├─────────────────────────────────────────────────────────┤
│       [▶️ 開始]  [⏹️ リセット]  [⏭️ スキップ]         │
└─────────────────────────────────────────────────────────┘
```

### 3. ダッシュボードの更新レイアウト

```
┌──────────┬─────────────────────────┬──────────┐
│ 📊 進捗  │   📋 今日のタスク       │ 🚀 クイック│
│          │                         │          │
│ 継続日数 │ 達成率: 33% ████░░░░░  │ ➕ タスク │
│ 1日目    │                         │          │
│          │ [ ] タスクA             │ ⏱️ タイマー│
│ 今日の   │ [ ] タスクB             │          │
│ タスク   │ [x] タスクC             │          │
│ 2/3      │ ...                     │          │
│          │                         │          │
│ 作業時間 │ [📋 タスク管理へ]       │          │
│ 50分     │                         │          │
└──────────┴─────────────────────────┴──────────┘
```

---

## 🧪 テスト仕様

### Phase 1: タスク管理強化

#### 並び替え機能
- [ ] タスクを上に移動（↑ボタン）
- [ ] タスクを下に移動（↓ボタン）
- [ ] 最上位タスクの↑ボタンが無効
- [ ] 最下位タスクの↓ボタンが無効
- [ ] 並び替え後、リロードしても順序が保持される

#### カテゴリ・優先度フィルタ
- [ ] カテゴリフィルタが機能する
- [ ] 優先度フィルタが機能する
- [ ] 完了フィルタと併用できる
- [ ] フィルタクリアで全件表示

#### 繰り越し機能
- [ ] 前日の未完了タスクが表示される
- [ ] タスクを選択して繰り越せる
- [ ] 繰り越し後、今日のタスクに追加される
- [ ] 繰り越し元の日付からタスクが消える

### Phase 2: ポモドーロタイマー

#### 基本動作
- [ ] タイマー開始（25分）
- [ ] カウントダウン表示
- [ ] 一時停止→再開
- [ ] リセット
- [ ] スキップ

#### セッション遷移
- [ ] 作業完了→短い休憩
- [ ] 休憩完了→作業
- [ ] 4セット後→長い休憩

#### カスタム時間
- [ ] 作業時間を変更（例: 30分）
- [ ] 短休憩を変更（例: 3分）
- [ ] 長休憩を変更（例: 20分）
- [ ] 設定がセッション間で保持される

#### 履歴
- [ ] 完了したセッションが記録される
- [ ] 今日の総作業時間が正しい
- [ ] セッション一覧が表示される

#### 通知
- [ ] タイマー完了時に音が鳴る

### Phase 3: タスク連携タイマー

#### タスク選択
- [ ] タスク一覧から⏱️ボタンでタイマー起動
- [ ] タイマーページでタスク選択
- [ ] 選択したタスクが保持される

#### 作業時間記録
- [ ] ポモドーロ完了後、タスクに作業時間が記録される
- [ ] タスクカードに作業時間が表示される
- [ ] 複数セッション実施で累計される

#### 統計
- [ ] ダッシュボードに今日の総作業時間が表示される
- [ ] タスク別の作業時間が正しい
- [ ] 完了タスクの作業時間も表示される

---

## 📊 完了基準（Definition of Done）

Sprint 2は以下がすべて満たされた時点で完了:

### 機能面
- ✅ タスクの並び替えが正常動作
- ✅ カテゴリ・優先度フィルタが正常動作
- ✅ タスク繰り越しが正常動作
- ✅ ポモドーロタイマーが正常動作
- ✅ タスク連携タイマーが正常動作
- ✅ 作業時間の記録・表示が正常動作

### 技術面
- ✅ データベース変更が完了
- ✅ エラーハンドリングが適切
- ✅ コードが整理されている
- ✅ パフォーマンスが許容範囲

### ドキュメント
- ✅ README更新（新機能の説明）
- ✅ コードにdocstring/コメント

### デモ可能な状態
「タスクを3件追加 → 並び替え → ポモドーロタイマー起動（タスク選択） → 25分完了 → タスクに作業時間が記録される → ダッシュボードで総作業時間確認」

---

## 🚀 次のスプリントへの引き継ぎ事項

Sprint 2完了後、Sprint 3で以下を実装予定:
1. 習慣トラッカー
2. 習慣の可視化（グラフ）
3. ストリーク表示

Sprint 2で技術的負債として残る可能性:
- タイマーのリアルタイム更新（現在は手動更新）
- Web Push通知（現在は音声のみ）
- タスクのドラッグ&ドロップ（現在はボタン移動）

これらは優先度を見て後のスプリントで対応検討。

---

## 📝 実装時の注意点

### 1. タイマーの実装
- Streamlitの制約上、完璧なリアルタイム更新は困難
- ユーザーに「更新ボタン」の存在を明示
- 自動更新はオプション（重くなる可能性）

### 2. 並び替えの実装
- display_orderの値が連番である必要はない
- 順序が逆転しない限り問題なし
- パフォーマンス考慮で正規化は不要

### 3. データベース操作
- タスク移動時のトランザクション考慮
- 複数ユーザー同時操作でも問題ないか確認

### 4. UI/UX
- ボタンが多くなるので配置に注意
- モバイル表示の確認
- 色・アイコンで視覚的に区別

---

以上、Sprint 2詳細設計書
