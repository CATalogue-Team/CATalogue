
from app import create_app
from app.cli.commands import register_cli_commands
from flask import request
from flask_migrate import Migrate
import sys
import os
import logging

def main():
    try:
        # 设置工作目录为项目根目录
        project_root = os.path.dirname(os.path.abspath(__file__))
        os.chdir(project_root)
        
        app = create_app()
        app.root_path = project_root
        migrate = Migrate(app, app.db)
        
        # 配置日志系统
        if not app.debug:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                app.config['LOG_FILE'],
                maxBytes=10240,
                backupCount=10
            )
            file_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
            file_handler.setLevel(app.config['LOG_LEVEL'])
            app.logger.addHandler(file_handler)
            app.logger.info('已配置生产环境日志系统')
        
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
    # 开发模式下自动运行测试
    if os.getenv('FLASK_ENV') == 'development':
        print("\n=== 开发模式检测 ===")
        print("正在检查测试配置...")
        try:
            import pytest
            print("测试依赖已安装")
            
            # 检查测试文件是否存在
            test_path = os.path.join(os.path.dirname(__file__), 'tests/test_routes.py')
            if os.path.exists(test_path):
                print(f"测试文件存在: {test_path}")
                print("提示: 使用 'python -m pytest tests/' 运行测试")
            else:
                print("警告: 未找到测试文件")
                
        except ImportError:
            print("警告: pytest未安装，请运行 'pip install pytest'")
            
        print("===================\n")
    
    # 正常启动应用(使用config中的调试设置)
    app = main()
    app.run(
        debug=app.config['FLASK_DEBUG'],
        use_reloader=app.config['FLASK_ENV'] == 'development'
    )
