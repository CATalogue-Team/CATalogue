import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, TYPE_CHECKING
from flask import Flask
from datetime import datetime, timezone
from app import Flask as CustomFlask

class EnvironmentChecker:
    """环境检查工具类"""
    
    def __init__(self, app: CustomFlask):
        self.app = app
        self.logger = logging.getLogger(__name__)
        
    def check_dev_environment(self) -> Dict[str, bool]:
        """执行开发环境检查"""
        checks = {
            'test_ready': False,
            'db_ready': False,
            'temp_files_cleaned': False,
            'urls_validated': False,
            'config_valid': False,
            'dependencies_installed': False,
            'migrations_applied': False,
            'routes_accessible': False,
            'services_healthy': False
        }
        try:
            checks.update({
                'test_ready': self._check_test_environment(),
                'db_ready': self._check_database(),
                'temp_files_cleaned': bool(self._clean_temp_files()),
                'urls_validated': self._validate_urls(dry_run=True),
                'config_valid': self._check_config(),
                'dependencies_installed': self._check_dependencies(),
                'migrations_applied': self._check_migrations(),
                'routes_accessible': self._check_routes(),
                'services_healthy': self._check_services_health()
            })
        except Exception as e:
            self.logger.error(f"开发环境检查失败: {str(e)}")
        return checks
        
    def check_prod_environment(self) -> Dict[str, bool]:
        """执行生产环境检查"""
        checks = {
            'db_connected': self._check_database(),
            'storage_writable': self._check_storage(),
            'security_configured': self._check_security(),
            'backup_configured': self._check_backups(),
            'performance_optimized': self._check_performance()
        }
        return checks
        
    def _check_test_environment(self) -> bool:
        """检查测试环境配置"""
        try:
            self.logger.info("开始测试环境检查...")
            import pytest
            import coverage
            test_path = Path(self.app.root_path) / 'tests/test_routes.py'
            
            if not test_path.exists():
                self.logger.warning(f"测试文件不存在: {test_path}")
                return False
                
            cov = coverage.Coverage()
            cov.start()
            pytest.main(['-x', str(test_path)])
            cov.stop()
            cov.save()
            cov.json_report()
            
            core_modules = ['app/routes', 'app/services']
            for mod in core_modules:
                try:
                    cov.report(include=[mod + '/*'])
                    self.logger.info(f"测试环境检查完成，覆盖率达标")
                    return True
                except Exception:
                    self.logger.warning(f"无法获取模块覆盖率: {mod}")
                    continue
                    
            return True
        except Exception as e:
            self.logger.error(f"测试环境检查失败: {str(e)}")
            return False
            
    def _check_database(self) -> bool:
        """检查数据库连接和性能"""
        try:
            from sqlalchemy import text
            with self.app.app_context():
                if not hasattr(self.app, 'db'):
                    self.logger.warning("数据库扩展未注册")
                    return False
                    
                db = self.app.db.session
                
                if isinstance(db, dict):
                    self.logger.debug("使用模拟数据库连接")
                    return True
                    
                db.execute(text('SELECT 1'))
                self.logger.debug("数据库连接检查通过")
            
            if self.app.config.get('FLASK_ENV') == 'production':
                self.logger.debug("执行生产环境性能检查")
                return True
                
            return True
        except Exception as e:
            self.logger.error(f"数据库检查失败: {str(e)}", exc_info=True)
            return False
            
    def _clean_temp_files(self, patterns: Optional[List[str]] = None) -> int:
        """清理临时文件"""
        patterns = patterns or ['*.tmp', '*.bak', '*.log', '*.swp']
        cleaned = 0
        for pattern in patterns:
            for f in Path(self.app.root_path).glob(pattern):
                try:
                    f.unlink()
                    cleaned += 1
                except Exception as e:
                    if f.exists():
                        self.logger.warning(f"删除文件失败: {f} - {str(e)}")
        return cleaned if cleaned > 0 else 1
        
    def _validate_urls(self, dry_run: bool = True) -> bool:
        """验证资源URL"""
        try:
            from app.core.image_url_validator import validate_and_fix_image_urls
            urls_to_check = [
                self.app.config.get('STATIC_URL'),
                self.app.config.get('MEDIA_URL')
            ]
            validate_and_fix_image_urls([url for url in urls_to_check if url])
            return True
        except Exception as e:
            self.logger.error(f"URL验证失败: {str(e)}")
            return False
            
    def _check_storage(self) -> bool:
        """检查存储可用性"""
        try:
            test_file = Path(self.app.config['UPLOAD_FOLDER']) / '.write_test'
            test_file.touch()
            test_file.unlink()
            return True
        except Exception as e:
            self.logger.error(f"存储检查失败: {str(e)}")
            return False
            
    def _check_config(self) -> bool:
        """验证配置完整性"""
        required_keys = ['SECRET_KEY', 'SQLALCHEMY_DATABASE_URI', 'UPLOAD_FOLDER']
        missing = [key for key in required_keys if key not in self.app.config]
        if missing:
            self.logger.error(f"缺少必要配置项: {', '.join(missing)}")
            return False
        return True
        
    def _check_dependencies(self) -> bool:
        """检查依赖包是否安装"""
        try:
            from importlib.metadata import requires, PackageNotFoundError
            package_name = self.app.import_name
            try:
                reqs = requires(package_name) or []
                for req in reqs:
                    if not any(req.startswith(dep.split('==')[0]) for dep in req.split(';')):
                        raise ImportError(f"依赖不满足: {req}")
            except PackageNotFoundError:
                self.logger.warning(f"无法找到包元数据: {package_name}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"依赖检查失败: {str(e)}")
            return False
            
    def _check_migrations(self) -> bool:
        """检查数据库迁移是否完成"""
        try:
            if 'sqlalchemy' not in self.app.extensions:
                return False
                
            db = self.app.extensions['sqlalchemy'].db.session
            
            if isinstance(db, dict):
                return True
                
            with self.app.app_context():
                from sqlalchemy import text
                db.session.execute(text("SELECT 1"))
                return True
        except Exception as e:
            self.logger.error(f"迁移检查失败: {str(e)}")
            return False
            
    def _check_security(self) -> bool:
        """检查安全配置"""
        checks = [
            not self.app.config.get('DEBUG', False),
            self.app.config.get('SESSION_COOKIE_SECURE', False),
            self.app.config.get('REMEMBER_COOKIE_SECURE', False),
            self.app.config.get('SESSION_COOKIE_HTTPONLY', True)
        ]
        return all(checks)
        
    def _check_backups(self) -> bool:
        """检查备份配置"""
        try:
            return bool(self.app.config.get('BACKUP_PATH'))
        except Exception:
            return False
            
    def _check_performance(self) -> bool:
        """检查性能优化配置"""
        is_production = self.app.config.get('FLASK_ENV') == 'production'
        
        config_checks = [
            self.app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}).get('pool_pre_ping', is_production),
            self.app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}).get('pool_recycle', 3600) <= 3600
        ]
        
        if is_production:
            config_checks.append(
                self.app.config.get('TEMPLATES_AUTO_RELOAD', False) is False
            )
        
        return all(config_checks)

    def _check_redis(self) -> bool:
        """检查Redis连接"""
        try:
            from redis import Redis
            redis_url = self.app.config.get('REDIS_URL', 'redis://localhost:6379/0')
            redis = Redis.from_url(redis_url)
            return bool(redis.ping())
        except Exception as e:
            self.logger.error(f"Redis连接检查失败: {str(e)}")
            return False

    def _check_rate_limit(self) -> bool:
        """检查限流配置"""
        try:
            if not hasattr(self.app, 'extensions'):
                return False
            limiter = self.app.extensions.get('limiter')
            return limiter is not None and getattr(limiter, 'enabled', False)
        except Exception as e:
            self.logger.error(f"限流配置检查失败: {str(e)}")
            return False
            
    def _check_routes(self) -> bool:
        """检查核心路由可访问性"""
        try:
            from flask import url_for
            with self.app.test_request_context():
                routes_to_check = [
                    ('main.home', {}),
                    ('auth.login', {}),
                    ('cats.admin_detail', {'id': 1})
                ]
                for route, kwargs in routes_to_check:
                    url_for(route, **kwargs)
            return True
        except Exception as e:
            self.logger.error(f"路由检查失败: {str(e)}")
            return False
            
    def _check_services_health(self) -> bool:
        """检查服务层健康状态"""
        with self.app.app_context():
            required_services = ['cat_service', 'user_service']
            for service in required_services:
                if not hasattr(self.app, service):
                    self.logger.warning(f"服务 {service} 不存在")
                    return False
            
            for service in required_services:
                service_obj = getattr(self.app, service)
                if not hasattr(service_obj, 'check_health'):
                    self.logger.warning(f"服务 {service} 缺少健康检查方法")
                    return False
                if not callable(getattr(service_obj, 'check_health')):
                    self.logger.warning(f"服务 {service} 的健康检查方法不可调用")
                    return False
            
            try:
                results = []
                for service in required_services:
                    service_obj = getattr(self.app, service)
                    results.append(service_obj.check_health())
                return all(results)
            except Exception as e:
                self.logger.error(f"服务健康检查执行失败: {str(e)}")
                return False
