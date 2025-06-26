import pytest
import docker
import subprocess
from pathlib import Path

class TestDockerDeployment:
    """测试Docker部署流程"""
    
    def test_docker_build(self):
        """测试Docker镜像构建"""
        client = docker.from_env()
        image, _ = client.images.build(
            path=".",
            dockerfile="Dockerfile",
            tag="catalogue-test"
        )
        assert image is not None

    def test_docker_compose_up(self):
        """测试docker-compose启动服务"""
        result = subprocess.run(
            ["docker-compose", "up", "-d"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

    def test_docker_compose_down(self):
        """测试docker-compose停止服务"""
        result = subprocess.run(
            ["docker-compose", "down"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 0

@pytest.mark.skipif(
    not Path("docker-compose.yml").exists(),
    reason="需要docker-compose.yml文件"
)
class TestProductionDeployment:
    """测试生产环境部署"""
    
    def test_production_config(self):
        """测试生产环境配置"""
        from app.config import ProductionConfig
        config = ProductionConfig()
        assert config.ENV == 'production'
        assert not config.DEBUG
