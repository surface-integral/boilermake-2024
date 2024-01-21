from io import BytesIO
import base64
from PIL import Image
import numpy as np

import pytesseract

from openai import OpenAI


def get_text_from_image(filename: str):
    img = Image.open(filename)
    text = pytesseract.image_to_string(img)
    return text

def generate_subject(subject: str) -> Image:
    client = OpenAI(api_key="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")
    
    prompt = "exactly one " + subject
    response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size="256x256",
        quality="standard",
        n=1,
        response_format='b64_json'
    )
    
    image_data = response.data[0].b64_json
    
    im_bytes = base64.b64decode(image_data)   # im_bytes is a binary image
    im_file = BytesIO(im_bytes)  # convert image to file-like object
    return Image.open(im_file)   # img is now PIL Image object

def add_white_band(img: Image, band_length=100) -> Image:
    w, h = img.size

    # Fill in white background
    ww = w
    hh = band_length
    color = (255,255,255)
    whitebg = np.full((hh,ww,3), color, dtype=np.uint8)
    
    img = np.concatenate([img, whitebg], axis=0)
    return Image.fromarray(img)


def generate_image(operation, subjects=None, name_to_string=None, subject_to_string=None, names=None):
    if operation == "and":
        # Janet has 5 apples and 6 bananas in her basket. How many fruits does she have in total?
        images = 
        
    elif operation == "more than":
    
    elif operation == "less than":
    