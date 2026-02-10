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