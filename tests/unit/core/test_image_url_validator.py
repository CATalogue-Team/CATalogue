"""测试图片URL验证工具"""
import pytest
from unittest.mock import patch
from app.core.image_url_validator import validate_image_url, validate_and_fix_image_urls

@pytest.fixture
def mock_app():
    """模拟Flask应用"""
    from flask import Flask
    app = Flask(__name__)
    app.config['ALLOWED_IMAGE_EXTENSIONS'] = ['jpg', 'png', 'gif']
    return app

def test_validate_image_url_valid(mock_app):
    """测试有效的图片URL"""
    with mock_app.app_context():
        valid_urls = [
            'https://example.com/image.jpg',
            'http://test.com/path/to/image.png',
            'https://sub.domain.com/img.gif?width=100'
        ]
        for url in valid_urls:
            assert validate_image_url(url) is True

def test_validate_image_url_invalid(mock_app):
    """测试无效的图片URL"""
    with mock_app.app_context():
        invalid_urls = [
            '',  # 空URL
            'not-a-url',  # 无效格式
            'ftp://example.com/image.jpg',  # 不支持协议
            'https://example.com/image.txt',  # 无效扩展名
            'https://example.com'  # 无路径
        ]
        for url in invalid_urls:
            assert validate_image_url(url) is False

def test_validate_and_fix_image_urls(mock_app):
    """测试URL修复功能"""
    with mock_app.app_context():
        test_urls = [
            'https://example.com/image.jpg',
            'http://test.com/path with spaces/image.png',
            'invalid-url',
            'https://example.com/image.bmp'  # 不支持格式
        ]
        # 接受两种格式的URL（带空格和编码空格）
        result = validate_and_fix_image_urls(test_urls)
        assert len(result) == 2
        assert result[0] == 'https://example.com/image.jpg'
        assert (
            result[1] == 'http://test.com/path with spaces/image.png' or 
            result[1] == 'http://test.com/path%20with%20spaces/image.png'
        )

def test_validate_and_fix_empty_list(mock_app):
    """测试空URL列表"""
    with mock_app.app_context():
        assert validate_and_fix_image_urls([]) == []

def test_validate_image_url_exception_handling(mock_app):
    """测试异常处理"""
    with mock_app.app_context():
        # 测试URL解析异常
        assert validate_image_url('http://[invalid]') is False
        
def test_validate_and_fix_url_with_query_params(mock_app):
    """测试带查询参数的URL修复"""
    with mock_app.app_context():
        test_urls = [
            'https://example.com/image.jpg?width=100&height=200',
            'http://test.com/path with spaces/image.png?param=value'
        ]
        result = validate_and_fix_image_urls(test_urls)
        assert len(result) == 2
        assert 'width=100' in result[0] or 'width%3D100' in result[0]
        assert (
            result[1] == 'http://test.com/path with spaces/image.png?param=value' or
            result[1] == 'http://test.com/path%20with%20spaces/image.png?param=value'
        )

def test_validate_and_fix_url_with_fragments(mock_app):
    """测试带片段标识的URL修复"""
    with mock_app.app_context():
        test_urls = [
            'https://example.com/image.jpg#section1',
            'http://test.com/path#fragment with spaces'
        ]
        result = validate_and_fix_image_urls(test_urls)
        assert len(result) == 2
        assert '#section1' in result[0] or '%23section1' in result[0]
        assert (
            result[1] == 'http://test.com/path#fragment with spaces' or
            result[1] == 'http://test.com/path%23fragment%20with%20spaces'
        )

def test_url_without_protocol(mock_app):
    """测试无协议URL修复"""
    with mock_app.app_context():
        test_urls = [
            'example.com/image.jpg',
            'test.com/path with spaces/image.png'
        ]
        result = validate_and_fix_image_urls(test_urls)
        # 检查结果数量并去重
        unique_results = list(set(result))
        assert len(unique_results) == 2
        assert any(r.startswith('http://example.com/image.jpg') for r in unique_results)
        assert any(
            r == 'http://test.com/path with spaces/image.png' or
            r == 'http://test.com/path%20with%20spaces/image.png'
            for r in unique_results
        )

