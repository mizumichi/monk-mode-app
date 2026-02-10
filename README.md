# モンクモード支援システム

モンクモードの実践を支援し、自己改善の習慣化を促進するWebアプリケーション

## 概要

モンクモードとは、外部の刺激を断ち、自己改善や目標達成に特化するためのライフスタイルです。
本システムは、規則正しい生活習慣・運動・学習・瞑想などの継続をサポートします。

## 技術スタック

- **フロントエンド**: Streamlit 1.31.0
- **バックエンド/DB**: Supabase (PostgreSQL)
- **認証**: Supabase Auth
- **言語**: Python 3.9+
- **データ可視化**: Plotly, Altair
- **デプロイ**: Streamlit Cloud

## セットアップ

詳細な手順は `docs/setup_guide.md` を参照してください。

### クイックスタート

```bash
# 1. リポジトリのクローン
git clone <repository-url>
cd monk-mode-app

# 2. 仮想環境の作成・有効化
python -m venv venv
source venv/bin/activate  # Windowsの場合: venv\Scripts\activate

# 3. パッケージのインストール
pip install -r requirements.txt

# 4. 環境変数の設定（.env.exampleをコピーして編集）
cp .env.example .env
# .env を編集してSupabaseのURLとKeyを設定

# 5. Supabaseでデータベースをセットアップ
# docs/database_design.md のSQLをSupabase SQL Editorで実行

# 6. アプリの起動
streamlit run Home.py
```

## プロジェクト構造

```
monk-mode-app/
├── Home.py                  # エントリーポイント（ダッシュボード）
├── pages/                   # マルチページアプリ
├── components/              # 再利用可能UIコンポーネント
├── utils/                   # ユーティリティ
│   └── supabase_client.py   # Supabase接続
├── assets/                  # 静的ファイル
│   ├── styles.css           # カスタムCSS
│   └── sounds/              # 通知音
├── docs/                    # 設計ドキュメント
├── .streamlit/config.toml   # Streamlit設定
├── .env.example             # 環境変数テンプレート
└── requirements.txt         # 依存パッケージ
```

## 開発計画

| Sprint | 内容 | 期間 |
|--------|------|------|
| 0 | 環境構築・設計 | 1週間 |
| 1 | 認証とタスク管理の基礎 | 2週間 |
| 2 | タスク拡張とポモドーロタイマー | 2週間 |
| 3 | 習慣トラッカーと記録機能 | 2週間 |
| 4 | 日記機能とデータ可視化 | 2週間 |
| 5 | ルーティン管理と通知 | 2週間 |
| 6 | 目標管理と最終調整 | 2週間 |

## ドキュメント

- `docs/requirements_definition.txt` - 要件定義書
- `docs/database_design.md` - データベース設計書
- `docs/streamlit_architecture.md` - アプリケーション構成設計
- `docs/coding_standards.md` - コーディング規約
- `docs/git_workflow_guide.md` - Git運用ガイド
- `docs/setup_guide.md` - 環境構築手順書
- `docs/quick_reference.md` - クイックリファレンス

## ライセンス

MIT License
