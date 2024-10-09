from fastapi import APIRouter
import base64
from io import BytesIO
from .ai import analyze_image
from .schema import ImageData
from PIL import Image

router=APIRouter(
    prefix="/api/v1/compute"
)

@router.post('/')
async def run(data: ImageData):
    # print(data)
    image_data = base64.b64decode(data.image.split(",")[1])
    image_bytes = BytesIO(image_data)
    image = Image.open(image_bytes)
    responses = analyze_image(image, dict_of_vars=data.dict_of_vars)
    data = []
    for response in responses:
        data.append(response)
    print('response in route: ', response)
    return {"message": "Image processed", "data": data, "status": "success"}
