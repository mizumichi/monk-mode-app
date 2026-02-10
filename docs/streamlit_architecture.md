# モンクモード支援システム - Streamlitアプリケーション構成設計

## アプリケーション構造

```
monk-mode-app/
├── .streamlit/
│   └── config.toml           # Streamlit設定
├── pages/                    # マルチページアプリ
│   ├── 1_📋_Tasks.py         # タスク管理
│   ├── 2_⏱️_Timer.py         # タイマー
│   ├── 3_📊_Habits.py        # 習慣トラッカー
│   ├── 4_📝_Journal.py       # 日記
│   ├── 5_📈_Analytics.py     # 統計・分析
│   └── 6_⚙️_Settings.py      # 設定
├── components/               # 再利用可能コンポーネント
│   ├── __init__.py
│   ├── auth.py              # 認証関連
│   ├── task_card.py         # タスクカードUI
│   ├── habit_tracker.py     # 習慣トラッカーUI
│   ├── timer_widget.py      # タイマーウィジェット
│   ├── chart_widgets.py     # グラフ表示
│   └── calendar_view.py     # カレンダー表示
├── utils/                    # ユーティリティ
│   ├── __init__.py
│   ├── supabase_client.py   # Supabase接続
│   ├── database.py          # DB操作関数
│   ├── date_utils.py        # 日付処理
│   └── constants.py         # 定数定義
├── assets/                   # 静的ファイル
│   ├── styles.css           # カスタムCSS
│   └── sounds/              # 通知音
│       └── timer_done.mp3
├── .env.example             # 環境変数テンプレート
├── .gitignore
├── requirements.txt         # 依存パッケージ
├── README.md
└── Home.py                  # エントリーポイント（ダッシュボード）
```

---

## ページ構成詳細

### Home.py - ダッシュボード
**役割**: アプリのエントリーポイント、今日の概要表示

**表示内容**:
- ログイン状態の確認（未ログインなら認証画面）
- 今日の日付と曜日
- モンクモード残り日数カウントダウン
- 今日のタスク概要（完了率）
- 習慣トラッカーのサマリー
- クイックアクションボタン
  - 「タスク追加」
  - 「ポモドーロ開始」
  - 「習慣記録」

**レイアウト**:
```python
# 3カラムレイアウト
col1, col2, col3 = st.columns([2, 3, 2])
with col1:
    # モンクモード進捗
    # ストリーク表示
with col2:
    # 今日のタスク一覧
with col3:
    # 習慣チェックリスト
    # クイックタイマー
```

---

### 1_📋_Tasks.py - タスク管理
**役割**: デイリータスクの管理

**機能**:
- タスク一覧表示（カテゴリ別フィルタ）
- タスク追加フォーム
- タスク編集・削除
- 優先度変更
- 完了チェック
- 並び替え（優先度/カテゴリ）
- 未完了タスクの翌日繰越ボタン

**セクション**:
1. フィルタバー（カテゴリ、優先度、完了状態）
2. タスク追加フォーム
3. タスクリスト
   - 各タスクにタイマー起動ボタン
   - 編集/削除ボタン

**状態管理**:
- `st.session_state.tasks`: タスクリスト
- `st.session_state.editing_task_id`: 編集中タスクID

---

### 2_⏱️_Timer.py - タイマー
**役割**: ポモドーロタイマーとタスクタイマー

**機能**:
- ポモドーロタイマー
  - 作業時間/休憩時間設定
  - 開始/一時停止/リセット
  - 進捗バー表示
  - 完了時の音通知
- タスク選択してタイマー開始
- セッション履歴表示
- 今日の総作業時間

**レイアウト**:
```python
# タブ分割
tab1, tab2 = st.tabs(["ポモドーロ", "タスクタイマー"])
with tab1:
    # ポモドーロタイマーUI
with tab2:
    # タスク選択 + タイマー
```

**状態管理**:
- `st.session_state.timer_running`: タイマー稼働中フラグ
- `st.session_state.remaining_seconds`: 残り時間
- `st.session_state.session_type`: 'work' / 'break'

**技術的注意点**:
- Streamlitはリアルタイム更新が弱いため、`st.rerun()`を活用
- タイマーは`time.sleep()`ではなく、セッション状態に開始時刻を保存し、現在時刻との差分で計算

---

### 3_📊_Habits.py - 習慣トラッカー
**役割**: 日々の習慣記録と継続状況の可視化

**機能**:
- 今日の習慣チェックリスト
  - 睡眠時間入力
  - 各習慣のチェックボックス
  - 水分摂取量入力
  - スクリーンタイム入力
- 禁止事項達成チェック
- 気分評価（1-5）
- 連続達成日数（ストリーク）表示
- 週間/月間ヒートマップ
- カレンダービュー（過去の記録確認）

