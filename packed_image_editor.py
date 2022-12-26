from PIL import Image, ImageEnhance


def make_baw(input_path='datasets/Semen-1/images/312312.jpg', output_path='baw_images/ready.jpeg'):
    img = Image.open(input_path)
    contrast = ImageEnhance.Contrast(img)
    r = contrast.enhance(1.5)
    thresh = 200
    def fn(x): return 255 if x > thresh else 0
    r = r.convert('1').point(fn, mode='1')
    r.save(fp=output_path)
    r.close()
    img.close()

