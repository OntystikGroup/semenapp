import logging
from os import getcwd
from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
from packed_image_editor import make_baw
import torch
from tools import predict
from api.models import ImageData
from PIL import Image
from io import BytesIO
import base64

model = torch.hub.load('./', 'custom', path='./model/best.pt', source='local', force_reload=True)
app = FastAPI(debug=True, description='API convert photo by model')
FORMAT = '%(asctime)s %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger('tcpserver')


@app.post('/use_model', response_class=JSONResponse)
async def use_model(file: UploadFile):
    global out_data
    delete()
    file_path = getcwd() + '/api/input_photo/' + file.filename
    logger.info(file_path)
    with open(file_path, 'wb') as image:
        content = await file.read()
        image.write(content)
        image.close()

    make_baw(input_path=file_path, output_path='api/baw_images/ready.jpeg')
    try:
        text, output_data = predict(
            input_model=model,
            save_dir='api/output_photo',
            img_path='api/baw_images/ready.jpeg',
            data=True
        )
        out_data = output_data
    except Exception as e:
        logger.error(e)
        return JSONResponse(status_code=422, content='Occurred error, try another file')

    image = Image.open(f"{getcwd()}/api/output_photo/ready.jpg")
    img_file = BytesIO()
    image.save(img_file, format='JPEG')
    img_bytes = base64.b64encode(img_file.getvalue())

    data = {
        'percent': str(round(out_data['percent'] * 100, 2)) + '%',
        'fragments': out_data['data'][0],
        'fragmented_degradeds': out_data['data'][2],
        'normals': out_data['data'][1],
        'img_bytes': img_bytes,
    }
    return JSONResponse(ImageData(**data).dict())


def delete():
    import os
    import shutil
    folder = 'api/input_photo'
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            logger.error('Failed to delete %s. Reason: %s' % (file_path, e))
