from fastapi import UploadFile
from api.constants import INPUT_PHOTO_FOLDER_FULL_PATH


async def save_input_photo(file: UploadFile):
    filename = file.filename
    file_path = INPUT_PHOTO_FOLDER_FULL_PATH + filename
    with open(file_path, 'wb') as image:
        content = await file.read()
        image.write(content)
