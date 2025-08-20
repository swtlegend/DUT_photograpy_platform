from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Path
from sqlalchemy.orm import Session
from typing import List
import os
import shutil
from datetime import datetime

from crud import create_message, get_messages_between_users, get_user_messages
from models import MessageCreate, MessageWithUserInfo
from database import Message
from dependencies import get_db, get_current_user
from database import User as DBUser

router = APIRouter()

UPLOAD_DIRECTORY = "./uploaded_images/messages"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@router.post("/", response_model=MessageWithUserInfo)
def send_message(
    message: MessageCreate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    发送私信消息
    
    Args:
        message: 消息内容
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        MessageWithUserInfo: 创建的消息
    """
    # 检查不能给自己发消息
    if message.recipient_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能给自己发送消息")
    
    # 创建消息
    db_message = create_message(db, message, current_user.id)
    return db_message

@router.post("/upload-image", response_model=dict)
async def upload_message_image(
    file: UploadFile = File(...),
    current_user: DBUser = Depends(get_current_user)
):
    """
    上传私信图片
    
    Args:
        file: 上传的图片文件
        current_user: 当前登录用户
        
    Returns:
        dict: 图片URL
    """
    # 检查文件类型
    allowed_extensions = ["jpg", "jpeg", "png"]
    file_extension = file.filename.split(".")[-1].lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="不支持的文件格式，仅支持jpg、jpeg、png格式")
    
    # 生成唯一的文件名
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    file_extension = os.path.splitext(file.filename)[1]
    new_filename = f"msg_{current_user.id}_{timestamp}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, new_filename)
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 返回文件URL
    file_url = f"/images/messages/{new_filename}"
    return {"image_url": file_url}

@router.get("/conversation/{user_id}", response_model=List[MessageWithUserInfo])
def get_conversation(
    user_id: int = Path(...),
    skip: int = 0,
    limit: int = 50,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取与指定用户的对话记录
    
    Args:
        user_id: 对方用户ID
        skip: 跳过的记录数
        limit: 限制返回的记录数
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        List[MessageWithUserInfo]: 对话记录列表
    """
    messages = get_messages_between_users(db, current_user.id, user_id, skip, limit)
    return messages

@router.get("/", response_model=List[MessageWithUserInfo])
def get_my_messages(
    skip: int = 0,
    limit: int = 50,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取我的所有消息记录
    
    Args:
        skip: 跳过的记录数
        limit: 限制返回的记录数
        current_user: 当前登录用户
        db: 数据库会话
        
    Returns:
        List[MessageWithUserInfo]: 消息记录列表
    """
    messages = get_user_messages(db, current_user.id, skip, limit)
    return messages