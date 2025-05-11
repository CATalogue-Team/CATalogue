
from flask import Blueprint, render_template
from flask_login import login_required
from app.models import EnvironmentCheck
from datetime import datetime, timedelta

bp = Blueprint('health', __name__)

@bp.route('/health')
@login_required
def health_dashboard():
    # 获取最近7天的检查结果
    checks = EnvironmentCheck.query.filter(
        EnvironmentCheck.timestamp >= datetime.utcnow() - timedelta(days=7)
    ).order_by(EnvironmentCheck.timestamp.desc()).all()
    
    # 计算通过率
    stats = {
        'total_checks': len(checks),
        'pass_rate': sum(1 for c in checks if all(c.results.values())) / len(checks) * 100 if checks else 0,
        'common_issues': {}
    }
    
    # 分析常见问题
    if checks:
        for key in checks[0].results.keys():
            fail_count = sum(1 for c in checks if not c.results.get(key, True))
            stats['common_issues'][key] = {
                'fail_count': fail_count,
                'fail_rate': fail_count / len(checks) * 100
            }
    
    return render_template('health/dashboard.html', 
                         checks=checks,
                         stats=stats)
