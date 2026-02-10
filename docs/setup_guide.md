# モンクモード支援システム - 環境構築手順書

## 前提条件
- Windows PC
- VS Code インストール済み
- Git インストール済み
- Python 3.9以上 インストール済み
- GitHubアカウント作成済み

---

## 1. Supabaseプロジェクト作成

### 1.1 アカウント作成とプロジェクト初期化

1. **Supabaseにアクセス**: https://supabase.com/
2. **Sign Up** でアカウント作成（GitHubアカウントで連携可）
3. **New Project** をクリック
4. プロジェクト情報入力:
   - **Name**: `monk-mode-system`
   - **Database Password**: 強力なパスワードを設定（保存しておく）
   - **Region**: `Northeast Asia (Tokyo)` または最寄りのリージョン
   - **Pricing Plan**: Free（開発用）
5. **Create new project** をクリック（数分待つ）

### 1.2 データベースセットアップ

1. 左サイドバーから **SQL Editor** を選択
2. **New Query** をクリック
3. `database_design.md` のSQLスクリプトをコピー＆ペースト
4. **Run** をクリックして実行
5. エラーがないことを確認

**実行順序**:
```sql
-- 1. テーブル作成（user_profiles から順番に）
-- 2. インデックス作成
-- 3. RLSポリシー設定
```

### 1.3 認証設定

1. 左サイドバーから **Authentication** → **Providers** を選択
2. **Email** を有効化（デフォルトで有効）
3. **Settings** タブで以下を確認:
   - Enable email confirmations: OFF（開発中は無効推奨）
   - Enable email signups: ON

### 1.4 APIキー取得

1. 左サイドバーから **Settings** → **API** を選択
2. 以下をコピーして保存:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **anon public key**: `eyJhbG...`（非常に長い文字列）

⚠️ **重要**: これらの情報は後で使用するので、安全な場所に保存してください。

---

## 2. ローカル開発環境構築

### 2.1 プロジェクトフォルダ作成

```bash
# Windows PowerShell または Git Bash で実行

# プロジェクトフォルダ作成
mkdir monk-mode-app
cd monk-mode-app

# Gitリポジトリ初期化
git init
```

### 2.2 Python仮想環境構築

```bash
# 仮想環境作成
python -m venv venv

# 仮想環境アクティベート（PowerShell）
.\venv\Scripts\Activate.ps1

# 仮想環境アクティベート（Git Bash）
source venv/Scripts/activate
```

### 2.3 必要なパッケージインストール

`requirements.txt` を作成:

```txt
streamlit==1.31.0
supabase==2.3.4
python-dotenv==1.0.0
pandas==2.1.4
plotly==5.18.0
altair==5.2.0
Pillow==10.2.0
```

パッケージインストール:
```bash
pip install -r requirements.txt
```

### 2.4 環境変数設定

`.env` ファイルを作成:

```env
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbG...あなたのanon public key
```

⚠️ **セキュリティ注意**:
- `.env` ファイルは **絶対に** GitHubにコミットしない
- `.gitignore` に必ず追加

`.gitignore` ファイルを作成:
```
# 仮想環境
venv/
__pycache__/
*.pyc

# 環境変数
.env

# Streamlitキャッシュ
.streamlit/

# その他
*.log
.DS_Store
```

### 2.5 `.env.example` 作成

他の開発者用のテンプレート:
```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_anon_key_here
```

---

## 3. プロジェクト構造作成

```bash
# フォルダ構造作成
mkdir pages components utils assets
mkdir assets/sounds

# 初期ファイル作成
touch Home.py
touch pages/__init__.py
touch components/__init__.py
touch utils/__init__.py
touch README.md
```

---

## 4. Supabase接続テスト

`utils/supabase_client.py` を作成:

```python
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# 環境変数読み込み
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Supabaseクライアント初期化
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def test_connection():
    """接続テスト"""
    try:
        # テーブル存在確認
        response = supabase.table('user_profiles').select("*").limit(1).execute()
        print("✅ Supabase接続成功！")
        return True
    except Exception as e:
        print(f"❌ Supabase接続エラー: {e}")
        return False

if __name__ == "__main__":
    test_connection()
```

テスト実行:
```bash
python utils/supabase_client.py
```

成功したら `✅ Supabase接続成功！` と表示される。

---

## 5. Streamlit基本設定

### 5.1 `.streamlit/config.toml` 作成

