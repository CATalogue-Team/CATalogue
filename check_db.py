from app import create_app, db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    print("Database tables:")
    print(inspector.get_table_names())
    
    # 检查User表是否存在
    from app.models import User
    print("\nUser table columns:")
    print(User.__table__.columns.keys())
