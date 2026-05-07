from backend.database.methods.user_methods import UserService
from fastapi import Header
from .include import *
from backend.api.security import (
    get_current_user,
    require_admin,
    require_same_user_or_admin,
    session_manager,
)
from backend.database.models import User

user_router = APIRouter(
    tags=['Users']
)


@user_router.post(
    '/auth/register',
    response_model=CreatedModel
)
@user_router.post(
    '/user/register',
    response_model=CreatedModel
    ,
    include_in_schema=False
)
async def create_user(
    user: UserCreate,
    user_db: Annotated[UserService, Depends(sql_helper_factory(UserService))]
):
    created_id: int = await user_db.create_user(
        user.email,
        user.name,
        user.password,
        secret_question=user.secret_question,
        secret_answer=user.secret_answer,
    )
    return {
        'created_id': created_id
    }


@user_router.post(
    '/auth/login',
    response_model=AuthResponse
)
@user_router.post(
    '/user/sign_in',
    response_model=ActiveModel
    ,
    include_in_schema=False
)
async def sign_in_user(
    user: UserLogin,
    user_db: Annotated[UserService, Depends(sql_helper_factory(UserService))]
):
    user_data = await user_db.sign_in(user.email, user.password)
    access, refresh = session_manager.issue_tokens(user_data["id"])
    return {
        **user_data,
        "access_token": access.token,
        "refresh_token": refresh.token,
        "access_expires_at": access.expires_at,
        "refresh_expires_at": refresh.expires_at,
    }


@user_router.post(
    '/auth/refresh',
    response_model=AuthResponse
)
async def refresh_session(
    data: RefreshTokenRequest,
    user_db: Annotated[UserService, Depends(sql_helper_factory(UserService))]
):
    access, refresh = session_manager.refresh_access_token(data.refresh_token)
    user = await user_db.get_by_id(access.user_id)

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role.value,
        "is_active": user.is_active,
        "access_token": access.token,
        "refresh_token": refresh.token,
        "access_expires_at": access.expires_at,
        "refresh_expires_at": refresh.expires_at,
    }


@user_router.post(
    '/auth/logout',
    response_model=StatusModel
)
async def logout_user(
    data: LogoutRequest,
    authorization: str | None = Header(default=None),
):
    token = None
    if authorization:
        auth_type, _, raw_token = authorization.partition(" ")
        if auth_type.lower() == "bearer" and raw_token:
            token = raw_token

    session_manager.revoke_access_token(token)
    session_manager.revoke_refresh_token(data.refresh_token)
    return {"status": True}


@user_router.get(
    '/auth/me',
    response_model=ActiveModel
)
async def get_current_session_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@user_router.post(
    '/user/deactivate/{user_id}',
    response_model=StatusModel
)
async def deactivate_user(
    user_id: int,
    user_db: Annotated[UserService, Depends(sql_helper_factory(UserService))],
    _: Annotated[User, Depends(require_admin)],
):
    result: bool = await user_db.deactivate_user(user_id)
    session_manager.revoke_user_sessions(user_id)
    return {
        'status': result
    }


@user_router.post(
    '/user/update/{user_id}',
    response_model=StatusModel
)
async def update_user(
    user_id: int,
    user: UserRequestUpdate,
    user_db: Annotated[UserService, Depends(sql_helper_factory(UserService))],
    current_user: Annotated[User, Depends(get_current_user)],
):
    require_same_user_or_admin(current_user, user_id)
    status: bool = await user_db.update_user(
        user_id,
        user.model_dump(exclude_unset=True)
    )
    return {
        'status': status
    }


@user_router.post(
    '/user/set_keyword',
    response_model=StatusModel
)
async def set_keyword(
    data: SetKeyword,
    user_db: Annotated[UserService, Depends(sql_helper_factory(UserService))],
    current_user: Annotated[User, Depends(get_current_user)],
):
    require_same_user_or_admin(current_user, data.user_id)
    result: bool = await user_db.set_secret_data(
        user_id=data.user_id,
        keyword=data.keyword,
        secret_question=data.secret_question,
        secret_answer=data.secret_answer,
    )
    return {
        'status': result
    }


@user_router.post(
    '/user/recover_password',
    response_model=StatusModel
)
async def recover_password(
    data: RecoverPassword,
    user_db: Annotated[UserService, Depends(sql_helper_factory(UserService))]
):
    result: bool = await user_db.recover_password(
        data.email,
        data.new_password,
        keyword=data.keyword,
        secret_question=data.secret_question,
        secret_answer=data.secret_answer,
    )
    return {
        'status': result
    }


@user_router.get(
    '/user/{user_id}',
    response_model=UserResponse
)
async def get_user_by_id(
    user_id: int,
    user_db: Annotated[UserService, Depends(sql_helper_factory(UserService))],
    current_user: Annotated[User, Depends(get_current_user)],
):
    require_same_user_or_admin(current_user, user_id)
    return await user_db.get_by_id(user_id)


@user_router.get(
    '/users',
    response_model=list[UserResponse]
)
async def get_users(
    user_db: Annotated[UserService, Depends(sql_helper_factory(UserService))],
    _: Annotated[User, Depends(require_admin)],
    page: int = 1,
    per_page: int = 10,
):
    return await user_db.get_all(page, per_page)
