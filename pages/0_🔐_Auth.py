"""
認証画面 - ログイン・新規登録

タブ切り替えでログインと新規登録を提供する。
認証済みユーザーはHome.pyへリダイレクトされる。
"""

import streamlit as st

from components.auth import login, signup, is_authenticated
from utils.constants import MIN_PASSWORD_LENGTH

st.set_page_config(
    page_title="ログイン",
    page_icon="🔐",
    layout="centered",
)

# 既にログイン済みならリダイレクト
if is_authenticated():
    st.switch_page("Home.py")

# タイトル
st.title("🔐 モンクモード支援システム")
st.caption("ログインまたは新規登録してください")

# タブ
tab_login, tab_signup = st.tabs(["ログイン", "新規登録"])

# ログインタブ
with tab_login:
    st.subheader("ログイン")

    with st.form("login_form"):
        email = st.text_input("メールアドレス", key="login_email")
        password = st.text_input(
            "パスワード", type="password", key="login_password"
        )

        submit = st.form_submit_button("ログイン", use_container_width=True)

        if submit:
            if not email or not password:
                st.error("すべての項目を入力してください")
            else:
                if login(email, password):
                    st.success("ログインしました")
                    st.rerun()

# サインアップタブ
with tab_signup:
    st.subheader("新規登録")

    with st.form("signup_form"):
        display_name = st.text_input("表示名", key="signup_name")
        email = st.text_input("メールアドレス", key="signup_email")
        password = st.text_input(
            f"パスワード（{MIN_PASSWORD_LENGTH}文字以上）",
            type="password",
            key="signup_password",
        )
        password_confirm = st.text_input(
            "パスワード確認", type="password", key="signup_password_confirm"
        )

        submit = st.form_submit_button("登録", use_container_width=True)

        if submit:
            if not display_name or not email or not password or not password_confirm:
                st.error("すべての項目を入力してください")
            elif len(password) < MIN_PASSWORD_LENGTH:
                st.error(f"パスワードは{MIN_PASSWORD_LENGTH}文字以上にしてください")
            elif password != password_confirm:
                st.error("パスワードが一致しません")
            else:
                if signup(email, password, display_name):
                    st.success("登録が完了しました")
                    st.rerun()
