# Git運用ガイド - Claude Code & 開発者協働版

## 📋 概要

このプロジェクトでは、**スプリント単位**でブランチを管理するシンプルなワークフローを採用します。
Claude Codeの制約（`claude/` プレフィックス配下のブランチのみ操作可能）を考慮しています。

---

## 🎯 基本方針

### シンプルなルール

1. **1スプリント = 1ブランチ**
2. Claude Codeがそのブランチに継続的にプッシュ
3. あなたがローカルで確認→OK なら次の実装を依頼
4. スプリント完了後、あなたがPR作成→マージ

### 役割分担

**Claude Code（AI）の役割：**
- スプリント開始時にブランチ作成
- 実装・コミット・プッシュ（繰り返し）
- あなたの確認を待つ

**あなた（開発者）の役割：**
- 実装指示（初回 & 継続）
- ローカルで動作確認
- 問題あれば修正依頼、OKなら次の実装を依頼
- スプリント完了後にPR作成・マージ

---

## 🌳 ブランチ構造

```
main (保護ブランチ)
├── claude/sprint-1          ← Sprint 1全体
├── claude/sprint-2          ← Sprint 2全体
├── claude/sprint-3          ← Sprint 3全体
├── claude/sprint-4          ← Sprint 4全体
├── claude/sprint-5          ← Sprint 5全体
├── claude/sprint-6          ← Sprint 6全体
└── claude/bugfix-XXXX       ← 緊急バグ修正のみ別ブランチ
```

### ブランチ命名規則

```bash
# スプリント実装（基本はこれだけ）
claude/sprint-<番号>
例: claude/sprint-1
    claude/sprint-2
    claude/sprint-3

# 緊急バグ修正（本番で致命的なバグが出た場合のみ）
claude/bugfix-<簡潔な説明>
例: claude/bugfix-login-error
    claude/bugfix-data-loss
```

---

## 🔄 標準ワークフロー（Sprint 1の例）

### 全体の流れ

```
1. Sprint開始 → Claude Codeがブランチ作成・初回実装・プッシュ
2. あなたが確認 → OK? → 次の実装を依頼 → Claude Codeがプッシュ
3. 2を繰り返す
4. Sprint完了 → あなたがPR作成・マージ
```

---

### ステップ1: Sprint開始

#### あなた → Claude Codeへの指示

```
Sprint 1を開始します。

手順:
1. claude/sprint-1 ブランチを作成してください
2. sprint_1_prompts.md のPhase 1から実装を開始してください
3. Phase 1の各プロンプトを実装し、適宜コミット・プッシュしてください
4. Phase 1が完了したら報告してください

重要:
- coding_standards.md と quick_reference.md に厳密に従ってください
- 各実装後は必ずコミット・プッシュしてください
```

#### Claude Codeの作業

```bash
# ブランチ作成
git checkout -b claude/sprint-1
git push -u origin claude/sprint-1

# Phase 1 実装開始
# プロンプト 1-1: 認証コンポーネント
# ... 実装 ...
git add components/auth.py
git commit -m "feat: 認証コンポーネントを実装"
git push origin claude/sprint-1

# プロンプト 1-2: ログイン画面
# ... 実装 ...
git add pages/0_🔐_Auth.py
git commit -m "feat: ログイン画面を実装"
git push origin claude/sprint-1

# プロンプト 1-3: 認証ガード
# ... 実装 ...
git add Home.py
git commit -m "feat: Home.pyに認証ガードを追加"
git push origin claude/sprint-1

# 報告
echo "Phase 1実装完了。claude/sprint-1 ブランチを確認してください。"
```

---

### ステップ2: あなたの確認（繰り返し）

#### ローカルで動作確認

```bash
# 最新を取得
git fetch origin
git checkout claude/sprint-1
git pull origin claude/sprint-1

# アプリ起動
streamlit run Home.py

# 動作テスト
# - ユーザー登録
# - ログイン
# - ログアウト
# - エラーケース確認
```

#### パターンA: 問題なし → 次の実装を依頼

```
Phase 1の実装を確認しました。問題ありません。

次の作業に進んでください:
- sprint_1_prompts.md のPhase 2（タスク管理機能）を実装
- 完了したら報告してください
```

#### パターンB: 修正が必要 → 修正依頼

```
Phase 1を確認しましたが、以下の修正が必要です:

1. components/auth.py 23行目
   - 型ヒントが不足: def login(email: str, password: str) -> bool:

2. pages/0_🔐_Auth.py 45行目
   - エラーメッセージをユーザーフレンドリーに変更
   - "Invalid credentials" → "メールアドレスまたはパスワードが正しくありません"

claude/sprint-1 ブランチで修正し、プッシュしてください。
修正完了後、報告してください。
```

