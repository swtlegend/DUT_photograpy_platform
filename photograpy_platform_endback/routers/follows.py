from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from models import FollowCreate, Follow, UserStats, UserProfile
from crud import create_follow, delete_follow, get_follow, get_followers_count, get_user_total_likes_received
from dependencies import get_db, get_current_user
from database import User as DBUser
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=Follow)
def follow_user(
    follow: FollowCreate, 
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    """
    关注用户
    
    Args:
        follow (FollowCreate): 包含被关注用户ID的请求数据
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        Follow: 关注对象
        
    Raises:
        HTTPException: 当发生错误时抛出
    """
    try:
        # 不能关注自己
        if current_user.id == follow.following_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="不能关注自己")
        
        db_follow = create_follow(db=db, follow=follow, follower_id=current_user.id)
        return db_follow
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{following_id}")
def unfollow_user(
    following_id: int,
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    """
    取消关注用户
    
    Args:
        following_id (int): 被关注用户ID
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        dict: 操作结果
        
    Raises:
        HTTPException: 当发生错误时抛出
    """
    try:
        delete_follow(db=db, follower_id=current_user.id, following_id=following_id)
        return {"message": "取消关注成功"}
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{following_id}", response_model=bool)
def check_if_following(
    following_id: int,
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    """
    检查当前用户是否已关注指定用户
    
    Args:
        user_id (int): 被关注用户ID (路径参数)
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        bool: 是否已关注
        
    Raises:
        HTTPException: 当发生错误时抛出
    """
    try:
        follow = get_follow(db=db, follower_id=current_user.id, following_id=following_id)
        return follow is not None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/stats/{user_id}", response_model=UserStats)
def get_user_stats(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    获取用户统计信息
    
    Args:
        user_id (int): 用户ID
        db (Session): 数据库会话依赖
        
    Returns:
        UserStats: 用户统计信息
        
    Raises:
        HTTPException: 当发生错误时抛出
    """
    try:
        followers_count = get_followers_count(db=db, user_id=user_id)
        total_likes_received = get_user_total_likes_received(db=db, user_id=user_id)
        
        return UserStats(
            followers_count=followers_count,
            total_likes_received=total_likes_received
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
