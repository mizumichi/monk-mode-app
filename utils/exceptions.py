"""
カスタム例外クラス

エラーハンドリングの階層:
- MonkModeException: 基底例外
  - DatabaseError: データベース操作エラー
  - AuthenticationError: 認証エラー
  - ValidationError: バリデーションエラー
  - NotFoundError: リソース未発見エラー
"""


class MonkModeException(Exception):
    """基底例外クラス"""
    pass


class DatabaseError(MonkModeException):
    """データベース操作エラー"""
    pass


class AuthenticationError(MonkModeException):
    """認証エラー"""
    pass


class ValidationError(MonkModeException):
    """バリデーションエラー"""
    pass


class NotFoundError(MonkModeException):
    """リソース未発見エラー"""
    pass
