from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from fastapi import HTTPException
from passlib.context import CryptContext

from database import (
    User as DBUser,
    Post as DBPost,
    Comment as DBComment,
    Like as DBLike,
    Share as DBShare,
    Follow as DBFollow,
    Collection as DBCollection,
    CollectionItem as DBCollectionItem,
    Rating as DBRating,
    Message as DBMessage
)
from models import UserCreate, PostCreate, PostUpdate, CommentCreate, LikeCreate, ShareCreate, FollowCreate, CollectionCreate, CollectionUpdate, CollectionItemCreate, RatingCreate, MessageCreate, UserUpdate, UserLogin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user(db: Session, user_id: int):
    return db.query(DBUser).filter(DBUser.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(DBUser).filter(DBUser.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(DBUser).filter(DBUser.email == email).first()

def get_user_by_id_number(db: Session, id_number: str):
    return db.query(DBUser).filter(DBUser.id_number == id_number).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DBUser).offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    # 检查学号是否已存在
    existing_user = get_user_by_id_number(db, user.id_number)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="该学号已被注册"
        )
    
    hashed_password = pwd_context.hash(user.password)
    db_user = DBUser(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        id_number=user.id_number
    )
    db.add(db_user)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: int, user_update: UserUpdate):
    """
    更新用户信息（头像、背景图片等）
    
    Args:
        db (Session): 数据库会话
        user_id (int): 用户ID
        user_update (UserUpdate): 用户更新信息
        
    Returns:
        DBUser: 更新后的用户对象
    """
    db_user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    # 更新用户信息
    if user_update.avatar_url is not None:
        db_user.avatar_url = user_update.avatar_url
    if user_update.background_url is not None:
        db_user.background_url = user_update.background_url
    
    try:
        db.commit()
        db.refresh(db_user)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return db_user

def authenticate_user(db: Session, user_login: UserLogin):
    user = get_user_by_id_number(db, user_login.id_number)
    if not user:
        return False
    if not pwd_context.verify(user_login.password, user.hashed_password):
        return False
    return user

def reset_user_password(db: Session, id_number: str, new_password: str):
    """
    重置用户密码
    
    Args:
        db (Session): 数据库会话
        id_number (str): 学号
        new_password (str): 新密码
        
    Returns:
        bool: 是否成功重置密码
    """
    user = get_user_by_id_number(db, id_number)
    if not user:
        return False
    
    hashed_password = pwd_context.hash(new_password)
    user.hashed_password = hashed_password
    
    try:
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def get_posts(db: Session, skip: int = 0, limit: int = 100):
    return db.query(DBPost).order_by(DBPost.created_at.desc()).offset(skip).limit(limit).all()

def get_posts_by_author(db: Session, author_id: int, skip: int = 0, limit: int = 100):
    return db.query(DBPost).filter(DBPost.author_id == author_id).offset(skip).limit(limit).all()

def get_post(db: Session, post_id: int):
    return db.query(DBPost).filter(DBPost.id == post_id).first()

def create_post(db: Session, post: PostCreate, author_id: int):
    db_post = DBPost(
        title=post.title,
        content=post.content,
        author_id=author_id,
        images=post.images if post.images is not None else []
    )
    db.add(db_post)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    db.refresh(db_post)
    return db_post

def update_post(db: Session, post_id: int, post_update: PostUpdate):
    db_post = db.query(DBPost).filter(DBPost.id == post_id).first()
    if not db_post:
        return None
    
    if post_update.title is not None:
        db_post.title = post_update.title
    if post_update.content is not None:
        db_post.content = post_update.content
    if post_update.images is not None:
        db_post.images = post_update.images
    if post_update.visibility is not None:
        db_post.visibility = post_update.visibility
    
    try:
        db.commit()
        db.refresh(db_post)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return db_post

def delete_post(db: Session, post_id: int):
    db_post = get_post(db, post_id=post_id)
    if db_post:
        db.delete(db_post)
        db.commit()
    return db_post

# 评论相关操作
def get_comments_by_post(db: Session, post_id: int, skip: int = 0, limit: int = 100):
    return db.query(DBComment).filter(DBComment.post_id == post_id).offset(skip).limit(limit).all()

