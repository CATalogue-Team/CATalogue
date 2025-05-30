# 业务常量定义

class CatConstants:
    """猫咪相关常量"""
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = ['jpg', 'png', 'jpeg', 'gif']
    DEFAULT_ITEMS_PER_PAGE = 10

class AppConstants:
    """应用通用常量"""
    CACHE_DEFAULT_TIMEOUT = 300  # 5分钟
    LOG_RETENTION_DAYS = 7
    MAX_REQUEST_SIZE = 16 * 1024 * 1024  # 16MB
