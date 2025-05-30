from flask import request
from flask_restx import Namespace, Resource, fields
from .. import db
from ..services.cat_service import CatService
from ..models import Cat

api = Namespace('cats', description='猫咪管理相关操作')

cat_model = api.model('Cat', {
    'id': fields.Integer(description='猫咪ID'),
    'name': fields.String(required=True, description='猫咪名字'),
    'breed': fields.String(description='品种'),
    'age': fields.Integer(description='年龄'),
    'description': fields.String(description='描述'),
    'is_adopted': fields.Boolean(description='是否被领养'),
    'created_at': fields.DateTime(description='创建时间')
})

@api.route('/')
class CatList(Resource):
    @api.doc(security='Bearer Auth')
    @api.marshal_list_with(cat_model)
    def get(self):
        """获取所有猫咪列表"""
        return CatService(db).get_all_cats()

@api.route('/<int:id>')
class CatResource(Resource):
    @api.doc(security='Bearer Auth')
    @api.marshal_with(cat_model)
    def get(self, id):
        """获取单个猫咪详情"""
        cat = CatService(db).get_cat(id)
        if not cat:
            api.abort(404, '猫咪不存在')
        return cat

@api.route('/search')
class CatSearch(Resource):
    @api.doc(security='Bearer Auth')
    @api.doc(params={
        'q': '搜索关键词',
        'breed': '品种筛选',
        'min_age': '最小年龄',
        'max_age': '最大年龄',
        'is_adopted': '是否被领养(true/false)'
    })
    @api.marshal_list_with(cat_model)
    def get(self):
        """搜索猫咪"""
        search_params = {
            'q': request.args.get('q', ''),
            'breed': request.args.get('breed', ''),
            'min_age': request.args.get('min_age', type=int),
            'max_age': request.args.get('max_age', type=int),
            'is_adopted': request.args.get('is_adopted', type=lambda x: x == 'true')
        }
        cats = CatService(db).search_cats(**search_params)
        return cats if cats else []
