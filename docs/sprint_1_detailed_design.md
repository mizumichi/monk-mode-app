# Sprint 1 詳細設計書

## スプリント概要
- **目標**: ログインして今日のタスクを管理できる
- **期間**: 2週間
- **最終成果物**: 認証機能 + タスク管理 + ダッシュボード

---

## 📋 実装する機能一覧

### Phase 1: 認証機能（3日間）
1. Supabase認証統合
2. ログイン/サインアップ画面
3. セッション管理
4. ログアウト機能

### Phase 2: タスク管理基礎（5日間）
1. タスクCRUD操作
2. タスク一覧表示
3. タスク完了チェック
4. カテゴリ・優先度管理

### Phase 3: ダッシュボード（3日間）
1. Home.py完成
2. 今日のタスク表示
3. 達成率計算・表示

### Phase 4: テスト・調整（3日間）
1. 統合テスト
2. バグ修正
3. UI調整

---

## 🎨 設計仕様詳細

### 1. 認証機能

#### 1.1 サインアップ仕様
**入力項目**:
- 表示名（display_name）: 必須、1-100文字
- メールアドレス（email）: 必須、メール形式検証
- パスワード（password）: 必須、8文字以上
- パスワード確認（password_confirm）: 必須、passwordと一致

**バリデーション**:
```python
# パスワード検証
if len(password) < 8:
    return "パスワードは8文字以上にしてください"

# パスワード一致確認
if password != password_confirm:
    return "パスワードが一致しません"

# メール形式チェック（Supabaseが自動実行）
```

**処理フロー**:
1. Supabase Auth でユーザー作成
2. 成功時、user_profilesテーブルにレコード作成
   ```sql
   INSERT INTO user_profiles (id, display_name)
   VALUES (auth_user_id, display_name)
   ```
3. セッション状態に保存
4. ダッシュボードへリダイレクト

**エラーメッセージ**:
- 既存ユーザー: "このメールアドレスは既に登録されています"
- その他のエラー: "登録に失敗しました。再度お試しください"

#### 1.2 ログイン仕様
**入力項目**:
- メールアドレス: 必須
- パスワード: 必須

**エラーメッセージ**:
- 認証失敗: "メールまたはパスワードが正しくありません"（セキュリティ重視）
- その他: "ログインに失敗しました。再度お試しください"

**処理フロー**:
1. Supabase Auth でログイン
2. セッション状態に保存
   ```python
   st.session_state['user'] = {
       'id': user.id,
       'email': user.email,
       'display_name': profile.display_name
   }
   st.session_state['authenticated'] = True
   ```
3. ダッシュボードへリダイレクト

#### 1.3 セッション管理
**セッション状態の構造**:
```python
st.session_state = {
    'user': {
        'id': UUID,
        'email': str,
        'display_name': str
    },
    'authenticated': bool,
    'supabase_session': dict  # Supabaseセッション情報
}
```

**セッション維持**:
- Streamlitのセッション機能を使用
- ページ遷移時も維持
- ブラウザ閉じると消失（Sprint 1仕様）

**認証ガード**:
すべてのページで以下のチェックを実行:
```python
if not is_authenticated():
    st.warning("ログインが必要です")
    st.switch_page("pages/0_🔐_Auth.py")
    st.stop()
```

#### 1.4 ログアウト
- セッション状態をクリア
- Supabase Auth からサインアウト
- ログイン画面へリダイレクト

---

### 2. タスク管理機能

#### 2.1 タスクデータ構造
```python
Task = {
    'id': UUID,
    'user_id': UUID,
    'title': str,           # 必須、200文字まで
    'description': str,     # 任意、テキスト
    'category': str,        # 必須、固定5種類
    'priority': str,        # 必須、'high'/'medium'/'low'
    'is_completed': bool,   # デフォルト False
    'task_date': date,      # 必須、デフォルトは今日
    'completed_at': datetime | None,
    'display_order': int,   # 並び順
    'created_at': datetime,
    'updated_at': datetime
}
```

#### 2.2 カテゴリ定義（固定）
```python
TASK_CATEGORIES = [
    "運動",
    "学習",
    "健康管理",
    "自己研鑽",
    "その他"
]
```

#### 2.3 優先度定義
```python
TASK_PRIORITIES = {
    "高": "high",
    "中": "medium",
    "低": "low"
}

# 表示色
PRIORITY_COLORS = {
    "high": "#FFE5E5",    # 薄い赤
    "medium": "#FFF4E5",  # 薄いオレンジ
    "low": "#E5F2FF"      # 薄い青
}
```

#### 2.4 タスク追加フォーム
**配置**: ページ上部、折りたたみ式expander

**入力項目**:
- タイトル*: text_input, 必須
- 説明: text_area, 任意
- カテゴリ*: selectbox, TASK_CATEGORIESから選択
- 優先度*: selectbox, デフォルト「中」

