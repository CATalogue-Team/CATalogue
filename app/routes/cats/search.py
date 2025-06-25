from flask import Blueprint, render_template, request, make_response
from flask_login import login_required
from app import db
from app.services.cat_service import CatService

search_bp = Blueprint('search_cats', __name__)

@search_bp.route('/cats/search')
@login_required
def search():
    """搜索猫咪"""
    query = request.args.get('name')
    breed = request.args.get('breed')
    min_age = request.args.get('min_age', type=int)
    max_age = request.args.get('max_age', type=int)
    is_adopted = request.args.get('is_adopted', type=bool)
    
    cats = CatService(db).search(
        query=query,
        breed=breed,
        min_age=min_age,
        max_age=max_age,
        is_adopted=is_adopted
    )
    return render_template('search.html', cats=cats)

@search_bp.route('/cats/export')
@login_required
def export():
    """导出猫咪数据"""
    cats = CatService(db).search()
    csv_data = "id,name,breed,age,is_adopted\n" + "\n".join(
        [f"{cat.id},{cat.name},{cat.breed or ''},{cat.age},{cat.is_adopted}" 
         for cat in cats]
    )
    response = make_response(csv_data)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=cats.csv"
    return response
