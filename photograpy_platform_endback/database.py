from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, text, Float, or_, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import inspect
from datetime import datetime, timezone, timedelta
import json

# 使用SQLite数据库，实际项目中可以替换为PostgreSQL或MySQL
SQLALCHEMY_DATABASE_URL = "sqlite:///./forum.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 数据库模型
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    # 用户头像图片路径
    avatar_url = Column(String, default=None)
    # 用户个人主页背景图片路径
    background_url = Column(String, default=None)
    # 学号字段，唯一且不可变
    id_number = Column(String, unique=True, index=True)
    
    # 关系：一个用户可以有多篇帖子
    posts = relationship("Post", back_populates="author")
    # 关系：一个用户可以有多个评论
    comments = relationship("Comment", back_populates="author")
    # 关系：一个用户可以有多个点赞
    likes = relationship("Like", back_populates="user")
    # 关系：一个用户可以有多个分享
    shares = relationship("Share", back_populates="user")
    # 关系：一个用户可以有多个收藏夹
    collections = relationship("Collection", back_populates="user")
    # 关系：一个用户可以有多个收藏记录
    collection_items = relationship("CollectionItem", back_populates="user")
    # 关系：一个用户可以有多个评分
    ratings = relationship("Rating", back_populates="user")

class Post(Base):
    __tablename__ = "posts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))), onupdate=lambda: datetime.now(timezone(timedelta(hours=8))))
    images = Column(JSON, default=list)  # 存储图片路径列表
    # 帖子可见性设置: 
    # 0 - 全部人可见
    # 1 - 好友可见
    # 2 - 无时间限制
    # 3 - 三个月内可见
    # 4 - 一周内可见
    # 5 - 三天内可见
    visibility = Column(Integer, default=0)
    
    # 关系：一篇帖子属于一个用户
    author = relationship("User", back_populates="posts")
    # 关系：一篇帖子可以有多个评论
    comments = relationship("Comment", back_populates="post")
    # 关系：一篇帖子可以有多个点赞
    likes = relationship("Like", back_populates="post")
    # 关系：一篇帖子可以有多个分享
    shares = relationship("Share", back_populates="post")
    # 关系：一篇帖子可以被收藏到多个收藏夹
    collection_items = relationship("CollectionItem", back_populates="post")
    # 关系：一篇帖子可以有多个评分
    ratings = relationship("Rating", back_populates="post")

# 评论表
class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    # 关系
    author = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")

# 点赞表
class Like(Base):
    __tablename__ = "likes"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    # 关系
    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")

# 分享表
class Share(Base):
    __tablename__ = "shares"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    # 关系
    user = relationship("User", back_populates="shares")
    post = relationship("Post", back_populates="shares")

# 关注表
class Follow(Base):
    __tablename__ = "follows"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))  # 关注者
    following_id = Column(Integer, ForeignKey("users.id"))  # 被关注者
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    # 关系
    follower = relationship("User", foreign_keys=[follower_id])
    following = relationship("User", foreign_keys=[following_id])

# 收藏夹表
class Collection(Base):
    __tablename__ = "collections"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    is_default = Column(Boolean, default=False)  # 是否为系统默认收藏夹
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))), onupdate=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    # 关系
    user = relationship("User", back_populates="collections")
    collection_items = relationship("CollectionItem", back_populates="collection")

# 收藏记录表
class CollectionItem(Base):
    __tablename__ = "collection_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    collection_id = Column(Integer, ForeignKey("collections.id"))
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    # 关系
    user = relationship("User", back_populates="collection_items")
    post = relationship("Post", back_populates="collection_items")
    collection = relationship("Collection", back_populates="collection_items")

# 评分表
class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    post_id = Column(Integer, ForeignKey("posts.id"))
    score = Column(Float)  # 评分，0-10之间，支持一位小数
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))), onupdate=lambda: datetime.now(timezone(timedelta(hours=8))))
    
    # 关系
    user = relationship("User", back_populates="ratings")
    post = relationship("Post", back_populates="ratings")

# 私信表
class Message(Base):
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"))
    recipient_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone(timedelta(hours=8))))
    is_read = Column(Boolean, default=False)
    
    # 关系
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])

# 创建数据库表（如果表不存在则创建）

def migrate_database():
    # 检查并添加缺失的列
    try:
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        if 'posts' in table_names:
            # 获取posts表的列信息
            columns = [column['name'] for column in inspector.get_columns('posts')]
            
            # 如果images列不存在，则添加
            if 'images' not in columns:
                with engine.connect() as connection:
                    try:
                        # 使用 text() 包裹 SQL 语句以确保安全和兼容性
                        connection.execute(text("ALTER TABLE posts ADD COLUMN images JSON DEFAULT '[]'"))
                        connection.commit()
                        print("成功添加images列到posts表")
                    except Exception as e:
                        # 忽略列已存在的错误
                        print(f"添加images列时出错（可能已存在）: {e}")
    except Exception as e:
        print(f"数据库迁移过程中发生错误: {e}")

# 执行数据库迁移
migrate_database()

# 创建数据库表（如果表不存在则创建）
Base.metadata.create_all(bind=engine)