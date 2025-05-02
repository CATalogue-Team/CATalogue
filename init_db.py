
from app import create_app, db
from app.models import User, Cat, CatImage
import logging
from datetime import datetime
import os
from werkzeug.utils import secure_filename
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 示例图片URL
SAMPLE_IMAGES = [
    "cat1.jpg",
    "cat2.jpg",
    "cat3.jpg"
]

def setup_upload_folder(app):
    """设置上传文件夹"""
    upload_folder = Path(app.config['UPLOAD_FOLDER'])
    if not upload_folder.exists():
        upload_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"创建上传文件夹: {upload_folder}")

def init_database():
    """初始化数据库和基础数据"""
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("开始数据库初始化流程...")
            # 显示数据库配置信息
            db_uri = app.config['SQLALCHEMY_DATABASE_URI']
            logger.info(f"数据库位置: {db_uri.split('///')[-1]}")
            
            # 1. 创建所有表
            logger.info("正在创建数据库表...")
            db.create_all()
            logger.info("数据库表创建完成")
            
            # 2. 设置上传文件夹
            setup_upload_folder(app)
            
            # 3. 初始化管理员账户
            init_admin_account()
            
            # 4. 初始化示例数据
            init_sample_data(app)
            
            logger.info("数据库初始化完成")
            logger.info(f"数据库文件位置: {app.config['SQLALCHEMY_DATABASE_URI'].split('///')[-1]}")
            
            # 打印初始化结果
            logger.info(f"用户总数: {User.query.count()}")
            logger.info(f"猫咪总数: {Cat.query.count()}")
            logger.info(f"猫咪图片总数: {CatImage.query.count()}")
            
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            logger.exception(e)
            raise
        finally:
            # 确保数据库会话关闭
            db.session.remove()

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

def init_sample_data(app):
    """初始化示例猫咪数据"""
    if Cat.query.count() == 0:
        logger.info("正在创建示例猫咪数据...")
        
        # 确保管理员用户存在
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            logger.error("必须先创建管理员账号才能初始化示例数据")
            return
            
        # 创建示例猫咪
        cats = [
            Cat(name='橘猫', breed='橘猫', age=2, 
                description='可爱的橘色猫咪，性格温顺', 
                is_adopted=False, user_id=admin.id),
            Cat(name='黑猫', breed='黑猫', age=3,
                description='神秘的黑猫，喜欢夜间活动',
                is_adopted=True, user_id=admin.id),
            Cat(name='白猫', breed='波斯猫', age=1,
                description='纯洁的白猫，长毛品种',
                is_adopted=False, user_id=admin.id),
            Cat(name='三花猫', breed='三花猫', age=4,
                description='花色漂亮的三花猫，已绝育',
                is_adopted=False, user_id=admin.id),
            Cat(name='英短', breed='英国短毛猫', age=2,
                description='圆脸可爱的英国短毛猫',
                is_adopted=True, user_id=admin.id)
        ]
        
        db.session.bulk_save_objects(cats)
        db.session.commit()
        
        # 为每只猫添加示例图片
        for i, cat in enumerate(Cat.query.all()):
            for j, img_name in enumerate(SAMPLE_IMAGES):
                # 创建示例图片文件
                img_path = Path(app.config['UPLOAD_FOLDER']) / img_name
                if not img_path.exists():
                    with open(img_path, 'wb') as f:
                        f.write(os.urandom(1024))  # 生成随机内容作为示例图片
                
                # 添加图片记录
                db.session.add(CatImage(
                    url=f'uploads/{img_name}',
                    is_primary=j == 0,  # 第一张设为主图
                    cat_id=cat.id
                ))
        
        db.session.commit()
        logger.info(f"已创建 {len(cats)} 条示例猫咪数据，每只猫添加了 {len(SAMPLE_IMAGES)} 张图片")

if __name__ == '__main__':
    init_database()
