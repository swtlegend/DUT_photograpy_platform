from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from sqlalchemy.orm import Session
from models import LikeCreate, Like, ShareCreate, Share
from crud import create_like, delete_like, create_share, delete_share, get_like, get_share
from dependencies import get_db, get_current_user
from database import User as DBUser
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# 点赞相关接口
@router.post("/likes", response_model=Like)
def like_post(
    like: LikeCreate, 
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    """
    点赞帖子
    
    Args:
        like (LikeCreate): 包含帖子ID的请求数据
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        Like: 点赞对象
        
    Raises:
        HTTPException: 当发生错误时抛出
    """
    try:
        db_like = create_like(db=db, like=like, user_id=current_user.id)
        return db_like
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/likes")
def unlike_post(
    post_id: int = Query(..., title="帖子ID"),
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    """
    取消点赞
    
    Args:
        post_id (int): 帖子ID
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        dict: 操作结果
        
    Raises:
        HTTPException: 当发生错误时抛出
    """
    try:
        delete_like(db=db, user_id=current_user.id, post_id=post_id)
        return {"message": "取消点赞成功"}
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/likes/{post_id}", response_model=bool)
def check_if_liked(
    post_id: int,
    user_id: int = Query(None, description="用户ID，未提供时返回False"),
    db: Session = Depends(get_db)
):
    """
    检查指定用户是否已点赞指定帖子
    
    Args:
        post_id (int): 帖子ID
        user_id (int, optional): 用户ID，未提供时返回False
        db (Session): 数据库会话依赖
        
    Returns:
        bool: 是否已点赞，如果未提供user_id则返回False
        
    Raises:
        HTTPException: 当发生错误时抛出
    """
    try:
        # 如果没有提供用户ID，则返回False
        if user_id is None:
            return False
            
        like = get_like(db=db, user_id=user_id, post_id=post_id)
        return like is not None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

# 分享相关接口
@router.post("/shares", response_model=Share)
def share_post(
    share: ShareCreate, 
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    """
    分享帖子
    
    Args:
        share (ShareCreate): 包含帖子ID的请求数据
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        Share: 分享对象
        
    Raises:
        HTTPException: 当发生错误时抛出
    """
    try:
        db_share = create_share(db=db, share=share, user_id=current_user.id)
        return db_share
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/shares")
def unshare_post(
    post_id: int = Query(..., title="帖子ID"),
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    """
    取消分享
    
    Args:
        post_id (int): 帖子ID
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        dict: 操作结果
        
    Raises:
        HTTPException: 当发生错误时抛出
    """
    try:
        delete_share(db=db, user_id=current_user.id, post_id=post_id)
        return {"message": "取消分享成功"}
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/shares/{post_id}", response_model=bool)
def check_if_shared(
    post_id: int,
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    """
    检查当前用户是否已分享指定帖子
    
    Args:
        post_id (int): 帖子ID
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        bool: 是否已分享
        
    Raises:
        HTTPException: 当发生错误时抛出
    """
    try:
        share = get_share(db=db, user_id=current_user.id, post_id=post_id)
        return share is not None
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
