
from flask import current_app
from flask.cli import with_appcontext
import click
from ..models import User

def register_cli_commands(app):
    """注册所有CLI命令到应用"""
    
    @app.shell_context_processor
    def make_shell_context():
        from .. import db
        from ..models import Cat, User
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
