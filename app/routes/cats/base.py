from flask import Blueprint
from app import db
from app.services.cat_service import CatService
from app.core.base_crud import BaseCRUD

bp = Blueprint('cats', __name__, url_prefix='/cats')

# 初始化BaseCRUD
cat_crud = BaseCRUD(
    service=CatService(db),
    model_name='cat',
    list_template='search.html',
    detail_template='cat_detail.html',
    edit_template='edit_cat.html',
    list_route='cats.admin_cats_list',
    detail_route='cats.admin_detail',
    create_route='cats.admin_cats_create',
    edit_route='cats.admin_cats_edit',
    delete_route='cats.admin_cats_delete'
)
