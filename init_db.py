
from app import create_app, db
from app.models import User, Cat
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def init_database():
    """初始化数据库和基础数据"""
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("开始数据库初始化流程...")
            
            # 1. 创建所有表
            logger.info("正在创建数据库表...")
            db.create_all()
            logger.info("数据库表创建完成")
            
            # 2. 初始化管理员账户
            init_admin_account()
            
            # 3. 初始化示例数据
            init_sample_data()
            
            logger.info("数据库初始化完成")
            
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            raise

def init_admin_account():
    """初始化管理员账户"""
    if not User.query.filter_by(username='admin').first():
        logger.info("正在创建管理员账号...")
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True,
            status='approved'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        logger.info("管理员账号创建成功: admin/admin123")
    else:
        logger.info("管理员账号已存在")

def init_sample_data():
    """初始化示例猫咪数据"""
    if Cat.query.count() == 0:
        logger.info("正在创建示例猫咪数据...")
        cats = [
            Cat(name='橘猫', description='可爱的橘色猫咪', created_at=datetime.utcnow()),
            Cat(name='黑猫', description='神秘的黑猫', created_at=datetime.utcnow()),
            Cat(name='白猫', description='纯洁的白猫', created_at=datetime.utcnow())
        ]
        db.session.bulk_save_objects(cats)
        db.session.commit()
        logger.info(f"已创建 {len(cats)} 条示例猫咪数据")

if __name__ == '__main__':
    init_database()