**バリデーション**:
```python
if not title.strip():
    st.error("タスク名を入力してください")
    return

if len(title) > 200:
    st.error("タスク名は200文字以内にしてください")
    return
```

**追加時の動作**:
1. データベースにINSERT
2. display_orderは既存タスクの最大値+1
3. 成功メッセージ表示
4. ページリロード（st.rerun()）

#### 2.5 タスク一覧表示

**表示順序**（Sprint 1）:
1. 優先度（高 → 中 → 低）
2. 作成日時（新しい順）

※ドラグ&ドロップによる手動並び替えはSprint 2で実装

**フィルタ機能**（Sprint 1では簡易版）:
- 完了/未完了の切り替えボタン
- カテゴリフィルタはSprint 2で実装

**タスクカード表示内容**:
```
┌─────────────────────────────────────────┐
│ [ ] タスクタイトル                      │
│     説明文（あれば）                     │
│     🏷️ カテゴリ | 優先度: 高           │
│                         [編集] [削除]    │
└─────────────────────────────────────────┘
```

**インタラクション**:
- チェックボックス: タスク完了切り替え
- 編集ボタン: インライン編集モード切替
- 削除ボタン: 確認ダイアログ表示後削除

#### 2.6 タスク編集（インライン）
**編集モード**:
- 編集ボタンクリックでフォーム表示
- タイトル、説明、カテゴリ、優先度を編集可能
- 保存/キャンセルボタン

**実装方針**:
```python
if st.session_state.get(f'editing_{task_id}'):
    # 編集フォーム表示
    with st.form(f'edit_form_{task_id}'):
        new_title = st.text_input("タイトル", value=task['title'])
        # ...
        if st.form_submit_button("保存"):
            update_task(task_id, {...})
            del st.session_state[f'editing_{task_id}']
            st.rerun()
else:
    # 通常表示
    if st.button("編集", key=f'edit_btn_{task_id}'):
        st.session_state[f'editing_{task_id}'] = True
        st.rerun()
```

#### 2.7 タスク削除
**確認ダイアログ**:
- st.dialog または確認ボタン2回押し方式
- 「本当に削除しますか？」メッセージ

**削除方式**: 物理削除（データベースから完全削除）
- 復元機能なし（シンプル重視）

#### 2.8 タスク完了チェック
**動作**:
1. チェックボックスクリック
2. is_completedをトグル
3. completed_atにタイムスタンプ記録（完了時）またはNULL（未完了に戻す）
4. 達成率を再計算

**UI表現**:
- 完了タスク: グレー表示、タイトルに取り消し線
- 未完了タスク: 通常表示

---

### 3. ダッシュボード

#### 3.1 レイアウト構成
```python
# ヘッダー
col1, col2 = st.columns([5, 1])
with col1:
    st.title("🧘 モンクモード")
    st.caption("2026年2月10日（月）")
with col2:
    st.button("ログアウト")

st.divider()

# メインコンテンツ（3カラム）
col_left, col_center, col_right = st.columns([2, 5, 2])

with col_left:
    # モンクモード進捗（Sprint 1では簡易版）
    st.metric("継続日数", "1日目")

with col_center:
    # 今日のタスク（最大5件）
    # 達成率

with col_right:
    # クイックアクション
```

#### 3.2 今日のタスク表示
**表示ルール**:
- 今日の日付（task_date = 今日）のタスクのみ
- 未完了の高優先度から順に5件まで
- 5件を超える場合: 「他 X 件のタスク」表示

**表示内容**（簡易版）:
```
[ ] タスクタイトル
[ ] タスクタイトル
[x] タスクタイトル（完了済み・グレー）
...

他 3 件のタスク

[📋 タスク管理へ] ボタン
```

**チェックボックス**:
- 表示のみ（disabled=True）
- クリックしても動作しない
- タスク管理ページで操作する設計

#### 3.3 達成率表示
**計算式**:
```python
completion_rate = 完了タスク数 / 総タスク数
```

**UI表現**:
```python
st.progress(completion_rate, text=f"達成率: {int(completion_rate * 100)}%")
```

**色の変化**:
- Streamlitデフォルトのプログレスバー色を使用
- カスタムカラーはSprint 2以降

#### 3.4 空状態（タスクがない時）
**表示内容**:
```python
st.info("📝 今日のタスクはまだありません")
st.button("➕ 最初のタスクを追加", use_container_width=True)
# ボタンクリックでタスク管理ページへ遷移
```

#### 3.5 クイックアクション
**Sprint 1で実装するボタン**:
- 「➕ タスク追加」→ タスク管理ページへ
- （タイマーや習慣記録は後のスプリントで追加）

---

## 🎨 UI/UX詳細仕様

