
from app import create_app, db
from app.core.scheduler import init_scheduler
from app.core.health_check import HealthCheck
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
        health_checker = HealthCheck(app)
        if not health_checker.run_health_checks():
            print("警告: 部分环境检查未通过", file=sys.stderr)
            # 可选: 执行自动修复
            # checks = health_checker.environment_checker.check_dev_environment() if app.config['FLASK_ENV'] == 'development' else health_checker.environment_checker.check_prod_environment()
            # health_checker.run_auto_repair(checks)
    
    # 运行应用
    app.run(
        host='0.0.0.0',
        port=app.config['APP_PORT'],
        debug=app.config['FLASK_DEBUG'],
        use_reloader=app.config['FLASK_ENV'] == 'development'
    )