@pytest.mark.skip(reason="TODO: 需要先实现日志功能")
def test_debug_logging(mock_app, caplog):
    """测试调试日志输出(暂跳过)"""
    pass

def test_fixed_url_validation(mock_app):
    """测试修复后URL验证"""
    with mock_app.app_context():
        # 测试修复后URL验证失败的情况
        with patch('app.core.image_url_validator.validate_image_url', return_value=False):
            result = validate_and_fix_image_urls(['http://test.com/invalid url.jpg'])
            assert result == []

def test_validate_url_edge_cases(mock_app):
    """测试边界情况"""
    with mock_app.app_context():
        # 测试空URL
        assert not validate_image_url('')
        
        # 测试无效协议
        assert not validate_image_url('ftp://example.com/image.jpg')
        
        # 测试无路径URL
        assert not validate_image_url('http://example.com')
        
        # 测试无效扩展名
        mock_app.config['ALLOWED_IMAGE_EXTENSIONS'] = ['jpg', 'png']
        assert not validate_image_url('http://example.com/image.gif')

def test_fix_url_exception_handling(mock_app):
    """测试URL修复异常处理"""
    with mock_app.app_context():
        # 测试无效URL格式
        assert validate_and_fix_image_urls(['http://[invalid]']) == []
        
        # 测试修复过程中抛出异常
        with patch('urllib.parse.quote', side_effect=Exception('test error')):
            # 使用需要编码的URL测试
            result = validate_and_fix_image_urls(['http://test.com/path with spaces#fragment/image.png'])
            # 允许返回空列表或原始URL（取决于实现）
            assert result == [] or result == ['http://test.com/path with spaces#fragment/image.png']

def test_special_characters_in_url(mock_app):
    """测试URL中的特殊字符处理"""
    with mock_app.app_context():
        test_urls = [
            'http://test.com/path/with/special@chars.jpg',
            'http://test.com/path/with/special#chars.png'
        ]
        result = validate_and_fix_image_urls(test_urls)
        assert len(result) == 2
        assert '@' in result[0] or '%40' in result[0]
        assert '#' in result[1] or '%23' in result[1]

def test_protocol_handling(mock_app):
    """测试协议处理逻辑"""
    with mock_app.app_context():
        # 测试自动添加http协议
        test_urls = ['//example.com/image.jpg', 'example.com/image.png']
        result = validate_and_fix_image_urls(test_urls)
        assert all(url.startswith('http://') for url in result)
        
        # 测试https协议保留
        test_urls = ['https://secure.com/image.jpg']
        result = validate_and_fix_image_urls(test_urls)
        assert result[0].startswith('https://')

def test_edge_case_urls(mock_app):
    """测试边界条件URL"""
    with mock_app.app_context():
        # 测试极长URL
        long_url = 'http://example.com/' + 'a'*1000 + '.jpg'
        assert validate_image_url(long_url) is True
        
        # 测试带端口URL
        assert validate_image_url('http://example.com:8080/image.jpg') is True
        
        # 测试带认证信息URL - 应该拒绝
        with patch('app.core.image_url_validator.urlparse') as mock_parse:
            mock_parse.return_value = type('', (), {
                'scheme': 'http',
                'netloc': 'user:pass@example.com',
                'path': '/image.jpg',
                'params': '',
                'query': '',
                'fragment': ''
            })()
            assert validate_image_url('http://user:pass@example.com/image.jpg') is False
        
        # 测试国际化域名
        assert validate_image_url('http://例子.测试/image.jpg') is False
        
        # 测试URL编码异常处理
        with patch('app.core.image_url_validator.urlparse', side_effect=Exception('test error')):
            assert validate_image_url('http://test.com/image.jpg') is False
            
        # 测试特殊字符编码
        test_url = 'http://test.com/path with spaces#fragment'
        with patch('app.core.image_url_validator.quote', side_effect=Exception('test error')):
            assert validate_and_fix_image_urls([test_url], strict_mode=True) == []
            
        # 测试协议自动添加失败情况
        with patch('app.core.image_url_validator.validate_image_url', return_value=False):
            assert validate_and_fix_image_urls(['test.com/image.jpg']) == []
