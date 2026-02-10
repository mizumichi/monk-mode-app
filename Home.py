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