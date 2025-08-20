from sqlalchemy.orm import Session
from database import SessionLocal, User as DBUser
from fastapi import Depends, HTTPException, status
from typing import Optional

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(
    user_id: int, 
    db: Session = Depends(get_db)
) -> DBUser:
    """
    获取当前登录用户
    通过HTTP头部传递的user_id参数获取当前用户
    """
    # 不再提供默认用户ID，强制要求提供user_id参数
    
    user = db.query(DBUser).filter(DBUser.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="未找到指定的用户")
    return user