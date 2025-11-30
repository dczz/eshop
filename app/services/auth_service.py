import secrets
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from app.models.authorization_code_model import AuthorizationCode
from app.models.users_model import User


def create_authorization_code(
        db: Session,
        *,
        user: User,
        client_id: str,
        code_challenge: str,
        code_challenge_method: str,
        redirect_uri: str,
        expires_in_seconds: int = 600
) -> AuthorizationCode:
    """
    创建并存储一个新的授权码
    """
    code = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(seconds=expires_in_seconds)

    auth_code = AuthorizationCode(
        code=code,
        user_id=user.id,
        client_id=client_id,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
        expires_at=expires_at,
        redirect_uri=redirect_uri,
    )
    db.add(auth_code)
    db.commit()
    db.refresh(auth_code)
    return auth_code


def get_and_validate_authorization_code(db: Session, code: str, client_id: str,
                                        redirect_uri: str) -> AuthorizationCode | None:
    """
    获取并验证授权码
    1. 检查是否存在
    2. 检查客户端ID和重定向URI是否匹配
    3. 检查是否过期
    """
    auth_code: AuthorizationCode | None = db.query(AuthorizationCode).filter(AuthorizationCode.code == code).first()

    if not auth_code:
        return None

    # 验证客户端ID和重定向URI
    if auth_code.client_id != client_id or auth_code.redirect_uri != redirect_uri:
        # 出于安全考虑，如果客户端ID或重定向URI不匹配，应立即作废该授权码
        db.delete(auth_code)
        db.commit()
        return None

    # 检查授权码是否已过期
    print(f"{auth_code.expires_at=}")
    if datetime.now() > auth_code.expires_at:
        db.delete(auth_code)
        db.commit()
        return None

    return auth_code


def delete_authorization_code(db: Session, auth_code: AuthorizationCode):
    """
    在授权码使用后将其删除
    """
    db.delete(auth_code)
    db.commit()
