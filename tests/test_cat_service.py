import pytest
from app.services.cat_service import CatService
from app.models import Cat, User, db
from datetime import datetime, timezone

class TestCatService:
    @pytest.fixture
    def service(self, app, request):
        with app.app_context():
            db.create_all()  # 确保测试前创建所有表
            
            # 创建测试用户
            test_user = User(
                username='testuser',
                password_hash='testpass',
                is_admin=False,
                status='active',
                created_at=datetime.now(timezone.utc))
            db.session.add(test_user)
            db.session.commit()
            
            # 保存用户ID用于清理
            user_id = test_user.id
            
            # 创建并返回service对象
            service = CatService(db)
            # 使用__dict__添加测试用户ID
            service.__dict__['_test_user_id'] = user_id
            
            # 确保测试结束后清理
            def teardown():
                # 使用新的session进行清理
                with app.app_context():
                    # 重新获取测试用户
                    cleanup_user = db.session.query(User).filter_by(id=user_id).first()
                    if cleanup_user:
                        # 先删除该用户创建的所有猫咪记录
                        cats = db.session.query(Cat).filter_by(user_id=user_id).all()
                        for cat in cats:
                            db.session.delete(cat)
                        # 再删除测试用户
                        db.session.delete(cleanup_user)
                        db.session.commit()
            request.addfinalizer(teardown)
            
            yield service
            db.session.remove()

    @pytest.fixture
    def sample_cat(self, service):
        return service.create(
            name='Fluffy',
            age=3,
            breed='Persian',
            description='A cute cat',
            user_id=service.__dict__['_test_user_id']
        )

    def test_create_cat(self, service):
        """测试创建猫咪"""
        cat = service.create(
            name='Whiskers',
            age=2,
            breed='Siamese',
            description='Playful cat',
            user_id=service.__dict__['_test_user_id']  # 使用测试用户的ID
        )
        assert cat.id is not None
        assert cat.name == 'Whiskers'

    def test_get_cat_by_id(self, service, sample_cat):
        """测试根据ID获取猫咪"""
        cat = service.get_cat(sample_cat.id)
        assert cat.id == sample_cat.id
        assert cat.name == 'Fluffy'

    def test_update_cat(self, service, sample_cat):
        """测试更新猫咪信息"""
        updated = service.update(Cat, sample_cat.id, name='Fluffy Updated', age=4)
        assert updated.name == 'Fluffy Updated'
        assert updated.age == 4

    def test_delete_cat(self, service, sample_cat):
        """测试删除猫咪"""
        service.delete(sample_cat.id)
        assert service.get_cat(sample_cat.id) is None

    def test_list_cats(self, service):
        """测试获取猫咪列表"""
        service.create(
            name='Cat1', 
            age=1, 
            breed='TestBreed1', 
            description='Test cat 1', 
            user_id=service.__dict__['_test_user_id']
        )
        service.create(
            name='Cat2', 
            age=2, 
            breed='TestBreed2', 
            description='Test cat 2', 
            user_id=service.__dict__['_test_user_id']
        )
        cats = service.get_all_cats()
        assert len(cats) >= 2

    def test_search_cats(self, service):
        """测试搜索猫咪"""
        service.create(
            name='SearchCat',
            breed='TestBreed',
            age=3,
            description='Test search cat',
            user_id=service.__dict__['_test_user_id']
        )
        results = service.search_cats(breed='TestBreed')
        assert len(results) > 0
        assert results[0].breed == 'TestBreed'

    def test_get_cat_stats(self, service):
        """测试获取猫咪统计信息"""
        stats = service.get_cat_stats()
        assert 'total' in stats
        assert 'by_breed' in stats
