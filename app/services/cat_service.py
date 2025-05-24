from typing import List, Optional, Type, cast
from datetime import datetime, timezone
from sqlalchemy.orm import Query
from .. import db
from ..models import Cat, User, CatImage
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
import os
from flask import current_app, url_for
from .base_service import BaseService

class CatService(BaseService):
    """猫咪信息服务层"""
    def __init__(self, db):
        super().__init__(db)
        
    model: Type[Cat] = Cat  # 定义模型类
    
    @classmethod
    def get(cls, model: Type[Cat] = None, id: int = None) -> Optional[Cat]:  # type: ignore
        """获取单个猫咪信息"""
        model = model or cls.model
        if id is None:
            return None
        return cast(Optional[Cat], super().get(model, id))
    
    @classmethod
    def get_all(cls, model: Type[Cat] = None) -> List[Cat]:
        """获取所有猫咪信息"""
        return super().get_all(cls.model)
    
    @classmethod
    def get_cat(cls, cat_id: int) -> Optional[Cat]:
        """获取单个猫咪信息(包含主人信息)"""
        from sqlalchemy.orm import joinedload
        from ..models import Cat
        cat = db.session.get(Cat, cat_id, options=[joinedload(Cat.owner)])  # type: ignore
        return cat
    
    @classmethod
    def get_all_cats(cls) -> List[Cat]:
        """获取所有猫咪信息(按更新时间排序)"""
        return cls.model.query.order_by(Cat.updated_at.desc()).all()
        
    @classmethod
    def get_paginated_cats(cls, page: int = 1, per_page: int = 10, **filters) -> dict:
        """分页获取猫咪信息
        返回格式:
        {
            'items': List[Cat],  # 当前页数据
            'total': int,         # 总记录数
            'pages': int,         # 总页数
            'current_page': int,  # 当前页码
            'per_page': int       # 每页数量
        }
        """
        query = cls.model.query.order_by(Cat.updated_at.desc())
        for key, value in filters.items():
            if hasattr(cls.model, key):
                query = query.filter(getattr(cls.model, key) == value)
        
        # 手动实现分页
        total = query.count()
        items = query.offset((page - 1) * per_page).limit(per_page).all()
        pages = (total + per_page - 1) // per_page
        
        return {
            'items': items,
            'total': total,
            'pages': pages,
            'current_page': page,
            'per_page': per_page
        }
        
    @staticmethod
    def get_recent_cats(limit: int = 3) -> List[Cat]:
        """获取最近添加的猫咪(包含品种筛选)"""
        return Cat.query.order_by(Cat.created_at.desc()).limit(limit).all()
    
    @classmethod
    def create(cls, images: Optional[List[FileStorage]] = None, **kwargs) -> Cat:
        """创建猫咪信息(支持多图上传)"""
        if 'user_id' in kwargs:
            user_id = kwargs['user_id']
            if not db.session.get(User, user_id):
                raise ValueError(f"用户ID {user_id} 不存在")
            
        kwargs.update({
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc)
        })
        
        cat = super().create(cls.model, **kwargs)
        
        if images:
            cls._handle_images(cat.id, images)
            
        return cat
    
    @classmethod
    def _handle_images(cls, cat_id: int, images: List[FileStorage]) -> None:
        """处理猫咪图片上传"""
        if not images:
            return

        try:
            for i, image in enumerate(images):
                if not image or not image.filename or not image.content_type:
                    continue

                if not image.content_type.startswith('image/'):
                    raise ValueError("只允许上传图片文件")

                filename = secure_filename(str(image.filename))
                if not filename:
                    continue
                    
                upload_folder = current_app.config.get('UPLOAD_FOLDER')
                if not upload_folder:
                    raise ValueError("上传目录未配置")
                    
                save_path = os.path.join(str(upload_folder), filename)
                image.save(save_path)

                db.session.add(CatImage(
                    url=f"/static/uploads/{filename}",
                    is_primary=(i == 0),
                    cat_id=cat_id,
                    created_at=datetime.now(timezone.utc)
                ))
            
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"图片上传失败: {str(e)}")
            raise
    
    @classmethod
    def update(cls, id: int, images: Optional[List[FileStorage]] = None, **kwargs) -> Optional[Cat]:
        """更新猫咪信息"""
        try:
            cat = db.session.get(cls.model, id)
            if not cat:
                return None
                
            db.session.begin_nested()
            
            for key, value in kwargs.items():
                if hasattr(cat, key):
                    setattr(cat, key, value)
            cat.updated_at = datetime.now(timezone.utc)
            
            if images:
                for image in list(cat.images if cat.images else []):  # type: ignore
                    static_folder = current_app.static_folder
                    if not static_folder or not image.url:
                        continue
                    image_path = os.path.join(str(static_folder), str(image.url).lstrip('/static/'))
                    if os.path.exists(image_path):
                        try:
                            os.remove(image_path)
                        except Exception as e:
                            current_app.logger.error(f"删除图片文件失败: {str(e)}")
                    db.session.delete(image)
                
                for i, image in enumerate(images):
                    if not image:
                        continue
                        
                    filename = secure_filename(str(image.filename))
                    upload_folder = current_app.config.get('UPLOAD_FOLDER')
                    if not upload_folder:
                        raise ValueError("上传目录未配置")
                    save_path = os.path.join(str(upload_folder), filename)
                    image.save(save_path)
                    
                    db.session.add(CatImage(
                        url=f"/static/uploads/{filename}",
                        is_primary=(i == 0),
                        cat_id=cat.id
                    ))
            
            db.session.commit()
            return cat
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"更新猫咪失败: {str(e)}")
            raise
    
    @classmethod
    def delete(cls, id: int) -> bool:
        """删除猫咪信息"""
        try:
            cat = db.session.get(cls.model, id)
            if not cat:
                current_app.logger.warning(f"尝试删除不存在的猫咪ID: {id}")
                return False
                
            # 删除关联图片
            for image in list(cat.images if cat.images else []):  # type: ignore
                try:
                    if image.url:
                        image_path = os.path.join(
                            str(current_app.static_folder), 
                            str(image.url).lstrip('/static/'))
                        if os.path.exists(image_path):
                            os.remove(image_path)
                except Exception as e:
                    current_app.logger.error(f"删除图片文件失败: {str(e)}")
                    continue
            
            # 删除猫咪记录
            db.session.delete(cat)
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"删除猫咪失败(ID:{id}): {str(e)}", exc_info=True)
            return False
    
    @classmethod
    def create_cat(cls, user_id: int, **kwargs) -> Cat:
        """创建猫咪信息(兼容旧接口)"""
        kwargs['user_id'] = user_id
        
        if 'name' in kwargs and cls.model.query.filter_by(name=kwargs['name']).first():
            raise ValueError(f"猫咪名称'{kwargs['name']}'已存在")
            
        return cls.create(**kwargs)
    
    @classmethod
    def update_cat(cls, cat_id: int, **kwargs) -> Optional[Cat]:
        """更新猫咪信息(兼容旧接口)"""
        return cls.update(cat_id, **kwargs)
    
    @classmethod
    def delete_cat(cls, cat_id: int) -> bool:
        """删除猫咪信息(兼容旧接口)"""
        return cls.delete(cat_id)
    
    @staticmethod
    def search_cats(keyword: Optional[str] = None, breed: Optional[str] = None, 
                   min_age: Optional[int] = None, max_age: Optional[int] = None,
                   is_adopted: Optional[bool] = None) -> List[Cat]:
        """搜索猫咪信息"""
        query = Cat.query
        
        if keyword:
            query = query.filter(
                db.or_(
                    Cat.name.ilike(f'%{keyword}%'),
                    Cat.description.ilike(f'%{keyword}%')
                )
            )
        
        if breed:
            query = query.filter(Cat.breed.ilike(f'%{breed}%'))
            
        if min_age is not None:
            query = query.filter(Cat.age >= min_age)
        if max_age is not None:
            query = query.filter(Cat.age <= max_age)
            
        if is_adopted is not None:
            query = query.filter(Cat.is_adopted == is_adopted)
            
        return query.order_by(Cat.updated_at.desc()).all()
        
    @staticmethod
    def get_cats_by_breed(breed: str) -> List[Cat]:
        """按品种筛选猫咪(兼容旧接口)"""
        return CatService.search_cats(breed=breed)
        
    @staticmethod
    def get_adoptable_cats() -> List[Cat]:
        """获取可领养的猫咪(兼容旧接口)"""
        return CatService.search_cats(is_adopted=False)
        
    @classmethod
    def validate_image_urls(cls):
        """校验并修复数据库中的图片URL"""
        from ..models import CatImage
        invalid_urls = []
        
        try:
            images = CatImage.query.all()
            for image in images:
                if not image.url:
                    continue
                    
                if image.url.count('/static/uploads/') > 1:
                    original_url = image.url
                    image.url = '/static/uploads/' + image.url.split('/static/uploads/')[-1]
                    db.session.commit()
                    invalid_urls.append((original_url, image.url))
                    
            return invalid_urls
            
        except Exception as e:
            current_app.logger.error(f"校验图片URL时出错: {str(e)}", exc_info=True)
            raise
