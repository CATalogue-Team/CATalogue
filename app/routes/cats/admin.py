from flask import render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.decorators import admin_required

@admin_required
def list_cats():
    """管理员猫咪列表"""
    return current_app.cat_crud.list()

@admin_required
def get_cat(cat_id):
    """猫咪详情"""
    return current_app.cat_crud.detail(cat_id)

@admin_required
def create_cat():
    """创建猫咪"""
    return current_app.cat_crud.create()

@admin_required
def update_cat(cat_id):
    """编辑猫咪"""
    return current_app.cat_crud.edit(cat_id)

@admin_required
def delete_cat(cat_id):
    """删除猫咪"""
    return current_app.cat_crud.delete(cat_id)
