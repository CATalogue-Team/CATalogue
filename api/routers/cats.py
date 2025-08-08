from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, status
from typing import List
from uuid import UUID
from ..models.cat import Cat, CatUpdate
from ..schemas.cat import CatCreate
from ..services.cat_service import CatService
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/api/v1/cats", tags=["cats"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.get("/", response_model=List[Cat])
async def list_cats(skip: int = 0, limit: int = 100):
    cats = await CatService.get_all_cats()
    return cats[skip:skip+limit]

@router.post("/", response_model=Cat, status_code=status.HTTP_201_CREATED)
async def create_cat(cat: CatCreate):
    return await CatService.create_cat(cat)

@router.get("/{cat_id}", response_model=Cat)
async def get_cat(cat_id: UUID):
    cat = await CatService.get_cat_by_id(cat_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    return cat

@router.put("/{cat_id}", response_model=Cat)
async def update_cat(cat_id: UUID, cat: CatUpdate):
    updated_cat = await CatService.update_cat(cat_id, cat.model_dump())
    if not updated_cat:
        raise HTTPException(status_code=404, detail="Cat not found")
    return updated_cat

@router.delete("/{cat_id}")
async def delete_cat(cat_id: UUID):
    success = await CatService.delete_cat(cat_id)
    if not success:
        raise HTTPException(status_code=404, detail="Cat not found")
    return {"message": "Cat deleted successfully"}

@router.post("/{cat_id}/photos")
async def upload_cat_photos(
    cat_id: UUID,
    files: List[UploadFile] = File(...),
    token: str = Depends(oauth2_scheme)
):
    """
    上传猫咪照片
    """
    if not files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No files uploaded"
        )
    
    # 验证文件类型
    allowed_types = ["image/jpeg", "image/png"]
    for file in files:
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type: {file.content_type}"
            )
    
    try:
        # 检查空文件名
        if not files[0].filename:
            raise ValueError("Empty filename not allowed")
            
        # 调用服务层上传照片
        result = await CatService.upload_photos(cat_id, files)
        return result
        
    except OSError as e:
        if "No space left on device" in str(e):
            raise HTTPException(
                status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                detail=str(e)
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
