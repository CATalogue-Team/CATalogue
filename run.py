
from app import create_app
from app.cli.commands import register_cli_commands
from flask import request
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
        
        # 添加静态文件路由调试
        @app.route('/favicon.ico')
        def favicon():
            return app.send_static_file('favicon.ico')
        
        # 验证核心模块
        if not hasattr(app, 'extensions') or 'sqlalchemy' not in app.extensions:
            raise RuntimeError("数据库扩展未正确初始化")
            
        # 注册CLI命令
        register_cli_commands(app)
        
        # 添加路由调试信息
        @app.before_request
        def log_request_info():
            app.logger.debug(f"请求路径: {request.path}")
            app.logger.debug(f"请求方法: {request.method}")
            app.logger.debug(f"请求参数: {request.args.to_dict()}")
        
        return app
        
    except Exception as e:
        print(f"应用初始化失败: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    app = main()
    app.run(debug=True, use_reloader=False)
