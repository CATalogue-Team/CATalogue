
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

def init_scheduler(app):
    """初始化定时任务"""
    scheduler = BackgroundScheduler()
    
    # 添加健康检查任务
    scheduler.add_job(
        func=lambda: run_health_checks(app),
        trigger='interval',
        hours=app.config.get('CHECK_INTERVAL_HOURS', 1),
        id='health_checks'
    )
    
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    return scheduler
