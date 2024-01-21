from io import BytesIO
import os
from base64 import b64encode
import base64
from PIL import Image, ImageFont, ImageDraw
import numpy as np

import pytesseract
import spacy
from textblob import TextBlob

from openai import OpenAI

IMAGE_WIDTH = 1280
IMAGE_HEIGHT = 720

from pathlib import Path

PATH = str(Path(os.getcwd()).parent.absolute())
print(PATH)

def entry_point(prompt: str):
    output = analyze_prompt(prompt, operation="Addition", problem_type=get_question_type(prompt))
    print(output)
    img = generate_image(output)
    # image_io = BytesIO()
    # img.save(image_io, 'PNG')
    # dataurl = 'data:image/png;base64,' + b64encode(image_io.getvalue()).decode('ascii')
    return img
    
def get_question_type(question: str):
    if (('more' in question) | ('than' in question)):
        return "More Than"
    elif (('and' in question) | ('another' in question) | ('total' in question) | ('altogether' in question)):
        return "And"
    else: 
        return "Original Amount"

def get_text_from_image(filename: str):
    img = Image.open(filename)
    text = pytesseract.image_to_string(img)
    return text

def generate_subject_image(subject: str, 
                           filename=None, 
                           create_variation=False, 
                           vary_img=None, 
                           debug=False) -> Image:
    client = OpenAI(api_key="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")
    
    prompt = "exactly one singular cartoon " + subject
    if debug:
        print(prompt)
    if create_variation:
        # Converting the image object into bytes array
        img_byte_arr = BytesIO()
        vary_img.save(img_byte_arr, format='PNG')
        vary_img = img_byte_arr.getvalue()
        
        if debug:
            print("Creating a variation...")
            
        response = client.images.create_variation(
            image=vary_img,
            model="dall-e-2", 
            size="512x512",
            n=1,
            response_format='b64_json',
        )
    else:
        if debug:
            print("Creating a new image...")
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
    # for i in range(32, 0, -1):
    #     font = ImageFont.truetype(str(PATH) + "/fonts/comic-sans-ms/COMIC.TTF", i, encoding="unic")
    #     text_length = I1.textlength(text=text, font=font)
    #     offset = (IMAGE_WIDTH - text_length) // 2
    #     if offset < 0:
    #         continue
    font = ImageFont.truetype(str(PATH) + "/fonts/comic-sans-ms/COMIC.TTF", 28, encoding="unic")
    text_length = I1.textlength(text=text, font=font)
    offset = (IMAGE_WIDTH - text_length) // 2
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

def generate_image(data: dict, debug=False):
    for key in data.keys():
        data[key] = data[key].strip()
    
    if data['Type'] == "And":
        # Janet has 5 apples and 6 bananas in her basket. How many fruits does she have in total?
        subject_img1 = generate_subject_image(data['Subject1'], debug=debug)
        if data['Subject1'] == data['Subject2']:
            subject_img2 = generate_subject_image(data['Subject2'], 
                                                  create_variation=True, 
                                                  vary_img=subject_img1, 
                                                  debug=debug)    
        else:
            subject_img2 = generate_subject_image(data['Subject2'], debug=debug)
        
        multiplied1 = multiply_subject_image(subject_img1, mult=int(data['Quantity1']))
        multiplied2 = multiply_subject_image(subject_img2, mult=int(data['Quantity2']))
        
        combined = combine_images_vertically(multiplied1, multiplied2)
        img = add_question_band(combined, data['Question'])
        return img
    
    if data['Type'] == "More than":
        # Janet has 6 apples more than Ellin. Ellin has 3 apples. How many apples does Janet have?
        subject_img1 = generate_subject_image(data['Subject1'])
        if data['Subject1'] == data['Subject2']:
            subject_img2 = generate_subject_image(data['Subject2'], 
                                                  create_variation=True, 
                                                  vary_img=subject_img1, 
                                                  debug=debug)    
        else:
            subject_img2 = generate_subject_image(data['Subject2'])
            
        subject_img1 = multiply_subject_image(subject_img1, mult=int(data['Quantity1']))
        subject_img1 = add_question_band(subject_img1, "more than")
        
        subject_img2 = multiply_subject_image(subject_img2, mult=int(data['Quantity2']))
        
        combined = combine_images_vertically(subject_img1, subject_img2)
        img = add_question_band(combined, data['Question'])
        img.show()
        return img

def analyze_prompt(question: str, operation: str, problem_type: str): 
    output = {"Question":"", "Subject1":"", "Quantity1":"", "Subject2":"", "Quantity2":"", "Operation":"", "Type":""}
    output["Operation"] = operation
    output["Type"] = problem_type

    NER = spacy.load("en_core_web_sm")

    doc = NER(question)

    sents = [] 
    subject = ""
    quantity = ""
    for sent in doc.sents: 
        sents.append(sent)
    output["Question"] = sents[-1].text
    for sent in sents[:len(sents)-1]:
        for token in sent:
            if(token.pos_ == "NUM") and (output["Quantity1"] != ""):
                output["Quantity2"] = token.text
            if (token.dep_ == "nummod"): 
                subtree = list(token.subtree)
                start = subtree[0].i
                end = subtree[-1].i + 1
                j = 1
                for token2 in doc[end:]:
                    if not subject:
                        if token2.pos_ == "NOUN":
                            for token3 in doc[end:end+j]:
                                subject += token3.text+" "
                            break; 
                j += 1 
                quantity = doc[start:end].text
                if output["Quantity1"] == "":
                    output["Quantity1"] = quantity
                else: 
                    output["Quantity2"] = quantity

                if output["Subject1"] == "":
                    output["Subject1"] = subject
                else: 
                    output["Subject2"] = subject
            if (not subject) and (not quantity):
                if (("subj" in token.dep_) or ("dobj" in token.dep_)):
                    subtree = list(token.subtree)
                    start = subtree[0].i
                    end = subtree[-1].i + 1
                    adj = ""
                    contains_num = [True if "NUM" == token.pos_ else False for token in doc[start:end]]
                    contains_noun = [True if "NOUN" == token.pos_ else False for token in doc[start:end]]
                    k = 0 
                    seg1 = doc[start:end]
                    seg2 = ""
                    for token in doc[start:end]:
                        if (token.pos_ == "CCONJ"): 
                            if True in [True if "NUM" == token.pos_ else False for token in doc[k+1:]]: 
                                seg1 = doc[start:end][:k]
                                seg2 = doc[start:end][k+1:]
                        k += 1 
                    for seg in (seg1, seg2): 
                        if seg: 
                            if ((True in contains_num) and (True in contains_noun)):
                                for token in seg[:contains_noun.index(True)+1]:
                                    if (token.pos_ == "NUM"): 
                                        quantity = token.text
                                        if output["Quantity1"] == "":
                                            output["Quantity1"] = quantity
                                        else: 
                                            output["Quantity2"] = quantity
                                    if ((token.pos_ == "ADJ") and (token.text != "more")): 
                                        adj = token.text + " "
                                    if ((token.pos_ == "NOUN")):   # filter to only nouns 
                                        print(f"Token tag: {token.tag_}")
                                        #Singularize token subjects
                                        if token.tag_ == "NNS":
                                            subject = adj + TextBlob(token.text).words[0].singularize()
                                        else:
                                            subject = adj + token.text
                                        if output["Subject1"] == "":
                                            output["Subject1"] = subject
                                        else: 
                                            output["Subject2"] = subject
                                        adj = ""
        if output["Subject2"] == "": 
            output["Subject2"] = subject

    return output 
