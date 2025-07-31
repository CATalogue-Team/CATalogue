from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import List
from ..models.cat import Cat, CatCreate, CatUpdate
from ..services.cat_service import CatService

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login")

@router.get("/", response_model=List[Cat])
async def list_cats(
    skip: int = 0, 
    limit: int = 100,
    token: str = Depends(oauth2_scheme)
):
    return await CatService.list_cats(skip, limit)

@router.post("/", response_model=Cat)
async def create_cat(
    cat: CatCreate,
    token: str = Depends(oauth2_scheme)
):
    return await CatService.create_cat(cat)

@router.get("/{cat_id}", response_model=Cat)
async def get_cat(
    cat_id: str,
    token: str = Depends(oauth2_scheme)
):
    cat = await CatService.get_cat(cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    return cat

@router.put("/{cat_id}", response_model=Cat)
async def update_cat(
    cat_id: str,
    cat: CatUpdate,
    token: str = Depends(oauth2_scheme)
):
    updated_cat = await CatService.update_cat(cat_id, cat)
    if not updated_cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    return updated_cat

@router.delete("/{cat_id}")
async def delete_cat(
    cat_id: str,
    token: str = Depends(oauth2_scheme)
):
    success = await CatService.delete_cat(cat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cat not found")
    return {"message": "Cat deleted successfully"}