#### Claude Codeが修正・プッシュ

```bash
# 修正作業
# ... 修正 ...
git add components/auth.py pages/0_🔐_Auth.py
git commit -m "fix: レビュー指摘事項を修正"
git push origin claude/sprint-1

# 報告
echo "修正完了。claude/sprint-1 を再確認してください。"
```

---

### ステップ3: 繰り返し（Phase 2, 3, 4...）

同じフローを繰り返す:

```
あなた: Phase 2を実装してください
  ↓
Claude Code: Phase 2実装・プッシュ・報告
  ↓
あなた: ローカルで確認
  ↓
  OK → Phase 3を依頼
  修正必要 → 修正依頼
  ↓
Claude Code: Phase 3実装・プッシュ・報告
  ↓
あなた: ローカルで確認
  ↓
  ... 繰り返し ...
```

**Phase 2実装依頼例:**
```
Phase 1の確認完了しました。問題ありません。

次の作業:
- sprint_1_prompts.md のPhase 2（タスク管理機能）を実装してください
- プロンプト 2-1, 2-2, 2-3 をすべて実装
- 完了したら報告してください
```

**Phase 3実装依頼例:**
```
Phase 2も問題ありません。

次の作業:
- sprint_1_prompts.md のPhase 3（ダッシュボード）を実装してください
- 完了したら報告してください
```

**Phase 4（テスト）実装依頼例:**
```
Phase 3も完了しました。

最終段階:
- sprint_1_prompts.md のPhase 4（テスト・調整）を実施してください
- すべてのテストシナリオを確認
- 問題があれば修正
- 完了したら最終報告してください
```

---

### ステップ4: Sprint完了 → あなたがPR作成・マージ

#### Claude Codeの最終報告

```
Sprint 1のすべてのPhaseが完了しました。

実装内容:
- Phase 1: 認証機能（ログイン/サインアップ/セッション管理）
- Phase 2: タスク管理（CRUD操作/タスクカード）
- Phase 3: ダッシュボード（タスク一覧/完了率表示）
- Phase 4: テスト・調整（すべて合格）

claude/sprint-1 ブランチの最終確認をお願いします。
```

#### あなたの最終確認

```bash
# 最新を取得
git checkout claude/sprint-1
git pull origin claude/sprint-1

# 最終動作確認
streamlit run Home.py

# 全機能テスト
# - 認証フロー
# - タスク管理
# - ダッシュボード
# - エラーケース
```

#### GitHubでPR作成

1. GitHubのリポジトリページを開く
2. "Pull requests" → "New pull request"
3. 設定:
   - **base**: `main`
   - **compare**: `claude/sprint-1`
4. タイトル: `Sprint 1: 認証機能とタスク管理実装`
5. 説明:
   ```markdown
   ## Sprint 1 実装内容
   
   ### Phase 1: 認証機能
   - ログイン/サインアップ
   - セッション管理
   - 認証ガード
   
   ### Phase 2: タスク管理
   - タスクCRUD操作
   - タスクカードコンポーネント
   - カテゴリ・優先度管理
   
   ### Phase 3: ダッシュボード
   - 今日のタスク表示
   - 完了率計算・表示
   - ナビゲーション
   
   ### Phase 4: テスト
   - 全機能動作確認済み
   - エラーハンドリング確認済み
   
   ## 確認済み事項
   - [x] すべての機能が正常動作
   - [x] コーディング規約準拠
   - [x] セキュリティ対策実施
   - [x] エラーハンドリング適切
   ```
6. "Create pull request"

#### マージ

1. PR画面で最終確認
2. "Merge pull request" をクリック
3. コミットメッセージ（デフォルトでOK）:
   ```
   Sprint 1: 認証機能とタスク管理実装 (#1)
   ```
4. "Confirm merge"
5. "Delete branch" でブランチ削除

#### ローカルを更新

```bash
git checkout main
git pull origin main

# 次のSprintの準備完了
```

---

## 🔥 緊急バグ修正の場合

本番で致命的なバグが発見された場合のみ、別ブランチを作成します。

### あなた → Claude Codeへの指示

```
緊急バグ修正が必要です。

問題: [具体的な問題の説明]
ブランチ: claude/bugfix-[問題名]

以下を実施してください:
1. mainブランチから claude/bugfix-[問題名] を作成
2. 問題を修正
3. 動作確認
4. プッシュして報告
```

### Claude Codeの作業

