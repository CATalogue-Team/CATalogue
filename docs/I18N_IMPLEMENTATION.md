# CATalogue 多语言实现指南

## 1. Flask-Babel 集成

### 安装依赖
```bash
pip install flask-babel
```

### 初始化配置(app/extensions.py)
```python
from flask_babel import Babel

babel = Babel()

def init_app(app):
    babel.init_app(app)
    app.config['BABEL_DEFAULT_LOCALE'] = 'zh'
    app.config['BABEL_TRANSLATION_DIRECTORIES'] = 'translations'
```

### 添加语言选择器(模板中)
```html
<div class="language-switcher">
  <a href="?lang=zh">中文</a> | 
  <a href="?lang=en">English</a>
</div>
```

## 2. 翻译文件结构
```
translations/
  zh/LC_MESSAGES/
    messages.po
    messages.mo
  en/LC_MESSAGES/
    messages.po  
    messages.mo
```

## 3. 模板改造指南

### 文本提取示例
```html
<!-- 改造前 -->
<h1>猫咪信息中心</h1>

<!-- 改造后 -->  
<h1>{{ _('Cat Information Center') }}</h1>
```

### 复数处理
```html
{{ ngettext('%(num)d cat', '%(num)d cats', count) }}
```

## 4. Python代码国际化

### 常规文本
```python
from flask_babel import gettext as _

flash(_('Cat added successfully!'))
```

### 带变量的文本
```python
_('Hello, %(name)s!', name=user.name)
```

## 5. 翻译流程

1. 提取文本
```bash
pybabel extract -F babel.cfg -o messages.pot .
```

2. 创建翻译文件
```bash 
pybabel init -i messages.pot -d translations -l zh
```

3. 编译翻译
```bash
pybabel compile -d translations
```

4. 更新翻译
```bash
pybabel update -i messages.pot -d translations
