
from app import create_app
from app.cli.commands import register_cli_commands
from flask_migrate import Migrate
import sys
import os

def main():
    try:
        # 设置工作目录为项目根目录
        project_root = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_root)
        
        app = create_app()
        app.root_path = project_root
        migrate = Migrate(app, app.db)
        
        print(f"工作目录设置为: {os.getcwd()}")
        print(f"应用根路径设置为: {app.root_path}")
        
        # 验证核心模块
        if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
            raise RuntimeError("数据库扩展未正确初始化")
            
        # 注册CLI命令
        register_cli_commands(app)
        
        return app
        
    except Exception as e:
        print(f"应用初始化失败: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    app = main()
    app.run(debug=True)