def get_comments_counts(db: Session, post_ids: List[int]) -> Dict[int, int]:
    """批量获取帖子的评论数"""
    if not post_ids:
        return {}
    
    result = db.query(DBComment.post_id, func.count(DBComment.id).label('count'))\
               .filter(DBComment.post_id.in_(post_ids))\
               .group_by(DBComment.post_id).all()
    
    return {post_id: count for post_id, count in result}

def get_comments_count(db: Session, post_id: int) -> int:
    """获取单个帖子的评论数"""
    result = db.query(func.count(DBComment.id)).filter(DBComment.post_id == post_id).scalar()
    return result or 0

def get_comment(db: Session, comment_id: int):
    """根据评论ID获取评论"""
    return db.query(DBComment).filter(DBComment.id == comment_id).first()

def create_comment(db: Session, comment: CommentCreate, author_id: int):
    db_comment = DBComment(
        content=comment.content,
        post_id=comment.post_id,
        author_id=author_id
    )
    db.add(db_comment)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    db.refresh(db_comment)
    return db_comment

def delete_comment(db: Session, comment_id: int):
    db_comment = db.query(DBComment).filter(DBComment.id == comment_id).first()
    if db_comment:
        db.delete(db_comment)
        db.commit()
    return db_comment

# 点赞相关操作
def get_like(db: Session, user_id: int, post_id: int):
    return db.query(DBLike).filter(DBLike.user_id == user_id, DBLike.post_id == post_id).first()

def create_like(db: Session, like: LikeCreate, user_id: int):
    # 检查是否已经点赞
    existing_like = get_like(db, user_id, like.post_id)
    if existing_like:
        return existing_like
    
    db_like = DBLike(
        post_id=like.post_id,
        user_id=user_id
    )
    db.add(db_like)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    db.refresh(db_like)
    return db_like

def delete_like(db: Session, user_id: int, post_id: int):
    db_like = get_like(db, user_id, post_id)
    if db_like:
        db.delete(db_like)
        db.commit()
    return db_like

def get_likes_count(db: Session, post_id: int):
    return db.query(DBLike).filter(DBLike.post_id == post_id).count()

def get_likes_counts(db: Session, post_ids: List[int]) -> Dict[int, int]:
    """批量获取帖子的点赞数"""
    if not post_ids:
        return {}
    
    result = db.query(DBLike.post_id, func.count(DBLike.id).label('count'))\
               .filter(DBLike.post_id.in_(post_ids))\
               .group_by(DBLike.post_id).all()
    
    return {post_id: count for post_id, count in result}

# 分享相关操作
def get_share(db: Session, user_id: int, post_id: int):
    return db.query(DBShare).filter(DBShare.user_id == user_id, DBShare.post_id == post_id).first()

def create_share(db: Session, share: ShareCreate, user_id: int):
    # 检查是否已经分享
    existing_share = get_share(db, user_id, share.post_id)
    if existing_share:
        return existing_share
    
    db_share = DBShare(
        post_id=share.post_id,
        user_id=user_id
    )
    db.add(db_share)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    db.refresh(db_share)
    return db_share

def delete_share(db: Session, user_id: int, post_id: int):
    db_share = get_share(db, user_id, post_id)
    if db_share:
        db.delete(db_share)
        db.commit()
    return db_share

def get_shares_count(db: Session, post_id: int):
    return db.query(DBShare).filter(DBShare.post_id == post_id).count()

def get_shares_counts(db: Session, post_ids: List[int]) -> Dict[int, int]:
    """批量获取帖子的分享数"""
    if not post_ids:
        return {}
    
    result = db.query(DBShare.post_id, func.count(DBShare.id).label('count'))\
               .filter(DBShare.post_id.in_(post_ids))\
               .group_by(DBShare.post_id).all()
    
    return {post_id: count for post_id, count in result}

# 关注相关操作
def get_follow(db: Session, follower_id: int, following_id: int):
    return db.query(DBFollow).filter(DBFollow.follower_id == follower_id, DBFollow.following_id == following_id).first()

def create_follow(db: Session, follow: FollowCreate, follower_id: int):
    # 检查是否已经关注
    existing_follow = get_follow(db, follower_id, follow.following_id)
    if existing_follow:
        return existing_follow
    
    # 不能关注自己
    if follower_id == follow.following_id:
        raise HTTPException(status_code=400, detail="不能关注自己")
    
    db_follow = DBFollow(
        follower_id=follower_id,
        following_id=follow.following_id
    )
    db.add(db_follow)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    db.refresh(db_follow)
    return db_follow

