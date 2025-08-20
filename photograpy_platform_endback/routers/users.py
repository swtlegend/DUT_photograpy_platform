from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from models import User, UserLogin, UserUpdate, UserProfile, ForgotPasswordRequest, ResetPasswordRequest
from schemas import UserCreate
from database import User as DBUser
from crud import create_user, authenticate_user, get_user_by_username, update_user, get_user_by_id_number, reset_user_password, get_user
from dependencies import get_db, get_current_user
from passlib.context import CryptContext
import logging
import os
import uuid
from datetime import datetime
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()

# 定义密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

UPLOAD_DIRECTORY = "uploaded_images"

# 确保上传目录存在
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# 创建logger实例
logger = logging.getLogger(__name__)


@router.post("/register")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    """
    # 由于我们已经在UserCreate模型中使用了validator进行密码一致性验证，
    # 这里不再需要手动检查密码一致性
    
    # 检查用户名是否已存在
    existing_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 检查邮箱是否已存在
    existing_email = db.query(DBUser).filter(DBUser.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="邮箱已存在")
    
    # 检查学号是否已存在
    existing_id_number = db.query(DBUser).filter(DBUser.id_number == user.id_number).first()
    if existing_id_number:
        raise HTTPException(status_code=400, detail="学号已存在")
    
    # 创建新用户
    new_user = DBUser(
        username=user.username,
        email=user.email,
        id_number=user.id_number,
        hashed_password=pwd_context.hash(user.password)
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "注册成功", "user_id": new_user.id}

@router.post("/login", response_model=User)
def login_user(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录
    
    Args:
        user_login (UserLogin): 用户登录信息
        db (Session): 数据库会话依赖
        
    Returns:
        User: 登录成功的用户信息
        
    Raises:
        HTTPException(401): 当学号或密码错误时抛出
    """
    # 验证学号是否存在
    user = get_user_by_id_number(db, user_login.id_number)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 验证密码是否正确
    if not pwd_context.verify(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="学号或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 返回完整用户信息
    return user

@router.put("/profile", response_model=UserProfile)
def update_user_profile(
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    更新用户个人资料（头像、背景图片等）
    
    Args:
        user_update (UserUpdate): 用户更新信息
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        UserProfile: 更新后的用户个人资料
        
    Raises:
        HTTPException(404): 当用户未找到时抛出
        HTTPException(500): 当发生数据库错误时抛出
    """
    try:
        db_user = update_user(db=db, user_id=current_user.id, user_update=user_update)
        # 构造UserProfile对象返回
        return UserProfile(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            is_active=db_user.is_active,
            id_number=db_user.id_number
        )
    except Exception as e:
        logger.error(f"Failed to update user profile: {str(e)}")
        raise e

@router.post("/upload-avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: DBUser = Depends(get_current_user)
):
    """
    上传用户头像
    
    Args:
        file (UploadFile): 上传的头像文件
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        dict: 包含头像文件名和URL的字典
        
    Raises:
        HTTPException(400): 当文件格式不支持时抛出
    """
    # 检查文件类型
    allowed_extensions = ["jpg", "jpeg", "png"]
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件格式，仅支持jpg、jpeg、png格式")
    
    # 生成唯一文件名
    unique_filename = f"avatar_{current_user.id}_{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    return {"filename": unique_filename, "url": f"/images/{unique_filename}"}

@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    忘记密码 - 验证学号是否存在
    
    Args:
        request (ForgotPasswordRequest): 包含学号的请求
        db (Session): 数据库会话依赖
        
    Returns:
        dict: 验证结果
        
    Raises:
        HTTPException(404): 当学号不存在时抛出
    """
    user = get_user_by_id_number(db, request.id_number)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该学号未注册"
        )
    
    return {"message": "学号验证成功，请输入新密码"}


@router.post("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    重置密码
    
    Args:
        request (ResetPasswordRequest): 包含学号和新密码的请求
        db (Session): 数据库会话依赖
        
    Returns:
        dict: 重置结果
        
    Raises:
        HTTPException(404): 当学号不存在时抛出
        HTTPException(500): 当数据库操作失败时抛出
    """
    success = reset_user_password(db, request.id_number, request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="该学号未注册"
        )
    
    return {"message": "密码重置成功"}


@router.get("/profile/{user_id}", response_model=UserProfile)
def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户个人资料
    
    Args:
        user_id (int): 用户ID
        db (Session): 数据库会话依赖
        
    Returns:
        UserProfile: 用户个人资料
        
    Raises:
        HTTPException(404): 当用户未找到时抛出
    """
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到"
        )
    
    return UserProfile(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        is_active=db_user.is_active,
        avatar_url=db_user.avatar_url,
        background_url=db_user.background_url,
        id_number=db_user.id_number
    )

@router.post("/upload-background", response_model=dict)
async def upload_background_image(
    file: UploadFile = File(...),
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传用户个人主页背景图片
    
    Args:
        file (UploadFile): 上传的背景图片文件
        current_user (DBUser): 当前认证用户依赖
        db (Session): 数据库会话依赖
        
    Returns:
        dict: 包含背景图片文件名和URL的字典，以及提示信息
        
    Raises:
        HTTPException(400): 当文件格式不支持时抛出
    """
    # 检查文件类型
    allowed_extensions = ["jpg", "jpeg", "png"]
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件格式，仅支持jpg、jpeg、png格式")
    
    # 生成唯一文件名
    unique_filename = f"background_{current_user.id}_{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 更新用户背景图片URL
    user_update = UserUpdate(background_url=f"/images/{unique_filename}")
    update_user(db=db, user_id=current_user.id, user_update=user_update)
    
    return {
        "filename": unique_filename, 
        "url": f"/images/{unique_filename}",
        "message": "背景图片上传成功"
    }

@router.post("/upload-avatar", response_model=dict)
async def upload_avatar_image(
    file: UploadFile = File(...),
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    上传用户头像图片
    
    Args:
        file (UploadFile): 上传的头像图片文件
        current_user (DBUser): 当前认证用户依赖
        db (Session): 数据库会话依赖
        
    Returns:
        dict: 包含头像图片文件名和URL的字典
        
    Raises:
        HTTPException(400): 当文件格式不支持时抛出
    """
    # 检查文件类型
    allowed_extensions = ["jpg", "jpeg", "png"]
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件格式，仅支持jpg、jpeg、png格式")
    
    # 生成唯一文件名
    unique_filename = f"avatar_{current_user.id}_{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 更新用户头像URL
    user_update = UserUpdate(avatar_url=f"/images/{unique_filename}")
    update_user(db=db, user_id=current_user.id, user_update=user_update)
    
    return {
        "filename": unique_filename, 
        "url": f"/images/{unique_filename}"
    }


@router.get("/{username}", response_model=UserProfile)
def get_user_by_username_route(
    username: str,
    db: Session = Depends(get_db)
):
    """
    通过用户名获取用户信息
    
    Args:
        username (str): 用户名
        db (Session): 数据库会话依赖
        
    Returns:
        UserProfile: 用户个人资料
        
    Raises:
        HTTPException(404): 当用户未找到时抛出
    """
    db_user = get_user_by_username(db, username)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到"
        )
    
    # 获取用户统计数据
    from crud import get_followers_count, get_following_count, get_user_total_likes_received
    from sqlalchemy.orm import Session
    from database import Post as DBPost
    
    followers_count = get_followers_count(db, db_user.id)
    following_count = get_following_count(db, db_user.id)
    posts_count = db.query(DBPost).filter(DBPost.author_id == db_user.id).count()
    likes_received = get_user_total_likes_received(db, db_user.id)
    
    user_stats = {
        "followers_count": followers_count,
        "following_count": following_count,
        "posts_count": posts_count,
        "likes_received": likes_received
    }
    
    return UserProfile(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        is_active=db_user.is_active,
        avatar_url=db_user.avatar_url,
        background_url=db_user.background_url,
        id_number=db_user.id_number,
        stats=user_stats
    )

@router.get("/info/{user_id}")
def get_user_info(user_id: int, db: Session = Depends(get_db)):
    """
    获取用户信息接口
    
    Args:
        user_id (int): 用户ID
        db (Session): 数据库会话依赖
        
    Returns:
        dict: 用户信息
        
    Raises:
        HTTPException(404): 当用户未找到时抛出
    """
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户未找到"
        )
    
    # 确保返回完整的用户信息，包括所有必要字段
    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email or "",
        "avatar_url": db_user.avatar_url or "",
        "background_url": db_user.background_url or "",
        "is_active": db_user.is_active,
        "id_number": db_user.id_number
    }
