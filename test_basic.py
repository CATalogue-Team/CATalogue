
from app import create_app
app = create_app()

def test_app_context():
    with app.app_context():
        print("测试环境正常")
        
if __name__ == '__main__':
    test_app_context()