def delete_follow(db: Session, follower_id: int, following_id: int):
    db_follow = get_follow(db, follower_id, following_id)
    if db_follow:
        db.delete(db_follow)
        db.commit()
    return db_follow

def get_followers_count(db: Session, user_id: int):
    return db.query(DBFollow).filter(DBFollow.following_id == user_id).count()

def get_following_count(db: Session, user_id: int):
    return db.query(DBFollow).filter(DBFollow.follower_id == user_id).count()

# 获取用户收到的总点赞数
def get_user_total_likes_received(db: Session, user_id: int):
    # 通过用户帖子获得的点赞数
    return db.query(func.count(DBLike.id)).join(DBPost).filter(DBPost.author_id == user_id).scalar()

# 获取帖子的统计信息
def get_post_with_stats(db: Session, post_id: int):
    post = get_post(db, post_id)
    if not post:
        return None
    
    likes_count = get_likes_count(db, post_id)
    comments_count = len(get_comments_by_post(db, post_id))
    shares_count = get_shares_count(db, post_id)
    collections_count = get_collections_count(db, post_id)
    rating_info = get_rating_info(db, post_id)
    
    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "author_id": post.author_id,
        "created_at": post.created_at,
        "updated_at": post.updated_at,
        "images": post.images,
        "visibility": post.visibility,
        "author": post.author,
        "likes_count": likes_count,
        "comments_count": comments_count,
        "shares_count": shares_count,
        "collections_count": collections_count,
        "rating_count": rating_info["count"],
        "average_rating": rating_info["average"]
    }

# 收藏夹相关操作
def get_collection(db: Session, collection_id: int):
    return db.query(DBCollection).filter(DBCollection.id == collection_id).first()

def get_collections_by_user(db: Session, user_id: int):
    return db.query(DBCollection).filter(DBCollection.user_id == user_id).all()

def get_default_collection(db: Session, user_id: int):
    return db.query(DBCollection).filter(DBCollection.user_id == user_id, DBCollection.is_default == True).first()

def create_default_collection(db: Session, user_id: int):
    db_collection = DBCollection(
        name="默认收藏夹",
        user_id=user_id,
        is_default=True
    )
    db.add(db_collection)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    db.refresh(db_collection)
    return db_collection

def create_collection(db: Session, collection: CollectionCreate, user_id: int):
    db_collection = DBCollection(
        name=collection.name,
        user_id=user_id,
        is_default=False
    )
    db.add(db_collection)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    db.refresh(db_collection)
    return db_collection

def update_collection(db: Session, collection_id: int, collection_update: CollectionUpdate):
    db_collection = db.query(DBCollection).filter(DBCollection.id == collection_id).first()
    if not db_collection:
        raise HTTPException(status_code=404, detail="收藏夹不存在")
    
    db_collection.name = collection_update.name
    db_collection.updated_at = func.now()
    
    try:
        db.commit()
        db.refresh(db_collection)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return db_collection

def delete_collection(db: Session, collection_id: int):
    db_collection = db.query(DBCollection).filter(DBCollection.id == collection_id).first()
    if not db_collection:
        raise HTTPException(status_code=404, detail="收藏夹不存在")
    
    # 删除收藏夹中的所有收藏记录
    db.query(DBCollectionItem).filter(DBCollectionItem.collection_id == collection_id).delete()
    
    db.delete(db_collection)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return db_collection

# 收藏记录相关操作
def get_collection_item(db: Session, user_id: int, post_id: int, collection_id: int):
    return db.query(DBCollectionItem).filter(
        DBCollectionItem.user_id == user_id,
        DBCollectionItem.post_id == post_id,
        DBCollectionItem.collection_id == collection_id
    ).first()

def get_collection_items_by_collection(db: Session, collection_id: int, skip: int = 0, limit: int = 100):
    return db.query(DBCollectionItem).filter(DBCollectionItem.collection_id == collection_id).offset(skip).limit(limit).all()

