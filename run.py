
from app import create_app, db
from core.models import Cat, User  # 更新模型导入路径
from flask_migrate import Migrate
import click
from flask.cli import with_appcontext
import sys

try:
    app = create_app()
    migrate = Migrate(app, db)
    
    # 验证核心模块是否正常加载
    if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
        raise RuntimeError("数据库扩展未正确初始化")
        
except Exception as e:
    print(f"应用初始化失败: {str(e)}", file=sys.stderr)
    sys.exit(1)

def register_cli_commands(app):
    """集中注册所有CLI命令"""
    
    @app.shell_context_processor
    def make_shell_context():
        return {'db': db, 'Cat': Cat, 'User': User}

    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('password')
    @with_appcontext
    def create_admin(username, password):
        """创建管理员账号"""
        try:
            if User.query.filter_by(username=username).first():
                raise click.UsageError(f"用户名 {username} 已存在")
            
            admin = User(
                username=username,
                password=password,
                is_admin=True,
                status='approved'
            )
            db.session.add(admin)
            db.session.commit()
            click.echo(f"管理员账号 {username} 创建成功")
        except Exception as e:
            click.echo(f"错误: {str(e)}", err=True)
            db.session.rollback()

# 注册CLI命令
register_cli_commands(app)

if __name__ == '__main__':
    app.run(debug=True)
