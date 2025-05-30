
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

def setup_upload_folder(app):
    """设置上传文件夹"""
    upload_folder = Path(app.config['UPLOAD_FOLDER'])
    if not upload_folder.exists():
        upload_folder.mkdir(parents=True, exist_ok=True)
        logger.info(f"创建上传文件夹: {upload_folder}")

def init_database(admin_username='admin', admin_password='admin123', skip_samples=False):
    """
    初始化数据库和基础数据
    
    :param admin_username: 管理员用户名
    :param admin_password: 管理员密码
    :param skip_samples: 是否跳过示例数据
    """
    app = create_app()
    
    with app.app_context():
        try:
            logger.info("开始数据库初始化流程...")
            
            # 环境检查
            if not check_environment(app):
                raise RuntimeError("环境检查失败")
            
            # 显示关键配置信息
            logger.info(f"数据库位置: {app.config['SQLALCHEMY_DATABASE_URI'].split('///')[-1]}")
            logger.info(f"上传文件夹: {app.config['UPLOAD_FOLDER']}")
            
            # 1. 创建所有表
            logger.info("正在创建数据库表...")
            db.create_all()
            logger.info("数据库表创建完成")
            
            # 2. 设置上传文件夹
            setup_upload_folder(app)
            
            # 3. 初始化管理员账户
            init_admin_account(admin_username, admin_password)
            
            # 4. 初始化示例猫咪数据(可选)
            if not skip_samples:
                init_sample_cats()
            
            logger.info("数据库初始化完成")
            logger.info(f"用户总数: {User.query.count()}")
            logger.info(f"猫咪总数: {Cat.query.count()}")
            logger.info(f"猫咪图片总数: {CatImage.query.count()}")
            
        except Exception as e:
            logger.error(f"初始化失败: {str(e)}")
            logger.exception(e)
            raise
        finally:
            db.session.remove()

def check_environment(app):
    """检查运行环境是否满足要求"""
    try:
        # 检查数据库连接
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        logger.info("数据库连接测试成功")
        
        # 检查上传目录权限
        test_file = Path(app.config['UPLOAD_FOLDER']) / '.permission_test'
        try:
            test_file.touch()
            test_file.unlink()
            logger.info("上传目录权限检查通过")
        except Exception as e:
            logger.error(f"上传目录权限不足: {str(e)}")
            return False
            
        return True
    except Exception as e:
        logger.error(f"环境检查失败: {str(e)}")
        return False

def init_admin_account(admin_username='admin', admin_password='admin123'):
    """初始化管理员账户
    
    :param admin_username: 管理员用户名
    :param admin_password: 管理员密码
    """
    if not User.query.filter_by(username=admin_username).first():
        logger.info(f"正在创建管理员账号: {admin_username}")
        admin = User(
            username=admin_username,
            is_admin=True,
            status='approved'
        )
        admin.set_password(admin_password)
        db.session.add(admin)
        db.session.commit()
        logger.info(f"管理员账号创建成功: {admin_username}/{admin_password}")
    else:
        logger.info("管理员账号已存在")

def init_sample_cats():
    """初始化示例猫咪数据(不包含图片)"""
    logger.info("正在创建示例猫咪数据...")
    
    # 确保管理员用户存在
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        logger.error("必须先创建管理员账号才能初始化示例数据")
        return
        
    # 如果已有猫咪数据则跳过
    if Cat.query.count() > 0:
        logger.info("已有猫咪数据，跳过示例数据初始化")
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
    logger.info(f"已创建 {len(cats)} 条示例猫咪数据")

if __name__ == '__main__':
    init_database()
