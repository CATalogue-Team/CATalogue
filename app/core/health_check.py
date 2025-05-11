
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional
import logging
from flask import Flask
from datetime import datetime

class EnvironmentChecker:
    """环境检查与初始化工具"""
    
    def __init__(self, app: Flask):
        self.app = app
        self.logger = logging.getLogger(__name__)
        
    def check_dev_environment(self) -> Dict[str, bool]:
        """执行开发环境检查"""
        checks = {
            'test_ready': self._check_test_environment(),
            'db_ready': self._check_database(),
            'temp_files_cleaned': self._clean_temp_files(),
            'urls_validated': self._validate_urls(dry_run=True),
            'config_valid': self._check_config(),
            'dependencies_installed': self._check_dependencies(),
            'migrations_applied': self._check_migrations(),
            'routes_accessible': self._check_routes(),
            'services_healthy': self._check_services_health()
        }
        return checks
        
    def check_prod_environment(self) -> Dict[str, bool]:
        """执行生产环境检查"""
        checks = {
            'db_connected': self._check_database(),
            'storage_writable': self._check_storage(),
            'essential_services': self._check_services(),
            'security_configured': self._check_security(),
            'backup_configured': self._check_backups(),
            'performance_optimized': self._check_performance()
        }
        return checks
        
    def _check_test_environment(self) -> bool:
        """检查测试环境配置"""
        try:
            import pytest
            import coverage
            test_path = Path(__file__).parent.parent / 'tests/test_routes.py'
            
            # 检查测试文件存在性
            if not test_path.exists():
                return False
                
            # 检查测试覆盖率
            cov = coverage.Coverage()
            cov.start()
            
            # 执行核心测试
            pytest.main(['-x', str(test_path)])
            
            cov.stop()
            cov.save()
            
            # 获取覆盖率报告
            cov.json_report()
            data = cov.get_data()
            line_cover = data.line_counts()
            
            # 要求核心模块覆盖率>80%
            core_modules = ['app/routes', 'app/services']
            for mod in core_modules:
                if mod in line_cover and line_cover[mod] < 80:
                    return False
                    
            return True
        except Exception as e:
            self.logger.error(f"测试环境检查失败: {str(e)}")
            return False
            
    def _check_database(self) -> bool:
        """检查数据库连接和性能"""
        try:
            # 基础连接检查
            self.app.db.session.execute('SELECT 1')
            
            # 性能检查 (仅生产环境)
            if self.app.config['FLASK_ENV'] == 'production':
                from sqlalchemy import text
                
                # 检查慢查询
                slow_queries = self.app.db.session.execute(text("""
                    SELECT COUNT(*) 
                    FROM pg_stat_activity 
                    WHERE state = 'active' 
                    AND now() - query_start > interval '500ms'
                """)).scalar()
                
                # 检查连接池使用率
                conn_usage = self.app.db.session.execute(text("""
                    SELECT COUNT(*) 
                    FROM pg_stat_activity 
                    WHERE usename = current_user
                """)).scalar()
                
                max_conn = self.app.config.get(
                    'SQLALCHEMY_ENGINE_OPTIONS', {}
                ).get('pool_size', 5)
                
                return slow_queries == 0 and conn_usage < max_conn * 0.8
                
            return True
        except Exception as e:
            self.logger.error(f"数据库检查失败: {str(e)}")
            return False
            
    def _clean_temp_files(self, patterns: Optional[List[str]] = None) -> int:
        """清理临时文件"""
        patterns = patterns or ['*.tmp', '*.bak', '*.log', '*.swp']
        cleaned = 0
        for pattern in patterns:
            for f in Path('.').glob(pattern):
                try:
                    f.unlink()
                    cleaned += 1
                except Exception as e:
                    self.logger.warning(f"删除文件失败: {f.name} - {str(e)}")
        return cleaned
        
    def _validate_urls(self, dry_run: bool = True) -> bool:
        """验证资源URL"""
        try:
            from image_url_validator import validate_and_fix_image_urls
            validate_and_fix_image_urls(dry_run=dry_run)
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
            import pkg_resources
            with open('requirements.txt') as f:
                requirements = pkg_resources.parse_requirements(f)
                for req in requirements:
                    pkg_resources.require(str(req))
            return True
        except Exception as e:
            self.logger.error(f"依赖检查失败: {str(e)}")
            return False
            
    def _check_migrations(self) -> bool:
        """检查数据库迁移是否完成"""
        try:
            from flask_migrate import Migrate
            migrate = Migrate()
            migrate.init_app(self.app, self.app.db)
            return migrate.compare_metadata()
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
        # 基础配置检查
        config_checks = [
            self.app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}).get('pool_pre_ping', False),
            self.app.config.get('SQLALCHEMY_ENGINE_OPTIONS', {}).get('pool_recycle', 3600) <= 3600,
            self.app.config.get('TEMPLATES_AUTO_RELOAD', False) is False
        ]
        
        # API响应时间检查
        try:
            from app.models import RequestLog
            recent_logs = RequestLog.query.order_by(
                RequestLog.timestamp.desc()
            ).limit(100).all()
            
            if recent_logs:
                avg_response_time = sum(
                    log.duration for log in recent_logs
                ) / len(recent_logs)
                
                # 平均响应时间应<500ms
                config_checks.append(avg_response_time < 0.5)
                
        except Exception as e:
            self.logger.warning(f"性能数据获取失败: {str(e)}")
            
        return all(config_checks)
        
    def save_check_results(self, results: Dict[str, bool]):
        """保存检查结果到数据库"""
        try:
            from app.models import EnvironmentCheck
            check = EnvironmentCheck(
                environment=self.app.config['FLASK_ENV'],
                results=results,
                timestamp=datetime.utcnow()
            )
            self.app.db.session.add(check)
            self.app.db.session.commit()
            return True
        except Exception as e:
            self.logger.error(f"保存检查结果失败: {str(e)}")
            return False
            
    def run_auto_repair(self, checks: Dict[str, bool]) -> Dict[str, bool]:
        """自动修复失败的检查项"""
        repaired = {}
        for check_name, passed in checks.items():
            if not passed:
                try:
                    if check_name == 'dependencies_installed':
                        self._install_dependencies()
                        repaired[check_name] = True
                    elif check_name == 'migrations_applied':
                        self._apply_migrations()
                        repaired[check_name] = True
                    elif check_name == 'temp_files_cleaned':
                        self._clean_temp_files()
                        repaired[check_name] = True
                    elif check_name == 'urls_validated':
                        self._validate_urls(dry_run=False)
                        repaired[check_name] = True
                    elif check_name == 'config_valid':
                        self._repair_missing_config()
                        repaired[check_name] = True
                    elif check_name == 'performance_optimized':
                        self._optimize_performance()
                        repaired[check_name] = True
                    else:
                        repaired[check_name] = False
                except Exception as e:
                    self.logger.error(f"自动修复 {check_name} 失败: {str(e)}")
                    repaired[check_name] = False
        return repaired
        
    def _optimize_performance(self):
        """性能优化自动修复"""
        # 数据库优化
        if self.app.config['FLASK_ENV'] == 'production':
            from sqlalchemy import text
            self.app.db.session.execute(text("""
                ANALYZE VERBOSE;
                VACUUM FULL VERBOSE;
            """))
            self.app.db.session.commit()
            
        # 缓存清理
        if 'cache' in self.app.extensions:
            self.app.extensions['cache'].clear()
        
    def _repair_missing_config(self):
        """修复缺失的配置项"""
        from flask import current_app
        if 'SECRET_KEY' not in current_app.config:
            current_app.config['SECRET_KEY'] = os.urandom(24).hex()
        if 'UPLOAD_FOLDER' not in current_app.config:
            os.makedirs('uploads', exist_ok=True)
            current_app.config['UPLOAD_FOLDER'] = 'uploads'
        
    def _install_dependencies(self):
        """安装缺失的依赖"""
        import subprocess
        subprocess.run(['pip', 'install', '-r', 'requirements.txt'], check=True)
        
    def _check_routes(self) -> bool:
        """检查核心路由可访问性"""
        try:
            from flask import url_for
            with self.app.test_request_context():
                routes_to_check = [
                    'main.home',
                    'auth.login',
                    'cats.detail'
                ]
                for route in routes_to_check:
                    url_for(route)
            return True
        except Exception as e:
            self.logger.error(f"路由检查失败: {str(e)}")
            return False
            
    def _check_services_health(self) -> bool:
        """检查服务层健康状态"""
        try:
            services = [
                self.app.extensions.get('cat_service'),
                self.app.extensions.get('user_service')
            ]
            return all(service is not None for service in services)
        except Exception as e:
            self.logger.error(f"服务检查失败: {str(e)}")
            return False
            
    def _apply_migrations(self):
        """应用数据库迁移"""
        from flask_migrate import upgrade
        with self.app.app_context():
            upgrade()
            
    def register_cli_commands(self):
        """注册CLI命令"""
        import click
        @click.command('check-env')
        @click.option('--repair', is_flag=True, help='自动修复问题')
        def check_env(repair):
            """执行环境检查"""
            click.echo("执行环境检查...")
            if self.app.config['FLASK_ENV'] == 'development':
                checks = self.check_dev_environment()
            else:
                checks = self.check_prod_environment()
                
            if repair:
                self.run_auto_repair(checks)
                
            for check, passed in checks.items():
                color = 'green' if passed else 'red'
                click.echo(click.style(
                    f"{'✓' if passed else '✗'} {check.replace('_', ' ')}",
                    fg=color))
                
        self.app.cli.add_command(check_env)
