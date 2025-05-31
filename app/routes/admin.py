
from flask import Blueprint, jsonify, request, current_app, abort
from app import db
from flask_login import login_required, current_user
import logging
import os
from pathlib import Path
from app.models import User, Cat
from app.services.user_service import UserService
from app.services.cat_service import CatService

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/users', methods=['GET'])
@login_required
def list_users():
    """获取用户列表"""
    if not current_user.is_admin:
        abort(403)
    users = UserService(db).get_all_users()
    return jsonify([u.to_dict() for u in users])

@bp.route('/cats', methods=['GET'])
@login_required
def list_cats():
    """获取猫咪列表""" 
    if not current_user.is_admin:
        abort(403)
    cats = CatService(db).get_all_cats()
    return jsonify([c.to_dict() for c in cats])

@bp.route('/approvals', methods=['GET'])
@login_required
def list_approvals():
    """获取待审批项"""
    if not current_user.is_admin:
        abort(403)
    # TODO: 实现审批逻辑
    return jsonify([])

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
    
    if not request.json or 'level' not in request.json:
        return jsonify({'error': '缺少level参数'}), 400
        
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