```bash
mkdir .streamlit
```

`.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#27AE60"
backgroundColor = "#F8F9FA"
secondaryBackgroundColor = "#FFFFFF"
textColor = "#2C3E50"
font = "sans serif"

[server]
headless = true
port = 8501
```

### 5.2 最小限の `Home.py` 作成

```python
import streamlit as st
from utils.supabase_client import supabase

st.set_page_config(
    page_title="モンクモード支援システム",
    page_icon="🧘",
    layout="wide"
)

st.title("🧘 モンクモード支援システム")
st.write("自己改善の旅へようこそ")

# 接続テスト
if st.button("Supabase接続テスト"):
    try:
        response = supabase.table('user_profiles').select("*").limit(1).execute()
        st.success("✅ データベース接続成功！")
    except Exception as e:
        st.error(f"❌ 接続エラー: {e}")
```

### 5.3 動作確認

```bash
streamlit run Home.py
```

ブラウザで `http://localhost:8501` が開く。
「Supabase接続テスト」ボタンをクリックして成功メッセージを確認。

---

## 6. GitHubリポジトリ作成

### 6.1 GitHubで新規リポジトリ作成

1. https://github.com にアクセス
2. 右上の **+** → **New repository**
3. リポジトリ名: `monk-mode-app`
4. **Private** を選択（公開したくない場合）
5. **Create repository**

### 6.2 ローカルからプッシュ

```bash
# ファイルをステージング
git add .

# 初回コミット
git commit -m "Initial commit: Project setup"

# リモートリポジトリ追加（GitHubで表示されるURLを使用）
git remote add origin https://github.com/YOUR_USERNAME/monk-mode-app.git

# プッシュ
git branch -M main
git push -u origin main
```

---

## 7. Streamlit Cloudデプロイ準備

### 7.1 `requirements.txt` 確認

最終的な `requirements.txt`:
```txt
streamlit==1.31.0
supabase==2.3.4
python-dotenv==1.0.0
pandas==2.1.4
plotly==5.18.0
altair==5.2.0
Pillow==10.2.0
```

### 7.2 `.streamlit/secrets.toml` 作成（Streamlit Cloud用）

ローカルには作成せず、後でStreamlit Cloudの管理画面で設定。

内容（参考）:
```toml
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "eyJhbG..."
```

### 7.3 Streamlit Cloudアカウント作成

1. https://streamlit.io/cloud にアクセス
2. **Sign up** → GitHubアカウントで連携
3. GitHubリポジトリへのアクセス許可

**デプロイは後のスプリントで実施**

---

## 8. VS Code拡張機能推奨

以下の拡張機能をインストール:

- **Python** (Microsoft)
- **Pylance** (Microsoft)
- **GitLens** (Git履歴表示)
- **Better Comments** (コメント見やすく)
- **autoDocstring** (docstring自動生成)

---

## 9. 開発ワークフロー

### 日常の開発手順

```bash
# 1. 仮想環境アクティベート
.\venv\Scripts\Activate.ps1

# 2. Streamlitアプリ起動
streamlit run Home.py

# 3. ブラウザで http://localhost:8501 を開いて開発

# 4. 変更をコミット
git add .
git commit -m "機能追加: XXX"
git push
```

---

## 10. トラブルシューティング

### Q: Python仮想環境がアクティベートできない
**A**: PowerShellの実行ポリシーエラーの場合:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Q: Streamlitが起動しない
**A**: ポートが使用中の可能性:
```bash
streamlit run Home.py --server.port 8502
```

### Q: Supabase接続エラー
**A**: 
1. `.env` ファイルの内容確認
2. Supabase URLとKeyが正しいか確認
3. ファイアウォール設定確認

### Q: モジュールが見つからない
**A**: 
```bash
pip install -r requirements.txt --upgrade
```

---

## 完了チェックリスト

- [ ] Supabaseプロジェクト作成完了
- [ ] データベーステーブル作成完了
- [ ] ローカル開発環境構築完了
- [ ] Python仮想環境作成完了
- [ ] 必要なパッケージインストール完了
- [ ] `.env` ファイル作成・設定完了
- [ ] `.gitignore` 設定完了
- [ ] Supabase接続テスト成功
- [ ] Streamlit起動確認完了
- [ ] GitHubリポジトリ作成・プッシュ完了

---

## 次のステップ

Sprint 1の実装に進みます。
Claude Codeへの実装プロンプトを準備します。
