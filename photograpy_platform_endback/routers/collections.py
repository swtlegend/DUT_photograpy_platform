from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models import CollectionCreate, CollectionUpdate, Collection, CollectionItemCreate, CollectionItem, CollectionItemWithPost
from dependencies import get_db
from crud import (
    get_collections_by_user, 
    get_default_collection, 
    create_collection, 
    update_collection, 
    delete_collection,
    create_collection_item,
    get_collection_items_with_post_by_collection,
    delete_collection_item,
    get_collection
)
from dependencies import get_current_user
from database import User as DBUser

router = APIRouter(tags=["collections"])

@router.get("/", response_model=List[Collection])
def read_collections(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    获取当前用户的所有收藏夹
    
    Args:
        skip (int): 跳过的记录数，用于分页，默认为0
        limit (int): 返回的最大记录数，用于分页，默认为100
        db (Session): 数据库会话对象，通过依赖注入获取
        current_user (DBUser): 当前认证用户对象，通过依赖注入获取
        
    Returns:
        List[Collection]: 用户的收藏夹列表
    """
    collections = get_collections_by_user(db, current_user.id)
    return collections

@router.post("/", response_model=Collection)
def create_collection_endpoint(
    collection: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    创建新的收藏夹
    
    Args:
        collection (CollectionCreate): 收藏夹创建请求数据，包含收藏夹名称等信息
        db (Session): 数据库会话对象，通过依赖注入自动获取
        current_user (DBUser): 当前认证用户对象，通过依赖注入自动获取
        
    Returns:
        Collection: 创建成功的收藏夹对象，包含收藏夹的完整信息
    """
    return create_collection(db, collection, current_user.id)

@router.put("/{collection_id}", response_model=Collection)
def update_collection_endpoint(
    collection_id: int,
    collection_update: CollectionUpdate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    更新收藏夹信息（重命名）
    
    Args:
        collection_id (int): 收藏夹ID
        collection_update (CollectionUpdate): 收藏夹更新数据，包含新的名称
        db (Session): 数据库会话对象，通过依赖注入获取
        current_user (DBUser): 当前认证用户对象，通过依赖注入获取
        
    Returns:
        Collection: 更新后的收藏夹对象
        
    Raises:
        HTTPException: 当收藏夹不存在或用户无权限操作时抛出异常
    """
    # 验证收藏夹所有权
    db_collection = get_collection(db, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="收藏夹不存在")
    
    if db_collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限操作此收藏夹")
    
    return update_collection(db, collection_id, collection_update)

@router.delete("/{collection_id}", response_model=Collection)
def delete_collection_endpoint(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    删除收藏夹
    """
    # 检查收藏夹是否属于当前用户
    db_collection = get_collection(db, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="收藏夹不存在")
    
    if db_collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限操作此收藏夹")
    
    return delete_collection(db, collection_id)

@router.post("/{collection_id}/items/", response_model=CollectionItem)
def add_post_to_collection(
    collection_id: int,
    collection_item: CollectionItemCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    将帖子添加到指定收藏夹
    
    Args:
        collection_id (int): 收藏夹ID
        collection_item (CollectionItemCreate): 收藏项创建数据，包含要收藏的帖子信息
        db (Session): 数据库会话对象，通过依赖注入获取
        current_user (DBUser): 当前认证用户对象，通过依赖注入获取
        
    Returns:
        CollectionItem: 创建成功的收藏项对象
        
    Raises:
        HTTPException: 当收藏夹不存在或用户无权限操作时抛出异常
    """
    # 检查收藏夹是否属于当前用户
    db_collection = get_collection(db, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="收藏夹不存在")
    
    if db_collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限操作此收藏夹")
    
    return create_collection_item(db, collection_item, current_user.id)

@router.get("/{collection_id}/items/", response_model=List[CollectionItemWithPost])
def read_collection_items(
    collection_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    获取指定收藏夹中的所有收藏项
    
    Args:
        collection_id (int): 收藏夹ID
        skip (int): 跳过的记录数，用于分页，默认为0
        limit (int): 返回的最大记录数，用于分页，默认为100
        db (Session): 数据库会话对象，通过依赖注入获取
        current_user (DBUser): 当前认证用户对象，通过依赖注入获取
        
    Returns:
        List[CollectionItemWithPost]: 收藏项列表，每个项包含帖子的完整信息
        
    Raises:
        HTTPException: 当收藏夹不存在或用户无权限操作时抛出异常
    """
    # 检查收藏夹是否属于当前用户
    db_collection = get_collection(db, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="收藏夹不存在")
    
    if db_collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限操作此收藏夹")
    
    items = get_collection_items_with_post_by_collection(db, collection_id, skip, limit)
    return items

@router.delete("/{collection_id}/items/{item_id}", response_model=CollectionItem)
def remove_post_from_collection(
    collection_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    从收藏夹中移除帖子
    
    Args:
        collection_id (int): 收藏夹ID
        item_id (int): 收藏项ID
        db (Session): 数据库会话对象，通过依赖注入获取
        current_user (DBUser): 当前认证用户对象，通过依赖注入获取
        
    Returns:
        CollectionItem: 被删除的收藏项对象
        
    Raises:
        HTTPException: 当收藏夹不存在或用户无权限操作时抛出异常
    """
    # 检查收藏夹是否属于当前用户
    db_collection = get_collection(db, collection_id)
    if not db_collection:
        raise HTTPException(status_code=404, detail="收藏夹不存在")
    
    if db_collection.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权限操作此收藏夹")
    
    return delete_collection_item(db, item_id)

@router.post("/items/", response_model=CollectionItem)
def collect_post(
    collection_item: CollectionItemCreate,
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user)
):
    """
    收藏帖子（系统自动分配到默认收藏夹或第一个收藏夹）
    
    Args:
        collection_item (CollectionItemCreate): 收藏项创建数据，包含要收藏的帖子信息
        db (Session): 数据库会话对象，通过依赖注入获取
        current_user (DBUser): 当前认证用户对象，通过依赖注入获取
        
    Returns:
        CollectionItem: 创建成功的收藏项对象
    """
    return create_collection_item(db, collection_item, current_user.id)