from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from models import PostWithAuthor, PostWithStats
from crud import get_hot_posts, get_post_with_stats
from dependencies import get_db
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/hot", response_model=List[PostWithStats])
def get_hot_posts_leaderboard(
    period: str = Query("week", description="排行榜周期: week, month, year"),
    limit: int = Query(10, description="返回帖子数量", ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    获取热门帖子排行榜
    
    Args:
        period (str): 排行榜周期 ("week", "month", "year")
        limit (int): 返回帖子数量 (1-100)
        db (Session): 数据库会话依赖
        
    Returns:
        List[PostWithStats]: 热门帖子列表，按热度得分排序
        
    Raises:
        HTTPException: 当发生错误时抛出
    """
    try:
        # 验证period参数
        if period not in ["week", "month", "year"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="period参数必须是'week', 'month'或'year'之一"
            )
        
        # 获取热门帖子
        hot_posts = get_hot_posts(db, period=period, limit=limit)
        
        # 获取每个帖子的详细统计信息
        posts_with_stats = []
        for post in hot_posts:
            result = get_post_with_stats(db, post.id)
            if result:
                post_data = result["post"]
                likes_count = result["likes_count"]
                comments_count = result["comments_count"]
                shares_count = result["shares_count"]
                collections_count = result["collections_count"]
                rating_count = result["rating_count"]
                average_rating = result["average_rating"]
                
                post_with_stats = PostWithStats(
                    id=post_data.id,
                    title=post_data.title,
                    content=post_data.content,
                    author_id=post_data.author_id,
                    created_at=post_data.created_at,
                    updated_at=post_data.updated_at,
                    images=post_data.images,
                    author=post_data.author,
                    likes_count=likes_count,
                    comments_count=comments_count,
                    shares_count=shares_count,
                    collections_count=collections_count,
                    rating_count=rating_count,
                    average_rating=average_rating
                )
                posts_with_stats.append(post_with_stats)
        
        return posts_with_stats
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")