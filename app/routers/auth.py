from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Form, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.db.database import get_db  # Updated import path
from app.services import users_service, auth_service
from app.core import security
from app.schemas.token_schema import Token, TokenData
from app.core.config import SECRET_KEY, ALGORITHM
from app.models.users_model import User

from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


@router.get("/authorize", response_class=HTMLResponse)
async def authorize_get(
        request: Request,
        client_id: Annotated[str, Query()],
        redirect_uri: Annotated[str, Query()],
        code_challenge: Annotated[str, Query()],
        code_challenge_method: Annotated[str, Query("S256", enum=["S256", "plain"])],
        state: Annotated[str | None, Query(None)],
):
    """
    第一步: 显示登录页面
    客户端将用户重定向到此, 并附带PKCE质询参数
    """
    # 将查询参数传递给模板，以便在表单中作为隐藏字段提交
    return f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>登录授权 - eshop</title>
        <script src="https://cdn.tailwindcss.com"></script>
        <style>
            @keyframes fadeIn {{
                from {{ opacity: 0; transform: scale(0.95); }}
                to {{ opacity: 1; transform: scale(1); }}
            }}
            .fade-in {{
                animation: fadeIn 0.5s ease-out forwards;
            }}
        </style>
    </head>
    <body class="bg-gray-100 flex items-center justify-center min-h-screen">
        <div class="fade-in w-full max-w-md p-8 space-y-6 bg-white rounded-xl shadow-lg">
            <div class="flex justify-center">
                 <svg class="h-12 w-auto text-indigo-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M13.5 21v-7.5a.75.75 0 0 1 .75-.75h3a.75.75 0 0 1 .75.75V21m-4.5 0H2.25a.75.75 0 0 1-.75-.75v-7.5a.75.75 0 0 1 .75-.75h13.5a.75.75 0 0 1 .75.75v7.5a.75.75 0 0 1-.75.75H13.5m-4.5 0v-7.5a.75.75 0 0 1 .75-.75h3a.75.75 0 0 1 .75.75V21m-4.5 0h-3.75a.75.75 0 0 1-.75-.75V8.25c0-.414.336-.75.75-.75h16.5a.75.75 0 0 1 .75.75v12a.75.75 0 0 1-.75.75h-3.75m-4.5-15.75a.75.75 0 0 1 .75-.75h3a.75.75 0 0 1 .75.75v3a.75.75 0 0 1-.75.75h-3a.75.75 0 0 1-.75-.75v-3Z" />
                </svg>
            </div>
            <h1 class="text-3xl font-bold text-center text-gray-800">授权登录 E-Shop</h1>
            <p class="text-center text-gray-500">使用您的账户以授权访问</p>
            <form method="post" class="space-y-6">
                <input type="hidden" name="client_id" value="{client_id}">
                <input type="hidden" name="redirect_uri" value="{redirect_uri}">
                <input type="hidden" name="code_challenge" value="{code_challenge}">
                <input type="hidden" name="code_challenge_method" value="{code_challenge_method}">
                <input type="hidden" name="state" value="{state or ''}">
                
                <div>
                    <label for="email" class="text-sm font-medium text-gray-700">邮箱地址</label>
                    <input id="email" name="email" type="email" autocomplete="email" required class="mt-1 block w-full px-4 py-3 text-gray-900 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-200">
                </div>
                
                <div>
                    <label for="password" class="text-sm font-medium text-gray-700">密码</label>
                    <input id="password" name="password" type="password" autocomplete="current-password" required class="mt-1 block w-full px-4 py-3 text-gray-900 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 transition duration-200">
                </div>
                
                <div>
                    <button type="submit" class="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-transform transform hover:scale-105 duration-300">
                        安全登录
                    </button>
                </div>
            </form>
            <div class="text-center text-xs text-gray-400">
                <p>&copy; 2025 eshop. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """


@router.post("/authorize")
async def authorize_post(
        db: Annotated[Session, Depends(get_db)],
        email: Annotated[str, Form(...)],
        password: Annotated[str, Form(...)],
        client_id: Annotated[str, Form(...)],
        redirect_uri: Annotated[str, Form(...)],
        code_challenge: Annotated[str, Form(...)],
        code_challenge_method: Annotated[str, Form(...)],
        state: Annotated[str | None, Form(None)],
):
    """
    第二步: 处理登录表单, 验证用户, 生成授权码并重定向
    """
    user = users_service.authenticate_user(db, email=email, password=password)
    # for test user

    print(f"{user=}")
    if not user:
        # 在实际应用中, 这里应该返回一个带错误提示的登录页面
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建授权码
    auth_code = auth_service.create_authorization_code(
        db=db,
        user=user,
        client_id=client_id,
        redirect_uri=redirect_uri,
        code_challenge=code_challenge,
        code_challenge_method=code_challenge_method,
    )

    # 构建重定向URL
    redirect_url = f"{redirect_uri}?code={auth_code.code}"
    if state:
        redirect_url += f"&state={state}"

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.post("/token", response_model=Token)
async def token(
        db: Annotated[Session, Depends(get_db)],
        grant_type: Annotated[str, Form(...)],
        code: Annotated[str, Form(...)],
        redirect_uri: Annotated[str, Form(...)],
        client_id: Annotated[str, Form(...)],
        code_verifier: Annotated[str, Form(...)],
) -> dict[str, str]:
    print(f"/auth/token {grant_type=} {code=} {client_id=} {redirect_uri=} {code_verifier=}")
    """
    第三步: 用授权码和code_verifier交换access token
    """
    if grant_type != "authorization_code":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持的grant_type",
        )

    # 验证授权码
    auth_code = auth_service.get_and_validate_authorization_code(
        db=db, code=code, client_id=client_id, redirect_uri=redirect_uri
    )
    if not auth_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的授权码、客户端ID或重定向URI",
        )

    # 验证PKCE code_verifier
    if not security.verify_code_challenge(
            code_verifier=code_verifier,
            code_challenge=auth_code.code_challenge,
            code_challenge_method=auth_code.code_challenge_method
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的code_verifier",
        )

    # 授权码只能使用一次, 立即删除
    auth_service.delete_authorization_code(db, auth_code)
    user = users_service.get_user_by_id(db, auth_code.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="找不到与授权码关联的用户",
        )

    # 创建access token
    access_token = security.create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[Session, Depends(get_db)]) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = users_service.get_user_by_email(db, email=token_data.username)
    if user is None:
        raise credentials_exception
    return user
