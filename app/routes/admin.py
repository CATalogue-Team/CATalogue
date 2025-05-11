
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
import logging
import os
from pathlib import Path

bp = Blueprint('admin', __name__, url_prefix='/admin')

# ... 其他路由 ...

@bp.route('/logs', methods=['GET'])
@login_required
def get_logs():
    """获取日志文件列表"""
    if not current_user.is_admin:
        return jsonify({'error': '无权访问'}), 403
    
    log_dir = Path(current_app.config['LOG_FILE']).parent
    logs = []
    for f in log_dir.glob('*.log*'):
        logs.append({
            'name': f.name,
            'size': f.stat().st_size,
            'modified': f.stat().st_mtime
        })
    return jsonify({'logs': sorted(logs, key=lambda x: x['modified'], reverse=True)})

@bp.route('/logs/<filename>', methods=['GET'])
@login_required
def view_log(filename):
    """查看日志文件内容"""
    if not current_user.is_admin:
        return jsonify({'error': '无权访问'}), 403
    
    log_file = Path(current_app.config['LOG_FILE']).parent / filename
    if not log_file.exists() or not log_file.is_file():
        return jsonify({'error': '日志文件不存在'}), 404
    
    try:
        with open(log_file, 'r') as f:
            content = f.read()
        return jsonify({
            'filename': filename,
            'content': content
        })
    except Exception as e:
        current_app.logger.error(f"读取日志文件失败: {str(e)}")
        return jsonify({'error': '读取日志失败'}), 500

@bp.route('/logs/level', methods=['PUT'])
@login_required
def set_log_level():
    """动态设置日志级别"""
    if not current_user.is_admin:
        return jsonify({'error': '无权访问'}), 403
    
    level = request.json.get('level')
    if level not in ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'):
        return jsonify({'error': '无效的日志级别'}), 400
    
    # 更新所有日志处理器级别
    for handler in current_app.logger.handlers:
        handler.setLevel(level)
    
    # 更新根日志级别
    logging.getLogger().setLevel(level)
    current_app.logger.setLevel(level)
    
    current_app.logger.info(f"日志级别已更新为: {level}")
    return jsonify({'message': f'日志级别已设置为{level}'})

