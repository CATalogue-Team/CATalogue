
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required
from ..models import Cat

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/search')
@login_required
def search():
    cats = Cat.query.order_by(Cat.created_at.desc()).limit(3).all()
    return render_template('search.html',
                        cats=cats,
                        no_results=False,
                        is_recommendation=bool(cats))
