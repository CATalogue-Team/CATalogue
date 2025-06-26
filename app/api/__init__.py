from flask_restx import Api
from .auth import api as auth_ns
from .cats import api as cats_ns

# 初始化API
api = Api(
    title='CATalogue API',
    version='1.0',
    description='猫咪领养系统API文档',
    doc='/api/docs',  # Swagger UI路径
    security='Bearer Auth',
    authorizations={
        'Bearer Auth': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization'
        }
    }
)

# 添加命名空间
api.add_namespace(auth_ns)
api.add_namespace(cats_ns)
