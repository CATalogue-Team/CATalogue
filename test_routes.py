
from app import create_app

app = create_app()

def test_routes():
    print("=== 路由测试 ===")
    print("已注册蓝图:")
    for name, blueprint in app.blueprints.items():
        print(f"- {name}: {len(blueprint.deferred_functions)}个路由")
    
    print("\n主要端点:")
    for rule in app.url_map.iter_rules():
        if not rule.rule.startswith('/static'):
            print(f"{rule.endpoint}: {rule.rule}")

if __name__ == '__main__':
    test_routes()
