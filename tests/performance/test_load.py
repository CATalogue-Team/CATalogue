from locust import HttpUser, task, between

class CatalogueUser(HttpUser):
    """模拟用户行为进行性能测试"""
    
    wait_time = between(1, 3)
    
    @task
    def view_home_page(self):
        """测试主页访问性能"""
        self.client.get("/")
        
    @task(3)
    def search_cats(self):
        """测试猫咪搜索性能"""
        self.client.get("/cats/search?q=tabby")
        
    @task(2)
    def view_cat_detail(self):
        """测试猫咪详情页性能"""
        self.client.get("/cats/1")
        
    @task(1)
    def admin_operations(self):
        """测试管理员操作性能"""
        with self.client.post("/login", json={
            "username": "admin",
            "password": "admin123"
        }, catch_response=True) as response:
            if response.status_code == 200:
                self.client.get("/admin/cats")