**レイアウト**:
```python
# 上部: 今日の記録入力
st.subheader("今日の習慣")
# チェックリストフォーム

# 中部: ストリーク表示
st.metric("連続達成日数", "🔥 15日")

# 下部: 可視化
tab1, tab2 = st.tabs(["ヒートマップ", "カレンダー"])
```

---

### 4_📝_Journal.py - 日記
**役割**: デイリージャーナリングと過去の振り返り

**機能**:
- 日付選択
- 振り返りプロンプト付き入力フォーム
  - 今日達成できたこと
  - 改善すべき点
  - 気づきや学び
  - 明日の最優先事項
  - 感謝すること3つ
- フリーテキスト日記
- 気分評価
- 自動保存（下書き）
- 過去の日記検索・閲覧
- 日記エクスポート（テキスト/PDF）

**レイアウト**:
```python
# サイドバー: 日付選択、過去の日記一覧
with st.sidebar:
    selected_date = st.date_input("日付")
    # 過去の日記リスト

# メイン: 日記入力・表示
if editing_mode:
    # 入力フォーム
else:
    # 日記表示（読み取り専用）
```

---

### 5_📈_Analytics.py - 統計・分析
**役割**: データの可視化と分析

**機能**:
- ダッシュボード概要
  - 総日数
  - 最長ストリーク
  - 平均タスク完了率
  - 総作業時間
- グラフ表示
  - 習慣達成率の推移（折れ線グラフ）
  - カテゴリ別タスク分布（円グラフ）
  - 週間作業時間（棒グラフ）
  - ヒートマップ（習慣継続状況）
- 期間選択（週/月/全期間）
- データエクスポート（CSV/JSON）

**使用ライブラリ**:
- Plotly（インタラクティブグラフ）
- Altair（宣言的グラフ）

---

### 6_⚙️_Settings.py - 設定
**役割**: ユーザー設定とアカウント管理

**機能**:
- プロフィール編集
  - 表示名
  - モンクモード期間設定
  - 目標起床時刻/就寝時刻
- 通知設定
  - 各種リマインダーON/OFF
  - 通知時刻設定
- テーマ設定（ライト/ダーク）
- データ管理
  - データエクスポート
  - アカウント削除
- パスワード変更
- ログアウト

---

## 状態管理戦略

### セッション状態の構造
```python
# st.session_state の主要キー
{
    # 認証
    'user': {id, email, ...},
    'authenticated': bool,
    
    # データキャッシュ
    'tasks': [],
    'habits': {},
    'routines': [],
    
    # UI状態
    'current_page': str,
    'editing_task_id': str | None,
    'selected_date': date,
    
    # タイマー
    'timer_running': bool,
    'timer_start_time': datetime,
    'timer_duration': int,
    'timer_session_type': str,
}
```

### データフェッチング戦略
1. **ページ読み込み時**: 必要なデータのみフェッチ
2. **キャッシング**: `@st.cache_data` でAPI呼び出し削減
3. **リアルタイム同期**: 更新時は即座にSupabaseへ保存

---

## デザインガイドライン

### カラーパレット
```python
# constants.py で定義
COLORS = {
    'primary': '#2C3E50',      # ダークブルーグレー
    'secondary': '#34495E',    # グレー
    'accent': '#27AE60',       # グリーン（達成）
    'warning': '#E67E22',      # オレンジ
    'danger': '#E74C3C',       # レッド
    'background': '#ECF0F1',   # ライトグレー
    'text': '#2C3E50',
}
```

### カスタムCSS（assets/styles.css）
```css
/* シンプル、ミニマルなデザイン */
.stApp {
    background-color: #F8F9FA;
}

/* タスクカード */
.task-card {
    background: white;
    border-radius: 8px;
    padding: 16px;
    margin: 8px 0;
    border-left: 4px solid #27AE60;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* ストリーク表示 */
.streak-badge {
    font-size: 2em;
    color: #E67E22;
}
```

---

## パフォーマンス最適化

1. **遅延ロード**: 大きなデータは必要な時だけフェッチ
2. **ページネーション**: タスク一覧、日記一覧など
3. **キャッシュ戦略**: 
   - ユーザープロフィール: セッション全体でキャッシュ
   - タスク: ページごとにキャッシュ
   - 統計データ: 時間指定でキャッシュ（5分など）

---

## エラーハンドリング

```python
# 統一的なエラー表示
def show_error(message):
    st.error(f"⚠️ {message}")

# ネットワークエラー対応
try:
    data = fetch_data()
except Exception as e:
    show_error("データの取得に失敗しました。再度お試しください。")
    st.stop()
```

---

## セキュリティ考慮事項

1. **環境変数**: Supabase URLとKeyは`.env`で管理
2. **RLS**: データベースレベルで権限制御
3. **セッション**: Streamlit Cloudのセッション管理を使用
4. **入力検証**: ユーザー入力は必ずバリデーション

---

## 次のステップ

この構成をもとに、各コンポーネントの詳細実装プロンプトを作成します。
