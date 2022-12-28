from pydantic import BaseModel


class ImageData(BaseModel):
    percent: str
    fragments: int
    fragmented_degradeds: int
    normals: int
    img_bytes: str