### 1. デザイン原則
- **ミニマル**: 装飾を最小限に
- **直感的**: 説明なしで操作できる
- **集中重視**: 気が散る要素を排除

### 2. カラーパレット
```python
# utils/constants.py
COLORS = {
    'primary': '#2C3E50',      # メインテキスト
    'secondary': '#7F8C8D',    # サブテキスト
    'success': '#27AE60',      # 成功・完了
    'warning': '#F39C12',      # 警告
    'danger': '#E74C3C',       # エラー・削除
    'background': '#F8F9FA',   # 背景
    'card': '#FFFFFF',         # カード背景
    'border': '#E0E0E0',       # ボーダー
}
```

### 3. タイポグラフィ
- **タイトル**: 24-28px, bold
- **見出し**: 18-20px, semi-bold
- **本文**: 14-16px, regular
- **キャプション**: 12-14px, light

### 4. スペーシング
- **パディング**: 0.5rem, 1rem, 1.5rem, 2rem
- **マージン**: 同上
- **ボタン高さ**: 38-44px
- **カード間隔**: 0.5rem

### 5. フィードバック
**成功時**:
```python
st.success("✓ タスクを追加しました")
```

**エラー時**:
```python
st.error("⚠️ タスク名を入力してください")
```

**情報表示**:
```python
st.info("📝 今日のタスクはまだありません")
```

### 6. レスポンシブ対応（Sprint 1）
**方針**: 最低限の対応
- PC（デスクトップ）: フル機能
- タブレット（768px-1024px）: PC版と同じ
- スマートフォン（<768px）: 
  - カラムレイアウトは自動的に縦積み
  - フォントサイズはそのまま
  - 本格的な最適化はSprint 3で実施

---

## 🗄️ データベース操作仕様

### 1. 認証関連

#### ユーザー登録時
```python
# 1. Supabase Authでユーザー作成
response = supabase.auth.sign_up({
    "email": email,
    "password": password
})

# 2. user_profilesにレコード作成
supabase.table('user_profiles').insert({
    "id": response.user.id,
    "display_name": display_name,
    "created_at": "now()",
    "updated_at": "now()"
}).execute()
```

#### ログイン
```python
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
```

### 2. タスク関連

#### タスク取得（今日の日付）
```python
tasks = supabase.table('daily_tasks')\
    .select('*')\
    .eq('user_id', user_id)\
    .eq('task_date', today_str)\
    .order('priority', desc=True)\  # 高優先度が先
    .order('created_at', desc=False)\  # 古い順
    .execute()
```

#### タスク作成
```python
# display_orderは既存の最大値+1
max_order = supabase.table('daily_tasks')\
    .select('display_order')\
    .eq('user_id', user_id)\
    .eq('task_date', today_str)\
    .order('display_order', desc=True)\
    .limit(1)\
    .execute()

new_order = (max_order.data[0]['display_order'] + 1) if max_order.data else 0

supabase.table('daily_tasks').insert({
    "user_id": user_id,
    "title": title,
    "description": description,
    "category": category,
    "priority": priority,
    "task_date": today_str,
    "display_order": new_order
}).execute()
```

#### タスク更新
```python
supabase.table('daily_tasks')\
    .update({
        "title": new_title,
        "description": new_description,
        "category": new_category,
        "priority": new_priority,
        "updated_at": "now()"
    })\
    .eq('id', task_id)\
    .execute()
```

#### タスク完了切り替え
```python
# 完了状態を取得
task = get_task_by_id(task_id)

# トグル
new_status = not task['is_completed']
completed_at = "now()" if new_status else None

supabase.table('daily_tasks')\
    .update({
        "is_completed": new_status,
        "completed_at": completed_at,
        "updated_at": "now()"
    })\
    .eq('id', task_id)\
    .execute()
```

#### タスク削除（物理削除）
```python
supabase.table('daily_tasks')\
    .delete()\
    .eq('id', task_id)\
    .execute()
```

#### 達成率計算
```python
tasks = get_tasks_by_date(user_id, today_str)
total = len(tasks)
completed = len([t for t in tasks if t['is_completed']])

completion_rate = completed / total if total > 0 else 0
```

---

## 🔒 セキュリティ考慮事項

### 1. 認証
- パスワードは平文保存しない（Supabase Authが自動処理）
- セッショントークンは環境変数から取得
- RLSポリシーでユーザー間のデータ分離

### 2. 入力検証
**必須項目**:
- すべての必須フィールドの空チェック
- 文字数制限のチェック

**サニタイゼーション**:
- Supabase SDKが自動的にSQLインジェクション対策
- ユーザー入力のHTMLエスケープ（Streamlitが自動処理）

