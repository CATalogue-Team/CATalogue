
from app import create_app, db
from app.core.scheduler import init_scheduler
from app.core.health import run_health_checks
from flask_migrate import Migrate
import sys
import os
from pathlib import Path

def main():
    try:
        # 初始化应用
        app = create_app()
        
        # 配置工作目录
        project_root = Path(__file__).parent
        os.chdir(project_root)
        app.root_path = str(project_root)  # 转换为字符串类型

        # 初始化数据库迁移
        Migrate(app, db)

        # 初始化定时任务
        if app.config.get('SCHEDULED_CHECKS', False):
            init_scheduler(app)

        return app
        
    except Exception as e:
        print(f"应用初始化失败: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    app = main()
    
    # 执行环境检查（在应用上下文中）
    with app.app_context():
        if not run_health_checks(app):
            print("警告: 部分环境检查未通过", file=sys.stderr)
    
    # 运行应用
    app.run(
        debug=app.config['FLASK_DEBUG'],
        use_reloader=app.config['FLASK_ENV'] == 'development'
    )
