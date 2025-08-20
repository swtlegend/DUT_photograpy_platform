from fastapi import APIRouter, Depends, HTTPException, status, Path
from sqlalchemy.orm import Session
from typing import List
from models import CommentCreate, CommentWithAuthor
from crud import create_comment, get_comments_by_post, delete_comment, get_comment
from dependencies import get_db, get_current_user
from database import User as DBUser
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=CommentWithAuthor)
def create_new_comment(
    comment: CommentCreate, 
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    """
    创建新的评论
    
    Args:
        comment (CommentCreate): 包含评论内容和帖子ID的请求数据
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        CommentWithAuthor: 包含作者信息的评论对象
        
    Raises:
        HTTPException: 当发生预期错误时抛出
        HTTPException(500): 当发生未预期错误时抛出
    """
    try:
        db_comment = create_comment(db=db, comment=comment, author_id=current_user.id)
        return db_comment
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/post/{post_id}", response_model=List[CommentWithAuthor])
def read_comments_by_post(
    post_id: int,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    获取指定帖子的所有评论
    
    Args:
        post_id (int): 帖子ID
        skip (int): 跳过的记录数，默认为0
        limit (int): 限制返回记录数，默认为100
        db (Session): 数据库会话依赖
        
    Returns:
        List[CommentWithAuthor]: 评论列表，包含作者信息
        
    Raises:
        HTTPException: 当发生预期错误时抛出
        HTTPException(500): 当发生未预期错误时抛出
    """
    try:
        comments = get_comments_by_post(db=db, post_id=post_id, skip=skip, limit=limit)
        return comments
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{comment_id}", response_model=CommentWithAuthor)
def delete_existing_comment(
    comment_id: int,
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    """
    删除评论
    
    Args:
        comment_id (int): 评论ID
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        CommentWithAuthor: 被删除的评论
        
    Raises:
        HTTPException(403): 当用户无权限删除此评论时抛出
        HTTPException(404): 当评论未找到时抛出
        HTTPException(500): 当发生未预期错误时抛出
    """
    try:
        # 检查评论是否存在
        db_comment = get_comment(db, comment_id=comment_id)
        if db_comment is None:
            raise HTTPException(status_code=404, detail="评论未找到")
        
        # 检查用户是否有权限删除此评论
        if db_comment.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权限删除此评论")
        
        deleted_comment = delete_comment(db=db, comment_id=comment_id)
        return deleted_comment
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
