"""
認証モジュール

Supabase Authを使ったログイン・サインアップ・セッション管理を提供する。

主要機能:
- login: メール/パスワードでログイン
- signup: 新規ユーザー登録
- logout: ログアウト
- get_current_user: 現在のユーザー情報取得
- is_authenticated: 認証状態チェック
"""

import logging
from typing import Optional, Dict

import streamlit as st

from utils.supabase_client import supabase
from utils.constants import MIN_PASSWORD_LENGTH

logger = logging.getLogger(__name__)


def login(email: str, password: str) -> bool:
    """
    ログイン処理

    Supabase Authでログインし、成功時にセッション状態へユーザー情報を保存する。

    Args:
        email: メールアドレス
        password: パスワード

    Returns:
        成功時True、失敗時False
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })

        # user_profilesから追加情報取得
        profile = supabase.table("user_profiles")\
            .select("display_name")\
            .eq("id", response.user.id)\
            .single()\
            .execute()

        # セッション状態に保存
        st.session_state["user"] = {
            "id": response.user.id,
            "email": response.user.email,
            "display_name": profile.data["display_name"],
        }
        st.session_state["authenticated"] = True

        logger.info("User logged in: %s", email)
        return True

    except Exception as e:
        st.error("メールまたはパスワードが正しくありません")
        logger.error("Login error: %s", e)
        return False


def signup(email: str, password: str, display_name: str) -> bool:
    """
    サインアップ処理

    Supabase Authでユーザーを作成し、user_profilesテーブルにレコードを挿入する。

    Args:
        email: メールアドレス
        password: パスワード
        display_name: 表示名

    Returns:
        成功時True、失敗時False
    """
    try:
        if len(password) < MIN_PASSWORD_LENGTH:
            st.error(f"パスワードは{MIN_PASSWORD_LENGTH}文字以上にしてください")
            return False

        # Supabase Auth でユーザー作成
        # display_nameはユーザーメタデータとして渡し、
        # DBトリガー(handle_new_user)がuser_profilesに自動挿入する
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {
                "data": {
                    "display_name": display_name,
                }
            },
        })

        # セッション状態に保存
        st.session_state["user"] = {
            "id": response.user.id,
            "email": response.user.email,
            "display_name": display_name,
        }
        st.session_state["authenticated"] = True

        logger.info("User signed up: %s", email)
        return True

    except Exception as e:
        if "already registered" in str(e).lower():
            st.error("このメールアドレスは既に登録されています")
        else:
            st.error("登録に失敗しました。再度お試しください")
        logger.error("Signup error: %s", e)
        return False


def logout() -> None:
    """
    ログアウト処理

    Supabase Authからサインアウトし、セッション状態をクリアする。
    """
    try:
        supabase.auth.sign_out()
    except Exception as e:
        logger.error("Logout error: %s", e)
    finally:
        st.session_state.clear()


def get_current_user() -> Optional[Dict[str, str]]:
    """
    現在のユーザー情報を取得

    Returns:
        ユーザー情報の辞書（id, email, display_name）。未認証ならNone。
    """
    return st.session_state.get("user")


def is_authenticated() -> bool:
    """
    認証状態をチェック

    Returns:
        認証済みならTrue
    """
    return st.session_state.get("authenticated", False)
