
from app import create_app
from app.models import CatImage

app = create_app()
with app.app_context():
    print("开始验证图片URL...")
    images = CatImage.query.all()
    print(f"共找到{len(images)}条图片记录")
    
    for img in images:
        if not img.url.startswith('/static/uploads/'):
            original_url = img.url
            img.url = f'/static/uploads/{img.url.split("/")[-1]}'
            print(f"修正记录ID {img.id}: {original_url} -> {img.url}")
    
    app.db.session.commit()
    print("验证完成")
