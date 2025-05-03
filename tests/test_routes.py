
import pytest
from app import create_app
from flask import url_for
import time
from colorama import init, Fore

# 初始化彩色输出
init(autoreset=True)

class TestReporter:
    @staticmethod
    def start_test(name):
        print(f"\n{Fore.CYAN}▶ 开始测试: {name}{Fore.RESET}")
        
    @staticmethod    
    def end_test(name, duration):
        print(f"{Fore.CYAN}◀ 完成测试: {name} (耗时: {duration:.2f}s){Fore.RESET}")
        
    @staticmethod
    def test_step(description):
        print(f"{Fore.YELLOW}▷ 测试步骤: {description}{Fore.RESET}")
        
    @staticmethod
    def success(message):
        print(f"{Fore.GREEN}✓ 成功: {message}{Fore.RESET}")
        
    @staticmethod
    def failure(message):
        print(f"{Fore.RED}✗ 失败: {message}{Fore.RESET}")

@pytest.fixture
def app():
    TestReporter.start_test("应用初始化")
    start_time = time.time()
    app = create_app()
    app.config['TESTING'] = True
    TestReporter.end_test("应用初始化", time.time() - start_time)
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_main_routes(client, app):
    """测试主路由"""
    TestReporter.start_test("主路由测试")
    routes = [
        ('首页', 'main.home', {}),
        ('搜索页', 'main.search', {}),
        ('健康检查', 'main.ping', {}),
        ('分页测试', 'main.test_pagination', {})
    ]
    
    for name, endpoint, params in routes:
        TestReporter.test_step(f"测试 {name} 路由")
        start_time = time.time()
        with app.app_context():
            res = client.get(url_for(endpoint, **params))
        
        if res.status_code in [200, 302]:
            TestReporter.success(
                f"{name} 路由 ({endpoint}) - 状态码: {res.status_code} "
                f"(耗时: {time.time()-start_time:.2f}s)"
            )
        else:
            TestReporter.failure(
                f"{name} 路由 ({endpoint})\n"
                f"预期状态码: 200或302\n"
                f"实际状态码: {res.status_code}\n"
                f"响应内容: {res.data[:100]}..."
            )
            pytest.fail(f"{name} 路由测试失败")
    
    TestReporter.end_test("主路由测试", time.time() - start_time)

def test_cat_routes(client, app):
    """测试猫咪路由"""
    TestReporter.start_test("猫咪路由测试")
    routes = [
        ('猫咪详情', 'cats.detail', {'cat_id': 1}),
        ('管理列表', 'cats.admin__list', {}),
        ('猫咪搜索', 'cats.search', {})
    ]
    
    for name, endpoint, params in routes:
        TestReporter.test_step(f"测试 {name} 路由")
        start_time = time.time()
        with app.app_context():
            res = client.get(url_for(endpoint, **params))
        
        if res.status_code in [200, 302, 401]:
            TestReporter.success(
                f"{name} 路由 ({endpoint}) - 状态码: {res.status_code} "
                f"(耗时: {time.time()-start_time:.2f}s)"
            )
        else:
            TestReporter.failure(
                f"{name} 路由 ({endpoint})\n"
                f"预期状态码: 200, 302或401\n"
                f"实际状态码: {res.status_code}\n"
                f"响应内容: {res.data[:100]}..."
            )
            pytest.fail(f"{name} 路由测试失败")
    
    TestReporter.end_test("猫咪路由测试", time.time() - start_time)

def test_auth_routes(client, app):
    """测试认证路由"""
    TestReporter.start_test("认证路由测试")
    routes = [
        ('用户登录', 'auth.login', {}),
        ('用户登出', 'auth.logout', {}),
        ('用户注册', 'auth.register', {})
    ]
    
    for name, endpoint, params in routes:
        TestReporter.test_step(f"测试 {name} 路由")
        start_time = time.time()
        with app.app_context():
            res = client.get(url_for(endpoint, **params))
        
        if res.status_code in [200, 302]:
            TestReporter.success(
                f"{name} 路由 ({endpoint}) - 状态码: {res.status_code} "
                f"(耗时: {time.time()-start_time:.2f}s)"
            )
        else:
            TestReporter.failure(
                f"{name} 路由 ({endpoint})\n"
                f"预期状态码: 200或302\n"
                f"实际状态码: {res.status_code}\n"
                f"响应内容: {res.data[:100]}..."
            )
            pytest.fail(f"{name} 路由测试失败")
    
    TestReporter.end_test("认证路由测试", time.time() - start_time)
