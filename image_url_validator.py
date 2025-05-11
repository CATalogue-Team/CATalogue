
import os
import logging
from flask import Flask
from app import create_app, db
from app.models import CatImage

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def validate_and_fix_image_urls(dry_run=False, limit=None):
    """
    校验并修复数据库中的图片URL
    
    :param dry_run: 仅检查不修改
    :param limit: 限制检查的记录数
    """
    app = create_app()
    with app.app_context():
        logger.info("开始图片URL校验...")
        
        try:
            query = CatImage.query
            if limit:
                query = query.limit(limit)
                logger.info(f"限制检查前{limit}条记录")
                
            images = query.all()
            logger.info(f"共找到{len(images)}条图片记录")
            
            invalid_count = 0
            for image in images:
                if not image.url:
                    logger.warning(f"图片ID {image.id} URL为空")
                    continue
                    
                if not image.url.startswith('/static/uploads/'):
                    new_url = f'/static/uploads/{image.url.split("/")[-1]}'
                    logger.info(f"需要修正: {image.url} -> {new_url}")
                    
                    if not dry_run:
                        image.url = new_url
                        invalid_count += 1
                else:
                    logger.debug(f"图片ID {image.id} URL格式正确")
            
            if not dry_run:
                db.session.commit()
                logger.info(f"校验完成，共修正{invalid_count}条记录")
            else:
                logger.info(f"校验完成(模拟模式)，发现{invalid_count}条需要修正的记录")
                
        except Exception as e:
            logger.error(f"校验图片URL时出错: {str(e)}")
            raise

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='校验和修复图片URL')
    parser.add_argument('--dry-run', action='store_true', help='仅检查不修改')
    parser.add_argument('--limit', type=int, help='限制检查的记录数')
    args = parser.parse_args()
    
    validate_and_fix_image_urls(dry_run=args.dry_run, limit=args.limit)

