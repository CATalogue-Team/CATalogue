from flask import Blueprint, jsonify
from app.core.base_crud import BaseCRUD

bp = Blueprint('admin_cats', __name__, url_prefix='/admin/cats')

def init_cat_crud(cat_service):
    """初始化BaseCRUD (仅限管理后台使用)"""
    return BaseCRUD(
        service=cat_service,
        model_name='cat',
        list_template='admin/cats_list.html',  # 仅保留后台模板
        detail_template='admin/cat_detail.html',
        edit_template='admin/edit_cat.html',
        list_route='admin_cats.list_cats',
        detail_route='admin_cats.get_cat',
        create_route='admin_cats.create_cat',
        edit_route='admin_cats.update_cat',
        delete_route='admin_cats.delete_cat'
    )

@bp.route('/api/v1/cats', methods=['GET'])
def list_cats():
    """API端点-获取猫咪列表"""
    from app.services.cat_service import CatService
    from app import db
    
    service = CatService(db)
    cats = service.search_cats()
    return jsonify({
        'data': [cat.to_dict() for cat in cats],
        'meta': {
            'version': 'v1',
            'count': len(cats)
        }
    })

@bp.route('/api/v1/cats/<int:id>', methods=['GET'])
def get_cat(id):
    """API端点-获取猫咪详情(JSON格式)"""
    from app.services.cat_service import CatService
    from app import db
    
    service = CatService(db)
    cat = service.get_cat(id)
    if not cat:
        return jsonify({
            'error': {
                'code': 404,
                'message': '猫咪不存在'
            }
        }), 404
        
    return jsonify({
        'data': cat.to_dict(),
        'meta': {
            'version': 'v1'
        }
    })

@bp.route('/api/v1/cats', methods=['POST'])
def create_cat():
    """API端点-创建猫咪"""
    from app.services.cat_service import CatService
    from app import db
    from flask import request
    
    if not request.is_json:
        return jsonify({
            'error': {
                'code': 400,
                'message': '请求必须是JSON格式'
            }
        }), 400
        
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({
            'error': {
                'code': 400,
                'message': '缺少user_id字段'
            }
        }), 400
    
    service = CatService(db)
    try:
        cat_data = {k: v for k, v in data.items() if k != 'user_id'}
        cat = service.create_cat(
            user_id=data['user_id'],
            **cat_data
        )
        return jsonify({
            'data': cat.to_dict(),
            'meta': {
                'version': 'v1'
            }
        }), 201
    except ValueError as e:
        return jsonify({
            'error': {
                'code': 400,
                'message': str(e)
            }
        }), 400

@bp.route('/api/v1/cats/<int:id>', methods=['PUT'])
def update_cat(id):
    """API端点-更新猫咪信息"""
    from app.services.cat_service import CatService
    from app import db
    from flask import request
    
    if not request.is_json:
        return jsonify({
            'error': {
                'code': 400,
                'message': '请求必须是JSON格式'
            }
        }), 400
        
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({
            'error': {
                'code': 400,
                'message': '缺少user_id字段'
            }
        }), 400
    
    service = CatService(db)
    try:
        cat_data = {k: v for k, v in data.items() if k != 'user_id'}
        cat = service.update_cat(
            id=id,
            current_user_id=data['user_id'],
            **cat_data
        )
        return jsonify({
            'data': cat.to_dict(),
            'meta': {
                'version': 'v1'
            }
        })
    except ValueError as e:
        return jsonify({
            'error': {
                'code': 400,
                'message': str(e)
            }
        }), 400
    except PermissionError as e:
        return jsonify({
            'error': {
                'code': 403,
                'message': str(e)
            }
        }), 403

@bp.route('/api/v1/cats/<int:id>', methods=['DELETE'])
def delete_cat(id):
    """API端点-删除猫咪"""
    from app.services.cat_service import CatService
    from app import db
    from flask import request
    
    if not request.is_json:
        return jsonify({
            'error': {
                'code': 400,
                'message': '请求必须是JSON格式'
            }
        }), 400
        
    data = request.get_json()
    if not data or 'user_id' not in data:
        return jsonify({
            'error': {
                'code': 400,
                'message': '缺少user_id字段'
            }
        }), 400
    
    service = CatService(db)
    try:
        success = service.delete_cat(
            id=id,
            user_id=data['user_id']
        )
        if success:
            return '', 204
        return jsonify({
            'error': {
                'code': 500,
                'message': '删除失败'
            }
        }), 500
    except ValueError as e:
        return jsonify({
            'error': {
                'code': 404,
                'message': str(e)
            }
        }), 404
    except PermissionError as e:
        return jsonify({
            'error': {
                'code': 403,
                'message': str(e)
            }
        }), 403
