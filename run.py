
from app import create_app, db
from app.models import Cat, User
from flask_migrate import Migrate
import click
from flask.cli import with_appcontext

app = create_app()
migrate = Migrate(app, db)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Cat': Cat, 'User': User}

@click.command('create-admin')
@click.argument('username')
@click.argument('password')
@with_appcontext
def create_admin(username, password):
    """创建管理员账号"""
    if User.query.filter_by(username=username).first():
        print(f"错误：用户名 {username} 已存在")
        return
    
    admin = User(
        username=username,
        password=password,
        is_admin=True,
        status='approved'
    )
    db.session.add(admin)
    db.session.commit()
    print(f"管理员账号 {username} 创建成功")

app.cli.add_command(create_admin)

if __name__ == '__main__':
    app.run(debug=True)
