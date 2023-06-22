import logging
import os
from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from packed_image_editor import make_baw
import torch
from tools import predict
from api.api_tools import save_input_photo
from api.constants import (BAW_IMAGES_FOLDER_PATH, INPUT_PHOTO_FOLDER_PATH, OUTPUT_PHOTO_FOLDER_PATH,
                           BAW_IMAGES_FOLDER_FULL_PATH, INPUT_PHOTO_FOLDER_FULL_PATH, OUTPUT_PHOTO_FOLDER_FULL_PATH)
from api.models import ImageData
from PIL import Image
from io import BytesIO
import base64

model = torch.hub.load('./', 'custom', path='./model/best.pt', source='local', force_reload=True)
app = FastAPI(debug=False, description='API convert photo by model')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('logger')


def input_photo_name():
    folder_filenames = os.listdir('api/input_photo')
    return folder_filenames[0]


@app.post('/use_model', response_class=JSONResponse)
async def use_model(file: UploadFile):
    await save_input_photo(file)
    make_baw(input_path='/' + INPUT_PHOTO_FOLDER_FULL_PATH + file.filename, output_path=BAW_IMAGES_FOLDER_FULL_PATH + file.filename)
    output_data = dict(data=[], percent=0.0)
    try:
        text, output_data = predict(
            input_model=model,
            save_dir=OUTPUT_PHOTO_FOLDER_FULL_PATH,
            img_path=BAW_IMAGES_FOLDER_FULL_PATH + file.filename,
            data=True
        )
        logger.info('Prediction succeed!')
    except Exception as e:
        logger.error(e)
        file_format = '.' + file.filename.split('.')[-1]
        return JSONResponse(status_code=422, content=f'Occurred error with {file_format}, try another file format')

    image = Image.open(f"{OUTPUT_PHOTO_FOLDER_FULL_PATH}" + file.filename)
    img_file = BytesIO()
    image.save(img_file, format='JPEG')
    img_bytes = base64.b64encode(img_file.getvalue())

    delete(filename=file.filename)

    data = {
        'filename': file.filename,
        'percent': str(round(output_data.get('percent') * 100, 2)) + '%',
        'fragments': output_data['data'][0],
        'fragmented_degradeds': output_data['data'][2],
        'normals': output_data['data'][1],
        'img_bytes': img_bytes,
    }
    return JSONResponse(ImageData(**data).dict())


def delete(filename: str):
    import os

    input_file_path = os.path.join(INPUT_PHOTO_FOLDER_FULL_PATH, filename)
    output_file_path = os.path.join(OUTPUT_PHOTO_FOLDER_FULL_PATH, filename)
    baw_file_path = os.path.join(BAW_IMAGES_FOLDER_FULL_PATH, filename)

    if os.path.exists(input_file_path):
        os.remove(input_file_path)
    if os.path.exists(output_file_path):
        os.remove(output_file_path)

    if os.path.exists(baw_file_path):
        os.remove(baw_file_path)

    logger.info('%s deleted from all folders', filename)
