
import os
from flask import Flask
from app import create_app, db
from app.models import CatImage

app = create_app()
app.app_context().push()

def validate_image_urls():
    """校验并修复数据库中的图片URL"""
    print("开始校验图片URL...")
    invalid_urls = []
    
    try:
        images = CatImage.query.all()
        print(f"共找到{len(images)}条图片记录")
        
        for image in images:
            if not image.url:
                print(f"警告: 图片ID {image.id} URL为空")
                continue
                
            if image.url.count('/static/uploads/') > 1:
                original_url = image.url
                image.url = '/static/uploads/' + image.url.split('/static/uploads/')[-1]
                db.session.commit()
                invalid_urls.append((original_url, image.url))
                print(f"修正重复路径: {original_url} -> {image.url}")
            else:
                print(f"图片ID {image.id} URL格式正确: {image.url}")
                
        print(f"校验完成，共修正{len(invalid_urls)}条记录")
        return invalid_urls
        
    except Exception as e:
        print(f"校验图片URL时出错: {str(e)}")
        raise

if __name__ == '__main__':
    validate_image_urls()
