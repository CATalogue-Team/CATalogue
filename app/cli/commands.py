
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
                is_admin=True,
                status='approved'
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            click.echo(f"管理员账号 {username} 创建成功")
        except Exception as e:
            click.echo(f"错误: {str(e)}", err=True)
            db.session.rollback()

    @app.cli.command('create-user')
    @click.argument('username')
    @click.argument('password')
    @with_appcontext
    def create_user(username, password):
        """创建普通用户账号"""
        try:
            if User.query.filter_by(username=username).first():
                raise click.UsageError(f"用户名 {username} 已存在")
            
            user = User(
                username=username,
                is_admin=False,
                status='approved'
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            click.echo(f"普通用户账号 {username} 创建成功")
        except Exception as e:
            click.echo(f"错误: {str(e)}", err=True)
            db.session.rollback()

    @app.cli.command('list-users')
    @with_appcontext
    def list_users():
        """列出所有用户账号"""
        try:
            users = User.query.order_by(User.id).all()
            if not users:
                click.echo("系统中暂无用户")
                return
            
            click.echo("ID\t用户名\t\t管理员\t状态")
            click.echo("--------------------------------")
            for user in users:
                click.echo(f"{user.id}\t{user.username}\t\t{'是' if user.is_admin else '否'}\t{user.status}")
        except Exception as e:
            click.echo(f"错误: {str(e)}", err=True)