from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from models import PostCreate, Post, PostWithAuthor, PostUpdate, PostWithStats
from crud import create_post, get_posts, get_posts_by_author, get_post, delete_post, update_post, get_post_with_stats, get_likes_count, get_shares_count, get_collections_count, get_rating_info, get_comments_count, get_likes_counts, get_comments_counts, get_shares_counts, get_collections_counts, get_posts_with_stats, get_ratings_info
from dependencies import get_db, get_current_user
from database import User as DBUser
import logging
import os
import uuid
from datetime import datetime

router = APIRouter()
logger = logging.getLogger(__name__)

# 确保上传目录存在
UPLOAD_DIRECTORY = "./uploaded_images"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@router.post("/", response_model=PostWithAuthor)
def create_new_post(
    post: PostCreate, 
    db: Session = Depends(get_db), 
    current_user: DBUser = Depends(get_current_user)
):
    """
    创建新的帖子
    
    Args:
        post (PostCreate): 包含帖子标题和内容的请求数据
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        PostWithAuthor: 包含作者信息的帖子对象
        
    Raises:
        HTTPException: 当发生预期错误时抛出
        HTTPException(500): 当发生未预期错误时抛出
    """
    try:
        db_post = create_post(db=db, post=post, author_id=current_user.id)
        return get_post(db, db_post.id)
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.post("/upload-image")
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片文件并保存到服务器
    
    Args:
        file (UploadFile): 通过表单上传的图片文件对象
        
    Returns:
        dict: 包含保存后的文件名和访问URL的字典
            - filename (str): 服务器上保存的唯一文件名
            - url (str): 访问该文件的完整URL路径
            
    Raises:
        HTTPException: 当文件格式不被支持时抛出400状态码异常
    """
    # 检查文件类型
    allowed_extensions = ["jpg", "jpeg", "png", "raw"]
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件格式")
    
    # 生成唯一文件名
    unique_filename = f"{uuid.uuid4()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
    
    # 返回完整URL
    full_url = f"http://localhost:8000/images/{unique_filename}"
    return {"filename": unique_filename, "url": full_url}

@router.put("/{post_id}", response_model=PostWithAuthor)
def update_existing_post(
    post_id: int, 
    post_update: PostUpdate, 
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    更新帖子信息（标题、内容、图片、可见性等）
    
    Args:
        post_id (int): 帖子ID
        post_update (PostUpdate): 帖子更新信息
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        PostWithAuthor: 更新后的帖子信息
        
    Raises:
        HTTPException(404): 当帖子未找到时抛出
        HTTPException(403): 当用户无权限更新帖子时抛出
        HTTPException(500): 当发生数据库错误时抛出
    """
    try:
        # 检查帖子是否存在
        db_post = get_post(db, post_id)
        if db_post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子未找到")
        
        # 检查是否是帖子作者
        if db_post.author_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="无权限更新此帖子")
        
        db_post = update_post(db=db, post_id=post_id, post_update=post_update)
        if db_post is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="帖子未找到")
        return get_post(db, db_post.id)
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=List[PostWithStats])
def read_posts(
    skip: int = 0, 
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    """
    获取帖子列表，包含统计信息
    
    Args:
        skip (int): 跳过的记录数，用于分页，默认为0
        limit (int): 返回的最大记录数，用于分页，默认为20
        db (Session): 数据库会话，通过依赖注入获取
        
    Returns:
        List[PostWithStats]: 帖子列表，每个帖子包含统计信息
    """
    try:
        posts_with_stats_data = get_posts_with_stats(db, skip=skip, limit=limit)
        
        # 为每个帖子添加can_collect字段（默认为True，因为没有当前用户）
        posts_with_stats = []
        for post_data in posts_with_stats_data:
            # 默认情况下可以收藏（对于未登录用户）
            post_data["can_collect"] = True
            posts_with_stats.append(post_data)
        
        return posts_with_stats
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/user/{user_id}", response_model=List[PostWithStats])
def read_user_posts(
    user_id: int,
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    获取指定用户的帖子列表，包含统计信息
    
    Args:
        user_id (int): 用户ID
        skip (int): 跳过的记录数，用于分页，默认为0
        limit (int): 返回的最大记录数，用于分页，默认为20
        db (Session): 数据库会话，通过依赖注入获取
        
    Returns:
        List[PostWithStats]: 用户的帖子列表，每个帖子都包含统计信息
    """
    posts = get_posts_by_author(db, user_id=user_id, skip=skip, limit=limit)
    if not posts:
        return []
    
    post_ids = [post.id for post in posts]
    likes_counts = get_likes_counts(db, post_ids)
    comments_counts = get_comments_counts(db, post_ids)
    shares_counts = get_shares_counts(db, post_ids)
    collections_counts = get_collections_counts(db, post_ids)
    ratings_info = get_ratings_info(db, post_ids)
    
    # 构造包含统计信息的帖子列表
    posts_with_stats = []
    for post in posts:
        post_dict = post.__dict__.copy()
        post_dict.update({
            "likes_count": likes_counts.get(post.id, 0),
            "comments_count": comments_counts.get(post.id, 0),
            "shares_count": shares_counts.get(post.id, 0),
            "collections_count": collections_counts.get(post.id, 0),
            "average_rating": ratings_info.get(post.id, {}).get("average_rating", 0),
            "ratings_count": ratings_info.get(post.id, {}).get("count", 0),
            "can_collect": True  # 默认可以收藏
        })
        posts_with_stats.append(PostWithStats(**post_dict))
    
    return posts_with_stats

@router.get("/{post_id}", response_model=PostWithStats)
def read_post(
    post_id: int, 
    user_id: int = None,  # 可选的用户ID参数
    db: Session = Depends(get_db)
):
    """
    根据ID获取帖子详情，并包含统计信息
    
    Args:
        post_id (int): 帖子ID
        db (Session): 数据库会话，通过依赖注入获取
        current_user (DBUser): 当前登录用户，通过依赖注入获取
        
    Returns:
        PostWithStats: 包含统计信息的帖子对象
        
    Raises:
        HTTPException: 帖子不存在时抛出404异常
    """
    post_with_stats = get_post_with_stats(db, post_id)
    if post_with_stats is None:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    # 如果提供了用户ID，则检查当前用户是否是帖子作者
    # 如果是作者则不能收藏自己的帖子
    if user_id is not None:
        post_with_stats["can_collect"] = post_with_stats["author_id"] != user_id
    else:
        # 如果没有提供用户ID，默认可以收藏
        post_with_stats["can_collect"] = True
    
    return post_with_stats

@router.delete("/{post_id}", response_model=Post)
def delete_existing_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    删除帖子
    
    Args:
        post_id (int): 帖子ID
        db (Session): 数据库会话依赖
        current_user (DBUser): 当前认证用户依赖
        
    Returns:
        Post: 被删除的帖子
        
    Raises:
        HTTPException(403): 当用户无权限删除此帖子时抛出
        HTTPException(404): 当帖子未找到时抛出
        HTTPException(500): 当发生未预期错误时抛出
    """
    try:
        # 检查帖子是否存在
        db_post = get_post(db, post_id=post_id)
        if db_post is None:
            raise HTTPException(status_code=404, detail="帖子未找到")
        
        # 检查用户是否有权限删除此帖子
        if db_post.author_id != current_user.id:
            raise HTTPException(status_code=403, detail="无权限删除此帖子")
        
        deleted_post = delete_post(db=db, post_id=post_id)
        return deleted_post
    except HTTPException as e:
        logger.error(f"HTTPException occurred: {e.detail}")
        raise
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/search/", response_model=List[PostWithStats])
def search_posts(
    query: str,
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """
    根据标题搜索帖子，按热度排序
    
    Args:
        query (str): 搜索关键词
        skip (int): 跳过的记录数，默认为0
        limit (int): 限制返回记录数，默认为100
        db (Session): 数据库会话依赖
        
    Returns:
        List[PostWithStats]: 符合搜索条件的帖子列表，按热度排序
        
    Raises:
        HTTPException: 当发生错误时抛出
    """
    try:
        from crud import search_posts, calculate_hot_score
        
        # 搜索帖子
        posts = search_posts(db, query=query, skip=skip, limit=limit)
        
        if not posts:
            return []
        
        # 批量获取所有帖子的统计信息，提高查询性能
        post_ids = [post.id for post in posts]
        likes_counts = get_likes_counts(db, post_ids)
        comments_counts = get_comments_counts(db, post_ids)
        shares_counts = get_shares_counts(db, post_ids)
        collections_counts = get_collections_counts(db, post_ids)
        
        # 为每个帖子组合数据
        posts_with_stats = []
        post_scores = []
        
        for post in posts:
            post_id = post.id
            likes_count = likes_counts.get(post_id, 0)
            comments_count = comments_counts.get(post_id, 0)
            shares_count = shares_counts.get(post_id, 0)
            collections_count = collections_counts.get(post_id, 0)
            rating_info = get_rating_info(db, post_id)
            
            post_with_stats = PostWithStats(
                id=post.id,
                title=post.title,
                content=post.content,
                author_id=post.author_id,
                created_at=post.created_at,
                updated_at=post.updated_at,
                images=post.images,
                author=post.author,
                likes_count=likes_count,
                comments_count=comments_count,
                shares_count=shares_count,
                collections_count=collections_count,
                rating_count=rating_info["count"],
                average_rating=rating_info["average"],
                visibility=post.visibility
            )
            
            posts_with_stats.append(post_with_stats)
            
            # 计算热度得分用于排序
            score = calculate_hot_score(
                likes_count=likes_count,
                comments_count=comments_count,
                shares_count=shares_count,
                ratings_count=rating_info["count"],
                average_rating=rating_info["average"] or 0
            )
            post_scores.append((post_with_stats, score))
        
        # 按热度得分排序
        post_scores.sort(key=lambda x: x[1], reverse=True)
        sorted_posts = [post for post, score in post_scores]
        
        return sorted_posts
    except Exception as e:
        logger.error(f"An unexpected error occurred: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")