### 3. エラーハンドリング
**原則**: ユーザーに詳細なエラー情報を見せない
```python
try:
    # データベース操作
except Exception as e:
    print(f"Error: {e}")  # サーバーログに記録
    st.error("処理に失敗しました。再度お試しください")  # ユーザーには簡潔に
```

---

## 📱 レスポンシブ設計（Sprint 1）

### デバイス対応
- **デスクトップ（>1024px）**: フル機能、3カラムレイアウト
- **タブレット（768-1024px）**: フル機能、3カラム維持
- **スマートフォン（<768px）**: 
  - カラムは自動的に縦積み
  - ボタンは use_container_width=True で横幅いっぱいに
  - 本格的な調整はSprint 3で実施

### Streamlitのレスポンシブ機能
```python
# カラムは自動的にレスポンシブ
col1, col2, col3 = st.columns([2, 5, 2])

# モバイルでは自動的に縦積みになる
```

---

## 🧪 テスト仕様

### 1. 機能テスト項目

#### 認証
- [ ] 新規ユーザー登録（正常系）
- [ ] 既存メールで登録（エラー表示）
- [ ] パスワード8文字未満（エラー表示）
- [ ] パスワード不一致（エラー表示）
- [ ] ログイン（正常系）
- [ ] 間違ったパスワードでログイン（エラー表示）
- [ ] 未登録メールでログイン（エラー表示）
- [ ] ログアウト（正常系）
- [ ] 未認証でページアクセス（リダイレクト）

#### タスク管理
- [ ] タスク追加（全項目入力）
- [ ] タスク追加（最小限の入力：タイトルのみ）
- [ ] タイトル空でタスク追加（エラー表示）
- [ ] タスク完了チェック
- [ ] タスク未完了に戻す
- [ ] タスク編集（インライン）
- [ ] タスク削除（確認あり）
- [ ] 同じ日に複数タスク追加
- [ ] カテゴリフィルタ（Sprint 2）
- [ ] 優先度による自動ソート確認

#### ダッシュボード
- [ ] タスク0件時の表示
- [ ] タスク1-5件時の表示
- [ ] タスク6件以上時の表示（「他X件」表示確認）
- [ ] 達成率0%の表示
- [ ] 達成率50%の表示
- [ ] 達成率100%の表示
- [ ] クイックアクションボタン動作

### 2. UI/UXテスト
- [ ] エラーメッセージが赤色で表示
- [ ] 成功メッセージが緑色で表示
- [ ] ボタンがクリック可能
- [ ] フォーム送信後のリロード
- [ ] ページ遷移がスムーズ

### 3. データ整合性テスト
- [ ] タスク追加後、データベースに保存確認
- [ ] タスク削除後、データベースから削除確認
- [ ] ユーザーAのタスクがユーザーBに見えない（RLS確認）
- [ ] タイムゾーン: 今日の日付が正しく判定される

---

## 📊 完了基準（Definition of Done）

Sprint 1は以下がすべて満たされた時点で完了とする:

### 機能面
- ✅ ユーザー登録・ログイン・ログアウトが正常動作
- ✅ タスクの追加・編集・削除・完了チェックが正常動作
- ✅ ダッシュボードに今日のタスクと達成率が表示される
- ✅ エラーハンドリングが適切（エラー時にクラッシュしない）

### 技術面
- ✅ Supabaseとの連携が安定
- ✅ セッション管理が正常
- ✅ RLSポリシーが機能している
- ✅ コードが整理されている（適切な関数分割）

### ドキュメント
- ✅ コードにdocstringが記載されている
- ✅ README.mdにセットアップ手順が記載されている

### デモ可能な状態
「新規ユーザーを登録 → ログイン → タスクを3件追加 → 1件完了 → ダッシュボードで達成率33%を確認 → ログアウト」
という一連の流れが問題なく動作すること。

---

## 🚀 次のスプリントへの引き継ぎ事項

Sprint 1完了後、Sprint 2で以下を実装予定:
1. タスクの手動並び替え（ドラグ&ドロップ）
2. カテゴリフィルタ
3. ポモドーロタイマー
4. タスク連携タイマー

Sprint 1で技術的負債として残る可能性のある項目:
- レスポンシブデザインの完全対応
- パフォーマンス最適化
- リアルタイム同期（複数デバイス）

これらはSprint 2以降で順次対応する。

---

## 📝 補足事項

### 開発時の注意点
1. **こまめなコミット**: 各Phase完了時に必ずコミット
2. **動作確認**: 各関数実装後、必ずテスト実行
3. **エラーログ**: print文で必ずログ出力
4. **バックアップ**: 大きな変更前にブランチを切ることを検討

### 実装の優先順位
Phase 1 > Phase 2 > Phase 3 の順で実装。
Phase 4（テスト）は並行して実施。

各Phaseで動作する状態を維持すること。

---

以上、Sprint 1詳細設計書