def create_collection_item(db: Session, collection_item: CollectionItemCreate, user_id: int):
    # 检查帖子是否存在
    post = get_post(db, collection_item.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    # 不能收藏自己的帖子
    if post.author_id == user_id:
        raise HTTPException(status_code=400, detail="不能收藏自己的帖子")
    
    # 获取用户收藏夹
    collections = get_collections_by_user(db, user_id)
    
    # 如果没有收藏夹，创建默认收藏夹
    if not collections:
        collection = create_default_collection(db, user_id)
    else:
        # 查找默认收藏夹
        collection = next((c for c in collections if c.is_default), None)
        # 如果没有默认收藏夹，使用第一个收藏夹
        if not collection:
            collection = collections[0]
    
    # 检查是否已经在该收藏夹中
    existing_item = get_collection_item(db, user_id, collection_item.post_id, collection.id)
    if existing_item:
        return existing_item
    
    db_collection_item = DBCollectionItem(
        post_id=collection_item.post_id,
        user_id=user_id,
        collection_id=collection.id
    )
    db.add(db_collection_item)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    db.refresh(db_collection_item)
    return db_collection_item

def delete_collection_item(db: Session, collection_item_id: int):
    db_collection_item = db.query(DBCollectionItem).filter(DBCollectionItem.id == collection_item_id).first()
    if db_collection_item:
        db.delete(db_collection_item)
        db.commit()
    return db_collection_item

def get_collection_items_with_post_by_collection(db: Session, collection_id: int, skip: int = 0, limit: int = 100):
    return db.query(DBCollectionItem).filter(DBCollectionItem.collection_id == collection_id).offset(skip).limit(limit).all()

def get_collections_count(db: Session, post_id: int) -> int:
    """获取单个帖子的收藏数"""
    return db.query(DBCollectionItem).filter(DBCollectionItem.post_id == post_id).count()

def get_collections_counts(db: Session, post_ids: List[int]) -> Dict[int, int]:
    """批量获取帖子的收藏数"""
    if not post_ids:
        return {}
    
    result = db.query(DBCollectionItem.post_id, func.count(DBCollectionItem.id).label('count'))\
               .filter(DBCollectionItem.post_id.in_(post_ids))\
               .group_by(DBCollectionItem.post_id).all()
    
    return {post_id: count for post_id, count in result}

# 评分相关操作
def get_rating(db: Session, user_id: int, post_id: int):
    """获取用户对帖子的评分"""
    return db.query(DBRating).filter(DBRating.user_id == user_id, DBRating.post_id == post_id).first()

def create_rating(db: Session, rating: RatingCreate, user_id: int):
    """创建评分"""
    # 检查是否已经评分
    existing_rating = get_rating(db, user_id, rating.post_id)
    if existing_rating:
        raise HTTPException(status_code=400, detail="您已经对此帖子评过分了")
    
    # 检查帖子是否存在
    post = get_post(db, rating.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="帖子不存在")
    
    # 不能给自己评分
    if post.author_id == user_id:
        raise HTTPException(status_code=400, detail="不能给自己发布的帖子评分")
    
    db_rating = DBRating(
        post_id=rating.post_id,
        user_id=user_id,
        score=rating.score
    )
    db.add(db_rating)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    db.refresh(db_rating)
    return db_rating

def update_rating(db: Session, post_id: int, user_id: int, rating_update: RatingCreate):
    """更新评分"""
    db_rating = get_rating(db, user_id, post_id)
    if not db_rating:
        raise HTTPException(status_code=404, detail="评分记录不存在")
    
    db_rating.score = rating_update.score
    db_rating.updated_at = func.now()
    
    try:
        db.commit()
        db.refresh(db_rating)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return db_rating

def delete_rating(db: Session, post_id: int, user_id: int):
    """删除评分"""
    db_rating = get_rating(db, user_id, post_id)
    if not db_rating:
        raise HTTPException(status_code=404, detail="评分记录不存在")
    
    db.delete(db_rating)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    return db_rating

def get_rating_info(db: Session, post_id: int):
    """获取帖子的评分信息（评分人数和平均分）"""
    # 获取评分人数
    count = db.query(DBRating).filter(DBRating.post_id == post_id).count()
    
    # 如果没有评分，返回默认值
    if count == 0:
        return {"count": 0, "average": None}
    
    # 计算平均分，保留一位小数
    average = db.query(func.avg(DBRating.score)).filter(DBRating.post_id == post_id).scalar()
    if average is not None:
        average = round(float(average), 1)
    
    return {"count": count, "average": average}

def get_ratings_counts(db: Session, post_ids: List[int]) -> Dict[int, int]:
    """批量获取帖子的评分人数"""
    if not post_ids:
        return {}
    
    result = db.query(DBRating.post_id, func.count(DBRating.id).label('count'))\
               .filter(DBRating.post_id.in_(post_ids))\
               .group_by(DBRating.post_id).all()
    
    return {post_id: count for post_id, count in result}

def get_average_ratings(db: Session, post_ids: List[int]) -> Dict[int, Optional[float]]:
    """批量获取帖子的平均评分"""
    if not post_ids:
        return {}
    
    result = db.query(DBRating.post_id, func.avg(DBRating.score).label('average'))\
               .filter(DBRating.post_id.in_(post_ids))\
               .group_by(DBRating.post_id).all()
    
    return {post_id: round(float(avg), 1) if avg is not None else None for post_id, avg in result}

def get_ratings_info(db: Session, post_ids: List[int]) -> Dict[int, Dict[str, any]]:
    """
    批量获取帖子的评分信息（评分人数和平均分）
    
    Args:
        db (Session): 数据库会话
        post_ids (List[int]): 帖子ID列表
        
    Returns:
        Dict[int, Dict[str, any]]: 每个帖子的评分信息，包括count（评分人数）和average（平均分）
    """
    if not post_ids:
        return {}
    
    # 获取评分人数
    ratings_counts = get_ratings_counts(db, post_ids)
    
    # 获取平均分
    average_ratings = get_average_ratings(db, post_ids)
    
    # 组合结果
    ratings_info = {}
    for post_id in post_ids:
        ratings_info[post_id] = {
            "count": ratings_counts.get(post_id, 0),
            "average": average_ratings.get(post_id)
        }
    
    return ratings_info

def get_posts_with_stats(db: Session, skip: int = 0, limit: int = 100):
    """
    获取帖子列表及其统计信息
    
    Args:
        db (Session): 数据库会话
        skip (int): 跳过的记录数
        limit (int): 限制返回记录数
        
    Returns:
        List[Dict]: 帖子列表，每个帖子包含统计信息
    """
    posts = get_posts(db, skip=skip, limit=limit)
    if not posts:
        return []
    
    # 获取所有帖子的ID
    post_ids = [post.id for post in posts]
    
    # 批量获取统计信息
    likes_counts = get_likes_counts(db, post_ids)
    comments_counts = get_comments_counts(db, post_ids)
    shares_counts = get_shares_counts(db, post_ids)
    collections_counts = get_collections_counts(db, post_ids)
    ratings_counts = get_ratings_counts(db, post_ids)
    average_ratings = get_average_ratings(db, post_ids)
    
    # 组合数据
    posts_with_stats = []
    for post in posts:
        post_id = post.id
        post_with_stats = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "author_id": post.author_id,
            "created_at": post.created_at,
            "updated_at": post.updated_at,
            "images": post.images,
            "visibility": post.visibility,
            "author": post.author,
            "likes_count": likes_counts.get(post_id, 0),
            "comments_count": comments_counts.get(post_id, 0),
            "shares_count": shares_counts.get(post_id, 0),
            "collections_count": collections_counts.get(post_id, 0),
            "rating_count": ratings_counts.get(post_id, 0),
            "average_rating": average_ratings.get(post_id)
        }
        posts_with_stats.append(post_with_stats)
    
    return posts_with_stats

