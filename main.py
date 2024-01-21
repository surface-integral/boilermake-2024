from io import BytesIO
import base64
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import pandas as pd

import pytesseract

from openai import OpenAI

IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720

def get_text_from_image(filename: str):
    img = Image.open(filename)
    text = pytesseract.image_to_string(img)
    return text

def generate_subject_image(subject: str, filename=None) -> Image:
    client = OpenAI(api_key="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")
    
    prompt = "exactly one smiling cartoon " + subject
    print(prompt)
    response = client.images.generate(
        model="dall-e-2",
        prompt=prompt,
        size="512x512",
        quality="standard",
        n=1,
        response_format='b64_json',
        style="natural"
    )
    
    image_data = response.data[0].b64_json
    
    im_bytes = base64.b64decode(image_data)   # im_bytes is a binary image
    im_file = BytesIO(im_bytes)  # convert image to file-like object
    img = Image.open(im_file)    
    
    if filename:
        img.save(filename)
        return img
    
    return img

def multiply_subject_image(img, mult, set_width=IMAGE_WIDTH) -> Image:
    combined_image = np.hstack([img for _ in range(mult)])
    # combined_image = np.concatenate((combined_image, combined_image), axis=0)
    img = Image.fromarray(combined_image)
    new_height = int(img.size[1] / img.size[0] * set_width)
    img = img.resize((set_width, new_height))
    return img

def create_band(text: str, extra_length=100) -> np.array:
    ww = IMAGE_WIDTH
    hh = extra_length
    color = (255,255,255)
    whitebg = np.full((hh,ww,3), color, dtype=np.uint8)
    img = Image.fromarray(whitebg)
    I1 = ImageDraw.Draw(img)
    # Get the correct font size
    for i in range(32, -1, -1):
        font = ImageFont.truetype("/Users/aht_2004/boilermake-2024/fonts/comic-sans-ms/COMIC.ttf", 28, encoding="unic")
        text_length = I1.textlength(text=text, font=font)
        offset = (IMAGE_WIDTH - text_length) // 2
        if offset < 0:
            continue
    # Draw in question at the bottom of the image
    I1.text((offset, hh//5), text=text, fill=(0, 0, 0), stroke_width=0, font=font)
    return np.asarray(img)
    
    
def add_question_band(img: Image, question: str, extra_length=100) -> Image:
    band = create_band(question, extra_length)
    img = Image.fromarray(np.concatenate([np.asarray(img), band], axis=0))
    return img

def combine_images_vertically(image1: Image, image2: Image) -> Image:
    img1 = np.asarray(image1)
    img2 = np.asarray(image2)
    newImg = np.concatenate([img1, img2], axis=0)
    return Image.fromarray(newImg)

def generate_image(data: pd.DataFrame):
    if data['Type'] == "And":
        # Janet has 5 apples and 6 bananas in her basket. How many fruits does she have in total?
        subject_img1 = generate_subject_image(data['Subject1'])
        subject_img2 = generate_subject_image(data['Subject2'])
        
        multiplied1 = multiply_subject_image(subject_img1, data['Quantity1'])
        multiplied2 = multiply_subject_image(subject_img2, data['Quantity2'])
        
        combined = combine_images_vertically(multiplied1, multiplied2)
        img = add_question_band(combined, data['Question'])
        return img
    if data['Type'] == "more":
        # Janet has 6 apples more than Ellin. Ellin has 3 apples. How many apples does Janet have?
        subject_img1 = generate_subject_image(data['Subject1'])
        subject_img1 = multiply_subject_image(subject_img1, mult=data['Quantity1'])
        subject_img1 = add_question_band(subject_img1, "more than")
        
        subject_img2 = generate_subject_image(data['Subject2'])
        subject_img2 = multiply_subject_image(subject_img2, mult=data['Quantity2'])
        
        combined = combine_images_vertically(subject_img1, subject_img2)
        img = add_question_band(combined, "How many apples does Janet have?")
        return img
        

            
    