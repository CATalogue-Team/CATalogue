from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from flask_login import login_user, logout_user
from typing import cast
from .. import db
from ..services.user_service import UserService
from ..models import User

api = Namespace('auth', description='用户认证相关操作')

user_model = api.model('User', {
    'id': fields.Integer(description='用户ID'),
    'username': fields.String(required=True, description='用户名'),
    'is_admin': fields.Boolean(description='是否管理员'),
    'status': fields.String(description='账号状态')
})

login_model = api.model('Login', {
    'username': fields.String(required=True, description='用户名'),
    'password': fields.String(required=True, description='密码'),
    'remember': fields.Boolean(description='记住我')
})

register_model = api.model('Register', {
    'username': fields.String(required=True, description='用户名'),
    'password': fields.String(required=True, description='密码'),
    'is_admin': fields.Boolean(description='是否管理员')
})

@api.route('/login')
class Login(Resource):
    @api.doc(security=None)
    @api.expect(login_model)
    @api.response(200, '登录成功', user_model)
    @api.response(401, '无效凭证')
    @api.response(403, '账号未审核')
    def post(self):
        data = request.get_json()
        if not data or not data.get('username') or not data.get('password'):
            api.abort(401, 'Invalid credentials')
            
        # 使用username查询用户
        user = cast(User, current_app.user_service.get_user_by_username(data.get('username')))
        if not user or not user.check_password(data['password']):
            api.abort(401, 'Invalid credentials')
            
        if user.status != 'approved':
            api.abort(403, 'Account not approved')
            
        login_user(user, remember=data.get('remember', False))
        from flask_jwt_extended import create_access_token
        access_token = create_access_token(identity=user.id)
        return {
            'access_token': access_token,
            'token_type': 'bearer',
            'user': {
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin,
                'status': user.status
            }
        }, 200

@api.route('/logout')
class Logout(Resource):
    @api.doc(security='Bearer Auth')
    @api.response(200, '登出成功')
    def post(self):
        logout_user()
        return {'message': 'Logout successful'}, 200

@api.route('/register')
class Register(Resource):
    @api.doc(security=None)
    @api.expect(register_model)
    @api.response(201, '注册成功', user_model)
    @api.response(400, '无效请求')
    @api.response(500, '注册失败')
    def post(self):
        data = request.get_json()
        if not data:
            api.abort(400, 'Invalid request')
            
        try:
            user = current_app.user_service.create_user(
                password=data.get('password'),
                username=data.get('username'),
                is_admin=data.get('is_admin', False),
                status='pending'
            )
            return {
                'message': 'Registration successful',
                'user_id': user.id
            }, 201
        except ValueError as e:
            api.abort(400, str(e))
        except Exception as e:
            api.abort(500, 'Registration failed')
