from openai import OpenAI
from pathlib import Path
from io import BytesIO
import base64
from PIL import Image
client = OpenAI(api_key="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")

# client.api_key = "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"

# user_prompt = input("What image do you want?\n")
user_prompt = "exactly one apple"
response = client.images.generate(
  model="dall-e-2",
  prompt=user_prompt,
  size="256x256",
  quality="standard",
  n=1,
  response_format='b64_json'
)

image_data = response.data[0].b64_json

# file_name = "test.png"
# with open(file_name, mode="wb") as file:
#     file.write(base64.b64decode(image_data))
    
im_bytes = base64.b64decode(image_data)   # im_bytes is a binary image
im_file = BytesIO(im_bytes)  # convert image to file-like object
img = Image.open(im_file)   # img is now PIL Image object
img.show()