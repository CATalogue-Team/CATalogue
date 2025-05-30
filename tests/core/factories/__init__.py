from typing import cast
from factory import alchemy
from factory.helpers import post_generation
from factory.faker import Faker
from factory.declarations import SubFactory
from app.models import User, Cat
from app.extensions import db

class UserFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "commit"

    username = Faker('user_name')
    is_admin = False
    status = 'approved'
    password_hash = 'dummy'  # 临时值，会被set_password覆盖

    @post_generation
    def password(self, create, extracted, **kwargs):
        """设置密码后处理"""
        user = cast(User, self)
        user.set_password(extracted or 'password')
        if create:
            db.session.commit()

class CatFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Cat
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"  # 改为flush而不是commit

    name = Faker('name')
    breed = Faker('word')
    age = Faker('random_int', min=1, max=20)
    description = Faker('text', max_nb_chars=200)
    user_id = None  # 初始设为None，由post_generation设置

    @post_generation
    def set_user(self, create, extracted, **kwargs):
        """设置关联用户"""
        cat = cast(Cat, self)
        if not create:
            return
            
        if extracted:
            cat.user_id = extracted.id
        else:
            user = UserFactory()
            db.session.add(user)
            db.session.commit()  # 确保用户已提交
            cat.user_id = user.id
            
        if not cat.user_id:
            raise ValueError("Cat must have a user_id")
            
        if create:
            db.session.add(cat)
            db.session.commit()  # 确保猫咪已提交
