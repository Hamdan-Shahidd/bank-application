from fastapi import APIRouter, Depends
from api.schemas import ImageGenRequest, ImageGenResponse
from api.auth import current_user
from core.imagegen import generate_image

router = APIRouter()


@router.post("/image/generate", response_model=ImageGenResponse)
def image_generate(body: ImageGenRequest, user=Depends(current_user)):
    result = generate_image(user.user_id, body.prompt)
    return ImageGenResponse(**result)