def search_posts(db: Session, query: str, skip: int = 0, limit: int = 100):
    """
    根据标题搜索帖子，并按热度排序
    
    Args:
        db (Session): 数据库会话
        query (str): 搜索关键词
        skip (int): 跳过的记录数
        limit (int): 限制返回记录数
        
    Returns:
        List[DBPost]: 搜索到的帖子列表
    """
    # 根据标题搜索帖子
    posts = db.query(DBPost).filter(DBPost.title.contains(query)).offset(skip).limit(limit).all()
    
    return posts

def calculate_hot_score(likes_count: int, comments_count: int, shares_count: int, ratings_count: int, average_rating: float) -> float:
    """
    计算帖子热度得分
    
    Args:
        likes_count (int): 点赞数
        comments_count (int): 评论数
        shares_count (int): 分享数
        ratings_count (int): 评分人数
        average_rating (float): 平均评分
        
    Returns:
        float: 热度得分
    """
    # 计算热度得分 (加权平均)
    # 权重: 点赞(30%), 评论(25%), 分享(25%), 评分(20%)
    score = (
        likes_count * 0.3 +
        comments_count * 0.25 +
        shares_count * 0.25 +
        (average_rating * ratings_count * 0.2) if average_rating else 0
    )
    
    return score

# 排行榜相关操作
def get_hot_posts(db: Session, period: str = "week", limit: int = 10):
    """
    获取热门帖子排行榜
    
    Args:
        period (str): 时间周期 ("week", "month", "year")
        limit (int): 返回帖子数量限制
        
    Returns:
        List[DBPost]: 热门帖子列表，按热度得分排序
    """
    # 计算时间范围
    now = datetime.now()
    if period == "week":
        start_date = now - timedelta(days=7)
    elif period == "month":
        start_date = now - timedelta(days=30)
    elif period == "year":
        start_date = now - timedelta(days=365)
    else:
        start_date = now - timedelta(days=7)  # 默认为周榜
    
    # 查询在指定时间范围内创建的帖子
    posts = db.query(DBPost).filter(DBPost.created_at >= start_date).all()
    
    if not posts:
        return []
    
    # 获取帖子ID列表
    post_ids = [post.id for post in posts]
    
    # 批量获取统计数据
    likes_counts = get_likes_counts(db, post_ids)
    comments_counts = get_comments_counts(db, post_ids)
    shares_counts = get_shares_counts(db, post_ids)
    ratings_counts = get_ratings_counts(db, post_ids)
    average_ratings = get_average_ratings(db, post_ids)
    
    # 计算每个帖子的热度得分
    post_scores = []
    for post in posts:
        post_id = post.id
        likes_count = likes_counts.get(post_id, 0)
        comments_count = comments_counts.get(post_id, 0)
        shares_count = shares_counts.get(post_id, 0)
        ratings_count = ratings_counts.get(post_id, 0)
        average_rating = average_ratings.get(post_id, 0)
        
        # 计算热度得分 (加权平均)
        # 权重: 点赞(30%), 评论(25%), 分享(25%), 评分(20%)
        score = (
            likes_count * 0.3 +
            comments_count * 0.25 +
            shares_count * 0.25 +
            (average_rating * ratings_count * 0.2) if average_rating else 0
        )
        
        post_scores.append((post, score))
    
    # 按得分排序并返回前N个
    post_scores.sort(key=lambda x: x[1], reverse=True)
    return [post for post, score in post_scores[:limit]]

