import base64
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Optional

from jose import jwt
import bcrypt # 导入bcrypt
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    使用bcrypt验证明文密码和存储的哈希密码是否匹配。
    plain_password: 用户输入的明文密码字符串
    hashed_password: 从数据库中取出的哈希密码字符串
    """
    # bcrypt.checkpw 期望两个参数都是bytes类型
    # 注意：如果hashed_password在数据库中实际存储的是bytes而不是string，
    # 那么hashed_password.encode('utf-8')会导致TypeError
    # 我们假设hashed_password是从String类型的数据库字段中读出的字符串
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """
    使用bcrypt生成密码的哈希值。
    返回的哈希值是一个字符串，方便存储到数据库。
    """
    # bcrypt.gensalt() 生成一个盐
    salt = bcrypt.gensalt()
    # bcrypt.hashpw 返回一个bytes类型，需要解码为字符串才能存入数据库的String字段
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    创建JWT access token
    :param data: 要编码到token中的数据
    :param expires_delta: token的过期时间
    :return:编码后的JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_code_challenge(code_verifier: str, code_challenge_method: str) -> str:
    """
    根据code_verifier和指定的转换方法生成code_challenge
    :param code_verifier: 随机生成的验证码
    :param code_challenge_method: 转换方法，支持 "S256" 或 "plain"
    :return: 生成的code_challenge
    """
    if code_challenge_method == "S256":
        hashed = hashlib.sha256(code_verifier.encode("ascii")).digest()
        return base64.urlsafe_b64encode(hashed).rstrip(b"=").decode("ascii")
    elif code_challenge_method == "plain":
        return code_verifier
    else:
        raise ValueError("Unsupported code_challenge_method")


def verify_code_challenge(code_verifier: str, code_challenge: str, code_challenge_method: str) -> bool:
    """
    验证code_verifier是否与给定的code_challenge匹配
    """
    generated_challenge = create_code_challenge(code_verifier, code_challenge_method)
    return generated_challenge == code_challenge
