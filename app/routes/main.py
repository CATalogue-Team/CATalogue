
from flask import render_template, redirect, url_for
from flask_login import login_required
from flask_restx import Namespace, Resource, fields
from app.services.cat_service import CatService

# 保留模板路由的传统实现
def register_template_routes(app):
    @app.route('/')
    def home():
        return render_template('home.html')

    @app.route('/search')
    @login_required
    def search():
        from app.extensions import db
        service = CatService(db)
        cats = service.get_recent_cats(limit=3)
        return render_template('search.html',
                            cats=cats,
                            no_results=False,
                            is_recommendation=bool(cats))

# API路由标准化
api = Namespace('main', description='主路由API')

@api.route('/ping')
class Ping(Resource):
    @api.doc(description='测试服务状态')
    @api.response(200, '成功', model={
        'status': fields.String,
        'message': fields.String
    })
    def get(self):
        """测试路由"""
        return {'status': 'ok', 'message': 'pong'}

@api.route('/test_pagination')
class TestPagination(Resource):
    @api.doc(description='测试分页配置')
    @api.response(200, '成功', model={
        'config_page_size': fields.Integer,
        'actual_page_size': fields.Integer,
        'total_pages': fields.Integer
    })
    def get(self):
        """测试分页配置"""
        from flask import current_app
        from app.extensions import db
        page_size = current_app.config.get('ITEMS_PER_PAGE', 10)
        service = CatService(db)
        cats = service.get_recent_cats(limit=page_size)
        return {
            'config_page_size': page_size,
            'actual_page_size': len(cats),
            'total_pages': 1
        }
