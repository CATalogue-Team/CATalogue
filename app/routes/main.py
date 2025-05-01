
from flask import Blueprint, render_template, redirect, url_for, jsonify
from flask_login import login_required
from ..services.cat_service import CatService

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/search')
@login_required
def search():
    cats = CatService.get_recent_cats(limit=3)
    return render_template('search.html',
                        cats=cats,
                        no_results=False,
                        is_recommendation=bool(cats))

@bp.route('/ping')
def ping():
    """测试路由"""
    return jsonify({'status': 'ok', 'message': 'pong'})
