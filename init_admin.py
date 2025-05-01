
from app import create_app, db
from app.models import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app()
with app.app_context():
    try:
        logger.info("正在初始化数据库连接...")
        # 测试数据库连接
        db.engine.connect()
        logger.info("数据库连接成功")
        
        # 检查admin账号是否已存在
        if not User.query.filter_by(username='admin').first():
            logger.info("正在创建管理员账号...")
            admin = User(
                username='admin',
                is_admin=True,
                status='approved'
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            logger.info("管理员账号创建成功: admin/admin123")
        else:
            logger.info("管理员账号已存在")
            
    except Exception as e:
        logger.error(f"初始化失败: {str(e)}")
