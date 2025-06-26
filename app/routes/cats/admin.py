from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.decorators import admin_required

@admin_required
def admin_cats_list():
    """管理员猫咪列表"""
    return current_app.cat_crud.list()

@admin_required
def admin_detail(cat_id):
    """猫咪详情"""
    return current_app.cat_crud.detail(cat_id)

@admin_required
def admin_cats_create():
    """创建猫咪"""
    return current_app.cat_crud.create()

@admin_required
def admin_cats_edit(cat_id):
    """编辑猫咪"""
    return current_app.cat_crud.edit(cat_id)

@admin_required
def admin_cats_delete(cat_id):
    """删除猫咪"""
    return current_app.cat_crud.delete(cat_id)
