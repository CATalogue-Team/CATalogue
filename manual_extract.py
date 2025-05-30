# -*- coding: utf-8 -*-
import os
import re
from babel.messages.pofile import write_po
from babel.messages.catalog import Catalog

import chardet

def detect_encoding(filepath):
    """检测文件编码"""
    with open(filepath, 'rb') as f:
        rawdata = f.read(1024)
    return chardet.detect(rawdata)['encoding']

def extract_from_python(filepath):
    """从Python文件中提取gettext调用"""
    try:
        encoding = detect_encoding(filepath) or 'utf-8'
        with open(filepath, 'r', encoding=encoding) as f:
            content = f.read()
        
        # 匹配 _('...') 和 gettext('...') 调用
        pattern = r'[_\s]gettext\s*\(\s*[\'"](.*?)[\'"]\s*\)'
        return re.findall(pattern, content)
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")
        return []

def extract_from_html(filepath):
    """从HTML/Jinja2模板中提取翻译文本"""
    try:
        encoding = detect_encoding(filepath) or 'utf-8'
        with open(filepath, 'r', encoding=encoding) as f:
            content = f.read()
        
        # 匹配 {% trans %} 标签和 _('...') 调用
        trans_pattern = r'\{%\s*trans\s*%\}(.*?)\{%\s*endtrans\s*%\}'
        gettext_pattern = r'_\s*\(\s*[\'"](.*?)[\'"]\s*\)'
        return re.findall(trans_pattern, content) + re.findall(gettext_pattern, content)
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")
        return []

def main():
    catalog = Catalog()
    
    # 扫描Python文件
    for root, _, files in os.walk('.'):
        if any(excluded in root for excluded in ['migrations', 'instance', 'tests', 'venv']):
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                try:
                    for msg in extract_from_python(filepath):
                        catalog.add(msg, None, [(filepath, 0)])
                except Exception as e:
                    print(f"Skipping {filepath}: {str(e)}")
    
    # 扫描模板文件
    for root, _, files in os.walk('templates'):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                try:
                    for msg in extract_from_html(filepath):
                        catalog.add(msg, None, [(filepath, 0)])
                except Exception as e:
                    print(f"Skipping {filepath}: {str(e)}")
    
    # 写入PO文件
    with open('messages.pot', 'wb') as f:
        write_po(f, catalog)

if __name__ == '__main__':
    main()
