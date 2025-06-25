from app import create_app, db
from app.models import User

app = create_app()

with app.app_context():
    # 创建所有数据库表
    db.create_all()
    
    # 创建初始管理员用户
    if not db.session.query(User).filter_by(username='admin').first():
        admin = User(
            username='admin',
            is_admin=True,
            status='approved'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("成功创建管理员用户: admin")
    else:
        print("管理员用户已存在")
