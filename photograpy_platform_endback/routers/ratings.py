from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models import RatingCreate, Rating, RatingWithUser
from crud import create_rating, get_rating, update_rating, delete_rating, get_post_with_stats
from dependencies import get_db, get_current_user
from database import User as DBUser
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=Rating)
def create_new_rating(
    rating: RatingCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    创建新的评分
    
    Args:
        rating (RatingCreate): 评分信息
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        Rating: 评分对象
        
    Raises:
        HTTPException(400): 当用户已经对此帖子评过分时抛出
        HTTPException(404): 当帖子不存在时抛出
        HTTPException(500): 当发生未预期错误时抛出
    """
    try:
        db_rating = create_rating(db=db, rating=rating, user_id=current_user.id)
        return db_rating
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{post_id}", response_model=Rating)
def update_existing_rating(
    post_id: int,
    rating: RatingCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    更新评分
    
    Args:
        post_id (int): 帖子ID
        rating (RatingCreate): 评分信息
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        Rating: 更新后的评分对象
        
    Raises:
        HTTPException(404): 当评分记录不存在时抛出
        HTTPException(500): 当发生未预期错误时抛出
    """
    try:
        # 确保更新的是同一个post_id
        if rating.post_id != post_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="帖子ID不匹配")
        
        db_rating = update_rating(db=db, post_id=post_id, user_id=current_user.id, rating_update=rating)
        return db_rating
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{post_id}")
def delete_existing_rating(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    删除评分
    
    Args:
        post_id (int): 帖子ID
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        dict: 删除结果
        
    Raises:
        HTTPException(404): 当评分记录不存在时抛出
        HTTPException(500): 当发生未预期错误时抛出
    """
    try:
        delete_rating(db=db, post_id=post_id, user_id=current_user.id)
        return {"message": "评分已删除"}
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{post_id}/stats")
def get_rating_stats(
    post_id: int,
    db: Session = Depends(get_db)
):
    """
    获取帖子评分统计信息
    
    Args:
        post_id (int): 帖子ID
        db (Session): 数据库会话依赖
        
    Returns:
        dict: 包含评分人数和平均分的信息
        
    Raises:
        HTTPException(404): 当帖子未找到时抛出
        HTTPException(500): 当发生未预期错误时抛出
    """
    try:
        result = get_post_with_stats(db, post_id=post_id)
        if result is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子未找到")
        
        return {
            "rating_count": result["rating_count"],
            "average_rating": result["average_rating"]
        }
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")