# -*- coding: utf-8 -*-
import os
from babel.messages.extract import extract_from_dir
from babel.messages.pofile import write_po
from babel.messages.catalog import Catalog
from babel.util import parse_encoding

def main():
    # 设置提取参数
    method_map = [
        ('**.py', 'python'),
        ('**/templates/**.html', 'jinja2')
    ]
    options_map = {
        'jinja2': {
            'extensions': 'jinja2.ext.autoescape,jinja2.ext.with_'
        }
    }

    # 创建空的Catalog
    catalog = Catalog()

    # 排除目录和文件
    excluded_dirs = {'migrations', 'instance', 'logs', 'htmlcov', 'static', 'tests', 'venv'}
    excluded_files = {'.db', '.sqlite', '.jpg', '.png', '.ico', '.pyc', '.pyo', '.pyd', '.so'}
    excluded_extensions = {'.min.js', '.min.css'}

    # 提取消息并添加到Catalog
    for filename, lineno, message, comments, context in extract_from_dir(
        '.',
        method_map=method_map,
        options_map=options_map,
        keywords={'_': None, 'gettext': None, 'ngettext': (1, 2)},
        comment_tags=('NOTE:',),
        strip_comment_tags=True
    ):
        # 跳过排除的文件和目录
        if any(excluded_dir in filename.split(os.sep) for excluded_dir in excluded_dirs):
            continue
        if any(filename.endswith(ext) for ext in excluded_files):
            continue
        if any(filename.endswith(ext) for ext in excluded_extensions):
            continue
            
        try:
            # 检查文件是否为文本文件
            with open(filename, 'rb') as f:
                f.read(1024)  # 读取前1KB检查编码
            catalog.add(message, None, [(filename, lineno)], auto_comments=comments)
        except (UnicodeDecodeError, PermissionError, IsADirectoryError) as e:
            print(f"Skipping file {filename}: {str(e)}")
            continue

    # 写入PO文件
    with open('messages.pot', 'wb') as f:
        write_po(f, catalog)

if __name__ == '__main__':
    main()
