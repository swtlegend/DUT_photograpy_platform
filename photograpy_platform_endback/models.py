from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, List
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from passlib.context import CryptContext

# 帖子可见性选项
VISIBILITY_OPTIONS = {
    0: "全部人可见",
    1: "好友可见",
    2: "无时间限制",
    3: "三个月内可见",
    4: "一周内可见",
    5: "三天内可见"
}

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    id_number = Column(String(20), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 新增字段用于存储头像和背景图URL
    avatar_url = Column(String(255), default=None)
    background_url = Column(String(255), default=None)
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

class UserBase(BaseModel):
    username: str
    email: str
    id_number: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    id_number: str
    confirm_password: str

    @field_validator('confirm_password')
    @classmethod
    def passwords_match(cls, v: str, info) -> str:
        # 在Pydantic v2中，我们需要通过info.data访问其他字段的值
        if 'password' in info.data and v != info.data['password']:
            raise ValueError('密码和确认密码不一致')
        return v

class User(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool
    id_number: str
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    id_number: str
    password: str

class ForgotPasswordRequest(BaseModel):
    id_number: str

class ResetPasswordRequest(BaseModel):
    id_number: str
    new_password: str

class UserUpdate(BaseModel):
    """用户更新信息模型"""
    avatar_url: Optional[str] = None
    background_url: Optional[str] = None

class UserProfile(User):
    """用户个人资料模型，包含头像和背景图片"""
    avatar_url: Optional[str] = None
    background_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    images: Optional[List[str]] = None

class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    images: Optional[List[str]] = None
    visibility: Optional[int] = None  # 帖子可见性设置

class Post(PostBase):
    id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    images: Optional[List[str]] = None
    visibility: int = 0  # 默认全部人可见
    
    class Config:
        from_attributes = True

class PostWithAuthor(Post):
    author: User
    
    class Config:
        from_attributes = True

class PostWithStats(PostWithAuthor):
    likes_count: int = 0
    comments_count: int = 0
    shares_count: int = 0
    collections_count: int = 0
    rating_count: int = 0
    average_rating: Optional[float] = None
    images: Optional[List[str]] = None  # 添加图片字段
    
    class Config:
        from_attributes = True

# 评论相关模型
class CommentBase(BaseModel):
    content: str

class CommentCreate(CommentBase):
    post_id: int

class Comment(CommentBase):
    id: int
    author_id: int
    post_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CommentWithAuthor(Comment):
    author: User
    
    class Config:
        from_attributes = True

# 点赞相关模型
class LikeBase(BaseModel):
    post_id: int

class LikeCreate(LikeBase):
    pass

class Like(LikeBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 分享相关模型
class ShareBase(BaseModel):
    post_id: int

class ShareCreate(ShareBase):
    pass

class Share(ShareBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 关注相关模型
class FollowBase(BaseModel):
    following_id: int

class FollowCreate(FollowBase):
    pass

class Follow(FollowBase):
    id: int
    follower_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# 用户统计信息模型
class UserStats(BaseModel):
    followers_count: int = 0
    following_count: int = 0
    posts_count: int = 0
    likes_received: int = 0

# 用户个人中心模型
class UserProfile(User):
    stats: UserStats

# 收藏夹相关模型
class CollectionBase(BaseModel):
    name: str

class CollectionCreate(CollectionBase):
    pass

class CollectionUpdate(BaseModel):
    name: str

class Collection(CollectionBase):
    id: int
    user_id: int
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# 收藏记录相关模型
class CollectionItemBase(BaseModel):
    post_id: int
    collection_id: int

class CollectionItemCreate(BaseModel):
    post_id: int

class CollectionItem(CollectionItemBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class CollectionItemWithPost(CollectionItem):
    post: PostWithAuthor
    
    class Config:
        from_attributes = True

# 评分相关模型
class RatingBase(BaseModel):
    score: float = Field(..., ge=0, le=10, description="评分，范围0-10，支持一位小数")

    @field_validator('score')
    @classmethod
    def score_must_be_valid(cls, v: float) -> float:
        # 确保最多只有一位小数
        if round(v, 1) != v:
            raise ValueError('评分最多只能有一位小数')
        return v

class RatingCreate(RatingBase):
    post_id: int

class Rating(RatingBase):
    id: int
    user_id: int
    post_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class RatingWithUser(Rating):
    user: User
    
    class Config:
        from_attributes = True

# 私信相关模型
class MessageBase(BaseModel):
    recipient_id: int
    content: str
    image_url: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class Message(MessageBase):
    id: int
    sender_id: int
    created_at: datetime
    is_read: bool
    
    class Config:
        from_attributes = True

class MessageWithUsers(Message):
    sender: User
    recipient: User
    
    class Config:
        from_attributes = True

class MessageWithUserInfo(Message):
    sender: User
    
    class Config:
        from_attributes = True
