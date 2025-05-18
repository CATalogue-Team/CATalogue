
from typing import List, Optional, Union, Type
from datetime import datetime
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
        
    model = Cat  # 定义模型类
    
    @classmethod
    def get(cls, id: int) -> Optional[Cat]:
        """获取单个猫咪信息"""
        return super().get(cls.model, id)
    
    @classmethod
    def get_all(cls, model: Type[Cat] = None) -> List[Cat]:
        """获取所有猫咪信息"""
        return super().get_all(cls.model)
    
    @classmethod
    def get_cat(cls, cat_id: int) -> Optional[Cat]:
        """获取单个猫咪信息(包含主人信息)"""
        return cls.model.query.options(db.joinedload(Cat.owner)).get(cat_id)
    
    @classmethod
    def get_all_cats(cls) -> List[Cat]:
        """获取所有猫咪信息(按更新时间排序)"""
        return cls.model.query.order_by(Cat.updated_at.desc()).all()
        
    @classmethod
    def get_paginated_cats(cls, page=1, per_page=10, **filters) -> 'flask_sqlalchemy.Pagination':
        """分页获取猫咪信息"""
        query = cls.model.query.order_by(Cat.updated_at.desc())
        for key, value in filters.items():
            if hasattr(cls.model, key):
                query = query.filter(getattr(cls.model, key) == value)
        return query.paginate(page=page, per_page=per_page, error_out=False)
        
    @staticmethod
    def get_recent_cats(limit: int = 3) -> List[Cat]:
        """获取最近添加的猫咪(包含品种筛选)"""
        return Cat.query.order_by(Cat.created_at.desc()).limit(limit).all()
    
    @classmethod
    def create(cls, images: List[FileStorage] = None, **kwargs) -> Cat:
        """创建猫咪信息(支持多图上传)"""
        if 'user_id' in kwargs and not User.query.get(kwargs['user_id']):
            raise ValueError("用户不存在")
            
        kwargs.update({
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        })
        
        cat = super().create(cls.model, **kwargs)
        
        # 处理图片上传
        if images:
            cls._handle_images(cat, images)
            
        return cat
    
    @classmethod
    def _handle_images(cls, cat: Cat, images: List[FileStorage]) -> None:
        """处理猫咪图片上传"""
        for i, image in enumerate(images):
            if not image:
                continue
                
            filename = secure_filename(image.filename)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            image.save(save_path)
            
            # 第一张图片设为主图
            is_primary = i == 0
            # 生成并规范化图片URL
            image_url = f"/static/uploads/{filename}"
            current_app.logger.debug(f"生成的图片URL: {image_url}")
            
            db.session.add(CatImage(
                url=image_url,
                is_primary=is_primary,
                cat_id=cat.id
            ))
            
            current_app.logger.debug(f"保存图片URL: {image_url}")
        
        db.session.commit()
    
    @classmethod
    def update(cls, id: int, images: List[FileStorage] = None, **kwargs) -> Optional[Cat]:
        """
        更新猫咪信息(支持多图上传)
        改进点：
        1. 完整事务管理
        2. 合并图片处理
        3. 增强错误处理
        """
        try:
            cat = cls.model.query.get(id)
            if not cat:
                return None
                
            # 开始事务
            db.session.begin_nested()
            
            # 更新基础信息
            for key, value in kwargs.items():
                if hasattr(cat, key):
                    setattr(cat, key, value)
            cat.updated_at = datetime.utcnow()
            
            # 处理图片上传
            if images:
                # 先删除旧图片
                for image in cat.images:
                    image_path = os.path.join(current_app.static_folder, image.url.lstrip('/static/'))
                    if os.path.exists(image_path):
                        os.remove(image_path)
                    db.session.delete(image)
                
                # 添加新图片
                for i, image in enumerate(images):
                    if not image:
                        continue
                        
                    filename = secure_filename(image.filename)
                    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    image.save(save_path)
                    
                    # 生成并规范化图片URL
                    image_url = f"/static/uploads/{filename}"
                    current_app.logger.debug(f"生成的图片URL: {image_url}")
                    
                    db.session.add(CatImage(
                        url=image_url,
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
        """删除猫咪信息(包含关联图片处理)"""
        try:
            cat = cls.model.query.get(id)
            if not cat:
                current_app.logger.warning(f"尝试删除不存在的猫咪ID: {id}")
                return False
                
            # 删除关联图片
            for image in cat.images:
                try:
                    image_path = os.path.join(current_app.static_folder, image.url.lstrip('/static/'))
                    if os.path.exists(image_path):
                        os.remove(image_path)
                except Exception as e:
                    current_app.logger.error(f"删除图片文件失败: {str(e)}")
            
            # 删除数据库记录
            db.session.delete(cat)
            db.session.commit()
            current_app.logger.info(f"成功删除猫咪ID: {id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"删除猫咪失败(ID:{id}): {str(e)}", exc_info=True)
            raise
    
    @classmethod
    def create_cat(cls, user_id: int, **kwargs) -> Cat:
        """创建猫咪信息(兼容旧接口)"""
        kwargs['user_id'] = user_id
        
        # 检查猫咪名称是否已存在
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
    def search_cats(keyword: str = None, breed: str = None, 
                   min_age: int = None, max_age: int = None,
                   is_adopted: bool = None) -> List[Cat]:
        """
        宽搜索猫咪信息
        参数:
            keyword: 搜索关键词(名称或描述)
            breed: 品种筛选
            min_age: 最小年龄
            max_age: 最大年龄
            is_adopted: 领养状态
        返回:
            匹配的猫咪列表
        """
        query = Cat.query
        
        # 关键词搜索(名称或描述)
        if keyword:
            query = query.filter(
                db.or_(
                    Cat.name.ilike(f'%{keyword}%'),
                    Cat.description.ilike(f'%{keyword}%')
                )
            )
        
        # 品种筛选
        if breed:
            query = query.filter(Cat.breed.ilike(f'%{breed}%'))
            
        # 年龄范围
        if min_age is not None:
            query = query.filter(Cat.age >= min_age)
        if max_age is not None:
            query = query.filter(Cat.age <= max_age)
            
        # 领养状态
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
        current_app.logger.info("开始校验图片URL...")
        
        try:
            images = CatImage.query.all()
            current_app.logger.info(f"共找到{len(images)}条图片记录")
            
            for image in images:
                if not image.url:
                    current_app.logger.warning(f"图片ID {image.id} URL为空")
                    continue
                    
                if image.url.count('/static/uploads/') > 1:
                    original_url = image.url
                    image.url = '/static/uploads/' + image.url.split('/static/uploads/')[-1]
                    db.session.commit()
                    invalid_urls.append((original_url, image.url))
                    current_app.logger.warning(f"修正重复路径: {original_url} -> {image.url}")
                else:
                    current_app.logger.debug(f"图片ID {image.id} URL格式正确: {image.url}")
                    
            current_app.logger.info(f"校验完成，共修正{len(invalid_urls)}条记录")
            return invalid_urls
            
        except Exception as e:
            current_app.logger.error(f"校验图片URL时出错: {str(e)}", exc_info=True)
            raise