```bash
# mainから新ブランチ作成
git checkout main
git pull origin main
git checkout -b claude/bugfix-login-error
git push -u origin claude/bugfix-login-error

# 修正
# ... 修正作業 ...
git add [修正したファイル]
git commit -m "fix: ログインエラーを修正"
git push origin claude/bugfix-login-error

# 報告
echo "バグ修正完了。claude/bugfix-login-error を確認してください。"
```

### あなたが即座に確認・マージ

```bash
# 確認
git fetch origin
git checkout claude/bugfix-login-error
streamlit run Home.py
# テスト...

# 問題なければGitHub上でPR作成→即座にマージ
```

---

## ⚠️ トラブルシューティング

### Q1: ブランチ名を間違えた

**Claude Codeへの指示:**
```
ブランチ名が間違っています。正しく作り直してください:

git checkout main
git pull origin main
git branch -D sprint-1  # 間違ったブランチ削除
git checkout -b claude/sprint-1  # 正しいブランチ作成
git push -u origin claude/sprint-1

実装を続けてください。
```

---

### Q2: コミットメッセージが不適切だった

**次回からの指示:**
```
コミットメッセージは以下の形式で統一してください:

<プレフィックス>: <明確な説明>

プレフィックス:
- feat: 新機能
- fix: バグ修正
- docs: ドキュメント
- style: フォーマット
- refactor: リファクタリング
- test: テスト

例:
✅ git commit -m "feat: ログイン機能を実装"
✅ git commit -m "fix: タスク削除時のエラーを修正"
❌ git commit -m "update"
```

---

### Q3: 修正箇所が多すぎて混乱

**段階的に指示:**
```
一度に修正せず、1つずつ対応してください:

まず以下を修正:
1. components/auth.py の型ヒント追加

完了したらプッシュして報告してください。
次の修正を指示します。
```

---

### Q4: どのファイルを修正すべきか不明

**具体的に指示:**
```
以下のファイルを修正してください:
- ファイルパス: components/auth.py
- 行番号: 23行目
- 修正内容: [具体的な内容]

修正完了後、プッシュして報告してください。
```

---

## 📝 チェックリスト

### Sprint開始時（Claude Code）
- [ ] ブランチ名が `claude/sprint-<番号>` 形式
- [ ] mainブランチから最新を取得済み
- [ ] 実装する内容が明確

### 各プッシュ前（Claude Code）
- [ ] ローカルで動作確認済み
- [ ] コミットメッセージが明確（プレフィックス付き）
- [ ] エラーが出ていない

### 確認時（あなた）
- [ ] ローカルで動作確認
- [ ] コーディング規約確認
- [ ] 次の指示が明確

### Sprint完了時（あなた）
- [ ] 全機能の動作確認完了
- [ ] コードレビュー完了
- [ ] テスト完了
- [ ] PR作成・マージ準備OK

---

## 🎓 ベストプラクティス

### 1. 明確な指示を出す

```bash
# ✅ GOOD - 具体的
「claude/sprint-1 ブランチで、components/auth.py の23行目に型ヒントを追加してください」

# ❌ BAD - 曖昧
「修正してください」
```

### 2. 小まめに確認

```bash
# ✅ GOOD - Phase単位で確認
Phase 1完了 → 確認 → Phase 2指示 → 確認 → Phase 3指示

# ❌ BAD - まとめて確認
Sprint全部やって → 最後に確認（問題が大きくなる）
```

### 3. 問題は早期に修正

```bash
# ✅ GOOD - すぐ修正依頼
問題発見 → 即座に修正依頼 → 確認

# ❌ BAD - 溜め込む
問題を溜めて最後にまとめて修正依頼（混乱する）
```

---

## 📞 困ったときは

### Claude Codeが指示を理解しない

**より具体的に:**
```
❌ 「認証機能を実装してください」

✅ 「claude/sprint-1 ブランチで、
sprint_1_prompts.md のプロンプト1-1から順番に実装してください。
各プロンプト完了後にコミット・プッシュし、
Phase 1が完了したら報告してください」
```

### エラーが出て進まない

**エラー内容を共有:**
```
以下のエラーが発生しました:
[エラーメッセージ全文をコピー]

原因と解決方法を教えてください。
```

---

## 🎯 まとめ

### シンプルな3ステップ

1. **Claude Codeが実装・プッシュ**
2. **あなたが確認 → 次の指示 or 修正依頼**
3. **繰り返し → Sprint完了でマージ**

### 成功の鍵

- ✅ 1スプリント = 1ブランチでシンプルに
- ✅ Phase単位で確認・フィードバック
- ✅ 明確な指示で混乱を防ぐ
- ✅ 問題は早期発見・早期解決

**このワークフローで、効率的に高品質なコードを維持できます！** 🚀
