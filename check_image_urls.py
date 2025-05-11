
from app import create_app
from app.models import CatImage

app = create_app()
with app.app_context():
    images = CatImage.query.limit(5).all()
    print(f"找到{len(images)}条图片记录")
    for img in images:
        print(f"ID: {img.id}, URL: {img.url}")