def create_message(db: Session, message: MessageCreate, sender_id: int):
    """
    创建私信消息
    
    Args:
        db (Session): 数据库会话
        message (MessageCreate): 消息创建信息
        sender_id (int): 发送者ID
        
    Returns:
        DBMessage: 创建的消息对象
    """
    db_message = DBMessage(
        sender_id=sender_id,
        recipient_id=message.recipient_id,
        content=message.content,
        image_url=message.image_url
    )
    db.add(db_message)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    db.refresh(db_message)
    return db_message

def get_messages_between_users(db: Session, user1_id: int, user2_id: int, skip: int = 0, limit: int = 100):
    """
    获取两个用户之间的消息记录
    
    Args:
        db (Session): 数据库会话
        user1_id (int): 用户1 ID
        user2_id (int): 用户2 ID
        skip (int): 跳过的记录数
        limit (int): 限制返回的记录数
        
    Returns:
        List[DBMessage]: 消息列表
    """
    messages = db.query(DBMessage).filter(
        or_(
            and_(DBMessage.sender_id == user1_id, DBMessage.recipient_id == user2_id),
            and_(DBMessage.sender_id == user2_id, DBMessage.recipient_id == user1_id)
        )
    ).order_by(DBMessage.created_at).offset(skip).limit(limit).all()
    
    return messages

def get_user_messages(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    """
    获取用户参与的所有消息记录（按对话分组）
    
    Args:
        db (Session): 数据库会话
        user_id (int): 用户ID
        skip (int): 跳过的记录数
        limit (int): 限制返回的记录数
        
    Returns:
        List[DBMessage]: 消息列表
    """
    messages = db.query(DBMessage).filter(
        or_(DBMessage.sender_id == user_id, DBMessage.recipient_id == user_id)
    ).order_by(DBMessage.created_at.desc()).offset(skip).limit(limit).all()
    
    return messages
